"""Main application window for GDrive Manager."""

from tkinter import messagebox

import customtkinter as ctk

from app.__version__ import __version__
from app.config.account_repository import AccountRepository
from app.config.theme import Colors, Dimensions, Fonts
from app.core.account_manager import AccountManager
from app.core.auth_manager import AuthManager
from app.core.mount_manager import MountManager
from app.core.storage_manager import StorageManager
from app.core.sync_manager import SyncManager
from app.core.transfer_manager import TransferManager
from app.models.account import Account
from app.models.transfer_job import TransferJob
from app.services.credential_service import CredentialService
from app.services.rclone_service import RcloneService
from app.services.windows_drive_service import WindowsDriveService
from app.ui.assets import get_gdrive_icon
from app.ui.dashboard import Dashboard
from app.ui.dialogs.add_account_dialog import AddAccountDialog
from app.ui.dialogs.cloud_browser_dialog import CloudBrowserDialog
from app.ui.dialogs.confirmation_dialog import ConfirmationDialog
from app.ui.dialogs.drive_settings_dialog import DriveSettingsDialog
from app.ui.dialogs.setup_wizard_dialog import SetupWizardDialog
from app.ui.dialogs.storage_details_dialog import StorageDetailsDialog
from app.ui.logs_page import LogsPage
from app.ui.offline_page import OfflinePage
from app.ui.settings_page import SettingsPage
from app.ui.sidebar import Sidebar
from app.ui.streaming_page import StreamingPage
from app.ui.transfers_page import TransfersPage
from app.ui.tray import SystemTrayManager
from app.utils.logger import get_logger
from app.utils.notifications import send_notification
from app.utils.onboarding import is_onboarding_completed
from app.utils.paths import BASE_DIR

logger = get_logger("MainWindow")


