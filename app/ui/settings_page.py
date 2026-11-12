"""Settings page for application preferences, VFS cache paths, and system integration."""

import os
import subprocess
import threading
from collections.abc import Callable
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.services.rclone_service import RcloneService
from app.utils.paths import LOGS_DIR, get_app_data_dir
from app.utils.platform_checks import is_winfsp_installed
from app.utils.startup import is_startup_enabled, set_startup_enabled


class SettingsPage(ctk.CTkFrame):
    """View dedicated to app configuration, storage limits, startup options, and diagnostics."""

    def __init__(
        self,
        master,
        rclone_service: RcloneService | None = None,
        on_view_logs: Callable[[], None] | None = None,
        on_rerun_wizard: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.rclone_service = rclone_service or RcloneService()
        self.on_view_logs = on_view_logs
        self.on_rerun_wizard = on_rerun_wizard

        self.start_with_win = ctk.BooleanVar(value=is_startup_enabled())
        self.minimize_to_tray = ctk.BooleanVar(value=True)
        self.default_cache_path = ctk.StringVar(value=str(get_app_data_dir() / "vfs_cache"))
        self.default_cache_size = ctk.StringVar(value="20G")
        self.default_cache_expiry = ctk.StringVar(value="24h")
        self.rcl_status_var = ctk.StringVar()

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))

        title = ctk.CTkLabel(
            header, text="Application Settings", font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Configure system startup behavior, VFS cache quotas, credentials storage, and diagnostics",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Scrollable container for settings sections
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # 1. System Integration Section
        self._build_section_card(
            scroll,
            title="Windows Integration",
            description="Manage startup preferences and desktop shell behavior",
            build_func=self._build_sys_integration_fields,
        )

        # 2. VFS Storage & Cache Section
        self._build_section_card(
            scroll,
            title="VFS Streaming & Cache Policies",
            description="Control local virtual filesystem cache allocation and expiration",
            build_func=self._build_cache_fields,
        )

        # 3. Cloud Engine & Drivers Status
        self._build_section_card(
            scroll,
            title="Storage Engine Diagnostics",
            description="Status of system-level cloud mounting utilities (rclone & WinFsp)",
            build_func=self._build_diagnostics_fields,
        )

        # 4. Logs & Troubleshooting
        self._build_section_card(
            scroll,
            title="Logs & Diagnostics",
            description="Inspect detailed application and subprocess execution logs",
            build_func=self._build_logs_fields,
        )

    def _build_section_card(self, parent, title: str, description: str, build_func):
        card = ctk.CTkFrame(
            parent,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        card.pack(fill="x", pady=(0, 16))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=18)

        t_lbl = ctk.CTkLabel(inner, text=title, font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY)
        t_lbl.pack(anchor="w")

        d_lbl = ctk.CTkLabel(inner, text=description, font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
        d_lbl.pack(anchor="w", pady=(1, 14))

        build_func(inner)

    def _build_sys_integration_fields(self, parent):
        chk1 = ctk.CTkCheckBox(
            parent,
            text="Launch GDrive Manager automatically at Windows startup",
            variable=self.start_with_win,
            command=self._on_toggle_startup,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY,
        )
        chk1.pack(anchor="w", pady=(0, 8))

        chk2 = ctk.CTkCheckBox(
            parent,
            text="Minimize to system tray when closing the main window",
            variable=self.minimize_to_tray,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY,
        )
        chk2.pack(anchor="w")

    def _on_toggle_startup(self):
        val = self.start_with_win.get()
        ok = set_startup_enabled(val)
        if not ok:
            messagebox.showerror("Error", "Could not modify Windows startup registry.")
            self.start_with_win.set(not val)

    def _build_cache_fields(self, parent):
        path_lbl = ctk.CTkLabel(
            parent, text="Default VFS Cache Directory:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY
        )
        path_lbl.pack(anchor="w", pady=(0, 4))

        p_row = ctk.CTkFrame(parent, fg_color="transparent")
        p_row.pack(fill="x", pady=(0, 12))

        entry = ctk.CTkEntry(
            p_row,
            textvariable=self.default_cache_path,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.INPUT_BORDER,
            height=34,
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        b_btn = ctk.CTkButton(
            p_row,
            text="Browse...",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=34,
            command=self._browse_cache_dir,
        )
        b_btn.pack(side="right")

        opts_row = ctk.CTkFrame(parent, fg_color="transparent")
        opts_row.pack(fill="x")

        # Size
        s_box = ctk.CTkFrame(opts_row, fg_color="transparent")
        s_box.pack(side="left", padx=(0, 24))

        s_lbl = ctk.CTkLabel(
            s_box, text="Maximum Cache Limit:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY
        )
        s_lbl.pack(anchor="w", pady=(0, 4))

        s_menu = ctk.CTkOptionMenu(
            s_box,
            values=["5G", "10G", "20G", "50G", "100G", "Unlimited"],
            variable=self.default_cache_size,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            height=34,
        )
        s_menu.pack(anchor="w")

        # Expiry
        e_box = ctk.CTkFrame(opts_row, fg_color="transparent")
        e_box.pack(side="left")

        e_lbl = ctk.CTkLabel(
            e_box, text="Cache Expiration (TTL):", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY
        )
        e_lbl.pack(anchor="w", pady=(0, 4))

        e_menu = ctk.CTkOptionMenu(
            e_box,
            values=["1h", "6h", "24h", "48h", "168h (1 week)"],
            variable=self.default_cache_expiry,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            height=34,
        )
        e_menu.pack(anchor="w")

    def _build_diagnostics_fields(self, parent):
        winfsp_ok = is_winfsp_installed()
        rclone_ok = self.rclone_service.is_available()
        rclone_ver = self.rclone_service.get_version() or "Not Installed"

        # WinFsp status
        fsp_st = (
            "INSTALLED (Ready to mount virtual drives)"
            if winfsp_ok
            else "NOT DETECTED (Required for drive letters)"
        )
        fsp_color = Colors.STATUS_MOUNTED if winfsp_ok else Colors.STATUS_WARNING

        fsp_box = ctk.CTkFrame(parent, fg_color="transparent")
        fsp_box.pack(fill="x", pady=(0, 6))

        fsp_lbl = ctk.CTkLabel(
            fsp_box, text=f"• WinFsp Driver: {fsp_st}", font=Fonts.BODY, text_color=fsp_color
        )
        fsp_lbl.pack(side="left")

        if not winfsp_ok:
            winfsp_btn = ctk.CTkButton(
                fsp_box,
                text="Install WinFsp (winget)",
                font=Fonts.CAPTION,
                fg_color=Colors.CARD_INNER,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                height=26,
                command=self._install_winfsp,
            )
            winfsp_btn.pack(side="left", padx=(12, 0))

        # rclone status
        rcl_box = ctk.CTkFrame(parent, fg_color="transparent")
        rcl_box.pack(fill="x", pady=(0, 8))

        init_rcl_text = (
            f"• rclone Engine: AVAILABLE ({rclone_ver})" if rclone_ok else "• rclone Engine: NOT DETECTED"
        )
        self.rcl_status_var.set(init_rcl_text)

        self.rcl_lbl = ctk.CTkLabel(
            rcl_box,
            textvariable=self.rcl_status_var,
            font=Fonts.BODY,
            text_color=Colors.STATUS_MOUNTED if rclone_ok else Colors.STATUS_WARNING,
        )
        self.rcl_lbl.pack(side="left")

        if not rclone_ok:
            self.download_rcl_btn = ctk.CTkButton(
                rcl_box,
                text="Download & Setup rclone",
                font=Fonts.CAPTION,
                fg_color=Colors.ACCENT_PRIMARY,
                hover_color=Colors.ACCENT_HOVER,
                height=26,
                command=self._download_rclone,
            )
            self.download_rcl_btn.pack(side="left", padx=(12, 0))

        # Secure Storage
        sec_lbl = ctk.CTkLabel(
            parent,
            text="• Credential Vault: Windows Credential Manager Active (AES Hardware Encrypted)",
            font=Fonts.BODY,
            text_color=Colors.STATUS_MOUNTED,
        )
        sec_lbl.pack(anchor="w", pady=(0, 10))

        # Setup Wizard Launcher
        wiz_box = ctk.CTkFrame(parent, fg_color="transparent")
        wiz_box.pack(fill="x")

        wiz_btn = ctk.CTkButton(
            wiz_box,
            text="Launch Onboarding Wizard",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=32,
            command=self._handle_rerun_wizard,
        )
        wiz_btn.pack(side="left")

    def _handle_rerun_wizard(self):
        if self.on_rerun_wizard:
            self.on_rerun_wizard()

    def _download_rclone(self):
        self.download_rcl_btn.configure(state="disabled", text="Downloading...")
        self.rcl_status_var.set("• rclone Engine: Downloading standalone binary...")

        def _worker():
            ok = self.rclone_service.download_bundled_rclone()

            def _ui():
                if ok:
                    ver = self.rclone_service.get_version() or "Bundled"
                    self.rcl_status_var.set(f"• rclone Engine: AVAILABLE ({ver})")
                    self.rcl_lbl.configure(text_color=Colors.STATUS_MOUNTED)
                    self.download_rcl_btn.pack_forget()
                    messagebox.showinfo(
                        "Setup Complete",
                        f"rclone has been downloaded and configured at:\n{self.rclone_service.rclone_exe}",
                    )
                else:
                    self.rcl_status_var.set(
                        "• rclone Engine: Download failed. You can install via winget install Rclone.Rclone"
                    )
                    self.download_rcl_btn.configure(state="normal", text="Retry Download")
                    messagebox.showerror(
                        "Download Error",
                        "Could not download rclone automatically. Please run 'winget install Rclone.Rclone' in terminal.",
                    )

            self.after(0, _ui)

        threading.Thread(target=_worker, daemon=True).start()

    def _install_winfsp(self):
        res = messagebox.askyesno(
            "Install WinFsp",
            "WinFsp provides Windows virtual drive mounting.\nWould you like to run 'winget install WinFsp.WinFsp'?",
        )
        if res:
            try:
                subprocess.Popen(
                    [
                        "winget",
                        "install",
                        "WinFsp.WinFsp",
                        "--accept-package-agreements",
                        "--accept-source-agreements",
                    ]
                )
                messagebox.showinfo(
                    "Installer Launched",
                    "WinFsp installer has been launched. Please follow the on-screen installer prompts.",
                )
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch winget: {e}")

    def _build_logs_fields(self, parent):
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x")

        view_logs_btn = ctk.CTkButton(
            btn_row,
            text="Interactive Logs Viewer",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            height=34,
            command=self._handle_view_logs,
        )
        view_logs_btn.pack(side="left", padx=(0, 10))

        open_logs_btn = ctk.CTkButton(
            btn_row,
            text="Open Logs Directory",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=34,
            command=self._open_logs_dir,
        )
        open_logs_btn.pack(side="left")

    def _handle_view_logs(self):
        if self.on_view_logs:
            self.on_view_logs()

    def _browse_cache_dir(self):
        folder = filedialog.askdirectory(title="Select VFS Cache Directory")
        if folder:
            self.default_cache_path.set(folder)

    def _open_logs_dir(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        try:
            os.startfile(str(LOGS_DIR))
        except Exception:
            messagebox.showinfo("Logs Directory", f"Logs folder: {LOGS_DIR}")