class MainWindow(ctk.CTk):
    """Main desktop application window coordinating navigation, pages, and dialogs."""

    def __init__(self, enable_tray: bool = True):
        super().__init__()

        self.title("GDrive Manager")
        self.geometry(f"{Dimensions.WINDOW_MIN_WIDTH}x{Dimensions.WINDOW_MIN_HEIGHT}")
        self.minsize(Dimensions.WINDOW_MIN_WIDTH, Dimensions.WINDOW_MIN_HEIGHT)
        self.configure(fg_color=Colors.BG_MAIN)
        self.enable_tray = enable_tray
        self._notified_jobs: set[str] = set()

        # Set Windows AppUserModelID & Window/Taskbar Icon
        try:
            import ctypes

            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("GDriveManager.App")
        except Exception:
            pass

        ico_file = BASE_DIR / "assets" / "branding" / "icon.ico"
        if not ico_file.exists():
            ico_file = BASE_DIR / "assets" / "icons" / "app_icon.ico"
        if ico_file.exists():
            try:
                self.iconbitmap(str(ico_file))
            except Exception as e:
                logger.debug(f"Could not set window icon: {e}")

        # Services & Core Managers
        self.rclone_service = RcloneService()
        self.credential_service = CredentialService()
        self.account_repo = AccountRepository()
        self.account_manager = AccountManager(
            repository=self.account_repo,
            rclone_service=self.rclone_service,
            credential_service=self.credential_service,
        )
        self.auth_manager = AuthManager(
            rclone_service=self.rclone_service,
            account_repo=self.account_repo,
            credential_service=self.credential_service,
        )
        self.mount_manager = MountManager(rclone_service=self.rclone_service)
        self.mount_manager.register_callback(self._on_mount_status_updated)

        self.transfer_manager = TransferManager()
        self.sync_manager = SyncManager(
            rclone_service=self.rclone_service, transfer_manager=self.transfer_manager
        )
        self.transfer_manager.register_callback(self._on_transfer_job_updated)

        self.storage_manager = StorageManager(rclone_service=self.rclone_service)

        # Intercept window close to gracefully unmount all virtual drives
        self.protocol("WM_DELETE_WINDOW", self._on_close_window)

        # State
        self.accounts: list[Account] = self.account_manager.get_accounts()
        self.transfer_jobs: list[TransferJob] = self.transfer_manager.get_jobs()
        self.pages: dict[str, ctk.CTkFrame] = {}
        self.current_page_id: str = "drives"

        self._init_layout()
        self._init_pages()
        self.show_page("drives")

        # Initial sidebar account count
        self.sidebar.update_account_count(len(self.accounts))

        # System Tray Integration
        self.tray_manager: SystemTrayManager | None = None
        if self.enable_tray:
            try:
                self.tray_manager = SystemTrayManager(
                    on_show_window=self._show_from_tray,
                    on_mount_all=self._mount_all_drives,
                    on_unmount_all=self._unmount_all_drives,
                    on_quit=self._force_exit,
                )
                self.tray_manager.start()
            except Exception as e:
                logger.error(f"Failed to start system tray manager: {e}")
                self.tray_manager = None

        logger.info("GDrive Manager UI initialized successfully.")

        # First-launch onboarding check
        if self.enable_tray and not is_onboarding_completed():
            self.after(500, self.open_setup_wizard)

        # Asynchronously refresh storage quotas from Google Drive for real accounts
        self.account_manager.refresh_storage_quotas(self._on_quotas_refreshed)

    def _init_layout(self):
        # Configure grid: Column 0 is sidebar (fixed), Column 1 is main content area (expands)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # 1. Left Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_page,
            on_add_drive_click=self.open_add_account_dialog,
            version=f"v{__version__}",
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Main Content Canvas
        self.content_container = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        self.content_container.grid(row=0, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

    def _init_pages(self):
        # Dashboard
        self.dashboard = Dashboard(
            self.content_container,
            accounts=self.accounts,
            on_add_drive=self.open_add_account_dialog,
            on_open_drive=self.handle_open_drive,
            on_toggle_mount=self.handle_toggle_mount,
            on_settings=self.open_drive_settings_dialog,
            on_browse_drive=self.open_cloud_browser,
            on_refresh_storage=self.refresh_storage_quotas,
        )
        self.pages["drives"] = self.dashboard

        # Streaming Page
        self.streaming_page = StreamingPage(
            self.content_container,
            accounts=self.accounts,
            on_toggle_mount=self.handle_toggle_mount,
            on_open_drive=self.handle_open_drive,
            on_browse_drive=self.open_cloud_browser,
        )
        self.pages["streaming"] = self.streaming_page

        # Offline Page
        self.offline_page = OfflinePage(
            self.content_container, accounts=self.accounts, on_start_sync=self.handle_start_sync
        )
        self.pages["offline"] = self.offline_page

        # Transfers Page
        self.transfers_page = TransfersPage(
            self.content_container,
            jobs=self.transfer_manager.get_jobs(),
            on_pause_job=self.transfer_manager.pause_job,
            on_resume_job=self.transfer_manager.resume_job,
            on_cancel_job=self.transfer_manager.cancel_job,
            on_retry_job=self.transfer_manager.retry_job,
        )
        self.pages["transfers"] = self.transfers_page

        # Settings Page
        self.settings_page = SettingsPage(
            self.content_container,
            rclone_service=self.rclone_service,
            on_view_logs=lambda: self.show_page("logs"),
            on_rerun_wizard=self.open_setup_wizard,
        )
        self.pages["settings"] = self.settings_page

        # Logs & Diagnostics Page
        self.logs_page = LogsPage(self.content_container)
        self.pages["logs"] = self.logs_page

        # About Page
        self.about_page = self._build_about_page()
        self.pages["about"] = self.about_page

    def show_page(self, page_id: str):
        """Switch visible page frame in content container."""
        if page_id not in self.pages:
            return

        for p in self.pages.values():
            p.grid_forget()

        self.pages[page_id].grid(row=0, column=0, sticky="nsew")
        self.current_page_id = page_id
        self.sidebar.set_active(page_id)

    def _build_about_page(self) -> ctk.CTkFrame:
        """Create About page panel."""
        about_frame = ctk.CTkFrame(self.content_container, fg_color="transparent")

        center_card = ctk.CTkFrame(
            about_frame,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        center_card.pack(fill="both", expand=True, padx=40, pady=40)

        inner = ctk.CTkFrame(center_card, fg_color="transparent")
        inner.pack(padx=30, pady=30, fill="both", expand=True)

        logo = ctk.CTkLabel(inner, text="", image=get_gdrive_icon(54))
        logo.pack(pady=(20, 10))

        title = ctk.CTkLabel(inner, text="GDrive Manager", font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY)
        title.pack()

        ver = ctk.CTkLabel(
            inner,
            text=f"Version {__version__} (Production Architecture)",
            font=Fonts.CAPTION,
            text_color=Colors.ACCENT_LIGHT,
        )
        ver.pack(pady=(2, 16))

        desc_text = (
            "GDrive Manager is a modern Windows desktop application that bridges multiple Google Drive "
            "accounts seamlessly into Windows File Explorer through high-performance virtual drive mounting "
            "(WinFsp & rclone) and robust selective offline synchronization."
        )
        desc = ctk.CTkLabel(
            inner,
            text=desc_text,
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            wraplength=520,
            justify="center",
        )
        desc.pack(pady=(0, 20))

        features_box = ctk.CTkFrame(
            inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS
        )
        features_box.pack(fill="x", padx=40, pady=(0, 20))

        feats = [
            "✦ Multi-Account Isolation: Personal, Work, Academic, and Media accounts",
            "✦ Streaming Mode: Mount as native Windows drive letters (G:, H:, etc.) with VFS cache",
            "✦ Offline Sync: One-way copies, cloud mirrors, and two-way bi-sync with dry-run verification",
            "✦ Enterprise Security: Windows Credential Manager integration for OAuth tokens",
        ]
        for f in feats:
            f_lbl = ctk.CTkLabel(features_box, text=f, font=Fonts.BODY, text_color=Colors.TEXT_PRIMARY)
            f_lbl.pack(anchor="w", padx=16, pady=4)

        return about_frame

    # --- Actions & Handlers ---

    def open_setup_wizard(self):
        """Open First-Launch Onboarding and Setup Wizard."""
        SetupWizardDialog(self, on_connect_drive=self.open_add_account_dialog)

    def open_add_account_dialog(self):
        """Open Add Google Drive Account modal."""
        AddAccountDialog(self, auth_manager=self.auth_manager, on_account_created=self._on_account_added)

    def _on_account_added(self, account: Account):
        logger.info(f"Account added: {account.display_name} ({account.drive_letter})")
        self.account_manager.add_account(account)
        self.accounts = self.account_manager.get_accounts()
        self.dashboard.update_accounts(self.accounts)
        self.streaming_page.update_accounts(self.accounts)
        self.sidebar.update_account_count(len(self.accounts))
        # Asynchronously fetch quota in background and update metrics
        self.account_manager.refresh_storage_quotas(self._on_quotas_refreshed)
        messagebox.showinfo(
            "Account Connected",
            f"Account '{account.display_name}' has been configured for drive {account.drive_letter}.\n"
            "Ready for mounting or offline synchronization.",
        )

    def _on_quotas_refreshed(self):
        """Dispatched when background quota refresh finishes."""

        def _ui():
            self.accounts = self.account_manager.get_accounts()
            self.dashboard.update_accounts(self.accounts)
            self.streaming_page.update_accounts(self.accounts)
            self.sidebar.update_status("Cloud storage quotas updated.")

        self.after(0, _ui)

    def refresh_storage_quotas(self):
        """User-triggered cloud storage quota refresh."""
        self.sidebar.update_status("Refreshing storage quotas from Google Drive...")
        self.account_manager.refresh_storage_quotas(self._on_quotas_refreshed)

    def open_cloud_browser(self, account: Account | None = None):
        """Open in-app Cloud File & Directory Browser (no drive mount required)."""
        target = account or (self.accounts[0] if self.accounts else None)
        if not target:
            messagebox.showinfo(
                "No Accounts",
                "Please connect a Google Drive account first to browse cloud files.",
            )
            return
        CloudBrowserDialog(
            self,
            account=target,
            rclone_service=self.rclone_service,
            all_accounts=self.accounts,
            on_refresh=self.refresh_storage_quotas,
        )

    def open_drive_settings_dialog(self, account: Account):
        """Open Drive Settings modal."""
        DriveSettingsDialog(
            self,
            account=account,
            storage_manager=self.storage_manager,
            on_account_updated=self._on_account_updated,
            on_account_deleted=self._on_account_deleted,
            on_view_storage=self.open_storage_details_dialog,
        )

    def open_storage_details_dialog(self, account: Account):
        """Open Storage Details modal."""
        StorageDetailsDialog(
            self, account=account, storage_manager=self.storage_manager, on_cache_purged=self._on_cache_purged
        )

    def _on_cache_purged(self):
        self.sidebar.update_status("VFS streaming cache purged.")

    def _on_account_updated(self, account: Account):
        logger.info(f"Account updated: {account.display_name}")
        self.account_manager.update_account(account)
        self.accounts = self.account_manager.get_accounts()
        self.dashboard.update_accounts(self.accounts)
        self.streaming_page.update_accounts(self.accounts)

    def _on_account_deleted(self, account: Account):
        logger.info(f"Account removed: {account.display_name}")
        self.account_manager.remove_account(account.id)
        self.accounts = self.account_manager.get_accounts()
        self.dashboard.update_accounts(self.accounts)
        self.streaming_page.update_accounts(self.accounts)
        self.sidebar.update_account_count(len(self.accounts))

    def handle_toggle_mount(self, account: Account):
        """Toggle mount state of a Google Drive account using MountManager."""
        if account.is_sample:
            # Toggle sample preview status
            account.is_mounted = not account.is_mounted
            account.status = "Mounted" if account.is_mounted else "Connected"
            logger.info(f"Sample drive {account.drive_letter} toggled to {account.status}")
            self.dashboard.update_accounts(self.accounts)
            self.streaming_page.update_accounts(self.accounts)
            return

        # Real account mount/unmount via rclone & WinFsp
        if account.is_mounted:
            ok, msg = self.mount_manager.unmount_drive(account)
            if ok:
                self.sidebar.update_status(f"Unmounted drive {account.drive_letter}")
                send_notification(
                    "Drive Unmounted",
                    f"Unmounted Google Drive ({account.display_name}) from {account.drive_letter}\\",
                )
            else:
                messagebox.showwarning("Unmount Warning", msg)
        else:
            self.sidebar.update_status(f"Mounting {account.drive_letter}...")
            ok, msg = self.mount_manager.mount_drive(account)
            if ok:
                self.sidebar.update_status(f"Mounted {account.drive_letter}")
                send_notification(
                    "Drive Mounted",
                    f"Mounted Google Drive ({account.display_name}) at {account.drive_letter}\\",
                )
            else:
                messagebox.showerror("Mount Failed", msg)

        self.dashboard.update_accounts(self.accounts)
        self.streaming_page.update_accounts(self.accounts)

    def handle_open_drive(self, account: Account):
        """Open Windows drive letter in Explorer."""
        if account.is_sample:
            messagebox.showinfo(
                "Sample Drive Preview",
                f"Virtual path {account.drive_letter}\\ is a sample preview card.\n\n"
                "Connect a live Google account to mount and open real streamed cloud files directly in Windows Explorer.",
            )
            return

        if not account.is_mounted:
            messagebox.showinfo(
                "Drive Unmounted",
                f"Drive {account.drive_letter} is currently unmounted. Please mount it first.",
            )
            return

        opened = WindowsDriveService.open_in_explorer(account.drive_letter)
        if not opened:
            messagebox.showwarning(
                "Explorer", f"Could not open {account.drive_letter}\\ in Windows File Explorer."
            )

    def _on_mount_status_updated(self, account_id: str, new_status: str):
        """Callback invoked when background MountManager status changes."""

        def _refresh():
            for acc in self.accounts:
                if acc.id == account_id:
                    acc.status = new_status
                    acc.is_mounted = new_status == "Mounted"
                    break
            self.dashboard.update_accounts(self.accounts)
            self.streaming_page.update_accounts(self.accounts)

        self.after(0, _refresh)

    def _on_close_window(self):
        """Handle window close event: minimize to tray if enabled, or safely exit."""
        if self.enable_tray and self.settings_page.minimize_to_tray.get():
            self.withdraw()
            send_notification("GDrive Manager", "GDrive Manager is running in the background.")
            return
        self._force_exit()

    def _force_exit(self):
        """Safely unmount all virtual drives and terminate background tray before destruction."""
        logger.info("Application close requested. Safely unmounting active drives...")
        try:
            self.mount_manager.unmount_all()
        except Exception as e:
            logger.error(f"Error during shutdown unmount: {e}")

        if self.tray_manager:
            try:
                self.tray_manager.stop()
            except Exception as e:
                logger.error(f"Error stopping tray manager: {e}")

        self.destroy()

    def _show_from_tray(self):
        def _deiconify():
            self.deiconify()
            self.lift()
            self.focus_force()

        self.after(0, _deiconify)

    def _mount_all_drives(self):
        def _mount():
            for acc in self.accounts:
                if not acc.is_sample and not acc.is_mounted:
                    self.mount_manager.mount_drive(acc)
            self.sidebar.update_status("Mounted all configured drives.")
            self.dashboard.update_accounts(self.accounts)
            self.streaming_page.update_accounts(self.accounts)

        self.after(0, _mount)

    def _unmount_all_drives(self):
        def _unmount():
            self.mount_manager.unmount_all()
            self.sidebar.update_status("Unmounted all drives.")
            self.dashboard.update_accounts(self.accounts)
            self.streaming_page.update_accounts(self.accounts)

        self.after(0, _unmount)

    def handle_start_sync(self, account: Account, local_path: str, sync_type: str, dry_run: bool):
        """Trigger synchronization task from Offline Page."""
        if not local_path.strip():
            messagebox.showwarning("Missing Path", "Please select a valid local destination directory.")
            return

        if account.is_sample:
            op_name = sync_type.split("(")[0].strip()
            demo_job = TransferJob(
                id=f"demo-{len(self.transfer_manager.jobs) + 1}",
                account_name=account.display_name,
                item_name=f"{account.display_name} Offline Sync (Demo)",
                operation_type=op_name,
                total_bytes=120 * 1024 * 1024,
                transferred_bytes=60 * 1024 * 1024,
                speed_bytes_per_sec=8 * 1024 * 1024,
                eta_seconds=7,
                status="Running",
                is_sample=True,
            )
            self.transfer_manager.jobs.insert(0, demo_job)
            self.transfers_page.update_jobs(self.transfer_manager.get_jobs())
            self.show_page("transfers")
            self.sidebar.update_status(f"Demo '{op_name}' started")
            return

        # Destructive Mirror safety warning
        if "Mirror/Sync" in sync_type and not dry_run:

            def _proceed_mirror():
                self._dispatch_sync(account, local_path, sync_type, dry_run=False)

            ConfirmationDialog(
                self,
                title="⚠️ Destructive Mirror Warning",
                message=(
                    "Mirror Synchronization will permanently DELETE files in the destination "
                    "that do not exist at the source!\n\n"
                    "Are you sure you want to proceed without a Dry-Run preview first?"
                ),
                confirm_text="Proceed & Sync",
                cancel_text="Cancel",
                is_destructive=True,
                on_confirm=_proceed_mirror,
            )
            return

        self._dispatch_sync(account, local_path, sync_type, dry_run)

    def _dispatch_sync(self, account: Account, local_path: str, sync_type: str, dry_run: bool):
        ok, msg, job = self.sync_manager.start_sync(account, local_path, sync_type, dry_run)
        if ok:
            self.sidebar.update_status(f"Sync started: {account.display_name}")
            self.transfers_page.update_jobs(self.transfer_manager.get_jobs())
            self.show_page("transfers")
        else:
            messagebox.showerror("Sync Error", msg)

    def _on_transfer_job_updated(self, job: TransferJob):
        """Update Transfers UI on background telemetry callback with desktop notifications."""
        if job.id not in self._notified_jobs:
            if job.status == "Completed":
                self._notified_jobs.add(job.id)
                send_notification("Transfer Completed", f"{job.item_name} finished successfully.")
            elif job.status == "Failed":
                self._notified_jobs.add(job.id)
                send_notification(
                    "Transfer Failed", f"{job.item_name} failed: {job.error_message or 'Unknown error'}"
                )

        self.after(0, lambda: self.transfers_page.update_jobs(self.transfer_manager.get_jobs()))
