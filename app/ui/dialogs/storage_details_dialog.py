"""Storage Details modal dialog displaying cloud, offline, and VFS cache breakdown."""

from collections.abc import Callable
from tkinter import messagebox

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.core.storage_manager import StorageBreakdown, StorageManager
from app.models.account import Account
from app.ui.assets import get_drive_hardware_icon


class StorageDetailsDialog(ctk.CTkToplevel):
    """Modal displaying isolated storage breakdown (Cloud Quota, Offline Files, VFS Cache)."""

    def __init__(
        self,
        master,
        account: Account,
        storage_manager: StorageManager,
        on_cache_purged: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.account = account
        self.storage_manager = storage_manager
        self.on_cache_purged = on_cache_purged

        self.title(f"Storage Breakdown - {account.display_name}")
        self.geometry("540x580")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_MAIN)

        self.transient(master)
        self.grab_set()

        self._build_ui()
        self._load_data()

        # Center on master
        self.update_idletasks()
        try:
            x = master.winfo_x() + (master.winfo_width() // 2) - 270
            y = master.winfo_y() + (master.winfo_height() // 2) - 290
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self):
        container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        container.pack(fill="both", expand=True, padx=16, pady=16)

        self.inner = ctk.CTkFrame(container, fg_color="transparent")
        self.inner.pack(fill="both", expand=True, padx=22, pady=20)

        # Header
        head_row = ctk.CTkFrame(self.inner, fg_color="transparent")
        head_row.pack(fill="x", pady=(0, 16))

        ico = ctk.CTkLabel(head_row, text="", image=get_drive_hardware_icon(32, "#8B5CF6"))
        ico.pack(side="left", padx=(0, 12))

        t_box = ctk.CTkFrame(head_row, fg_color="transparent")
        t_box.pack(side="left")

        t_lbl = ctk.CTkLabel(
            t_box, text=f"{self.account.display_name}", font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY
        )
        t_lbl.pack(anchor="w")

        m_lbl = ctk.CTkLabel(
            t_box,
            text=f"Operating Mode: {self.account.operating_mode}",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED,
        )
        m_lbl.pack(anchor="w")

        # 1. Cloud Storage Section Card
        self.cloud_card = ctk.CTkFrame(
            self.inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS
        )
        self.cloud_card.pack(fill="x", pady=(0, 14))

        cc_inner = ctk.CTkFrame(self.cloud_card, fg_color="transparent")
        cc_inner.pack(fill="x", padx=16, pady=14)

        c_top = ctk.CTkFrame(cc_inner, fg_color="transparent")
        c_top.pack(fill="x", pady=(0, 6))

        c_title = ctk.CTkLabel(
            c_top, text="☁️ Cloud Storage (Google Drive)", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY
        )
        c_title.pack(side="left")

        self.cloud_quota_lbl = ctk.CTkLabel(
            c_top, text="Loading...", font=Fonts.CAPTION, text_color=Colors.TEXT_SECONDARY
        )
        self.cloud_quota_lbl.pack(side="right")

        self.cloud_prog = ctk.CTkProgressBar(
            cc_inner,
            height=8,
            corner_radius=4,
            fg_color=Colors.PROGRESS_BG,
            progress_color=Colors.ACCENT_PRIMARY,
        )
        self.cloud_prog.set(0)
        self.cloud_prog.pack(fill="x", pady=(4, 6))

        self.cloud_detail_lbl = ctk.CTkLabel(
            cc_inner, text="Querying Google Drive API...", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED
        )
        self.cloud_detail_lbl.pack(anchor="w")

        # 2. Local Offline Directory Card
        self.offline_card = ctk.CTkFrame(
            self.inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS
        )
        self.offline_card.pack(fill="x", pady=(0, 14))

        oc_inner = ctk.CTkFrame(self.offline_card, fg_color="transparent")
        oc_inner.pack(fill="x", padx=16, pady=14)

        o_title = ctk.CTkLabel(
            oc_inner,
            text="📁 Local Offline Storage (Backup / Mirror)",
            font=Fonts.BODY_BOLD,
            text_color=Colors.TEXT_PRIMARY,
        )
        o_title.pack(anchor="w", pady=(0, 4))

        self.offline_detail_lbl = ctk.CTkLabel(
            oc_inner,
            text=f"Path: {self.account.offline_path or 'Not configured'}\nCalculating disk usage...",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_SECONDARY,
            justify="left",
        )
        self.offline_detail_lbl.pack(anchor="w")

        # 3. Local VFS Streaming Cache Card
        self.cache_card = ctk.CTkFrame(
            self.inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS
        )
        self.cache_card.pack(fill="x", pady=(0, 18))

        kc_inner = ctk.CTkFrame(self.cache_card, fg_color="transparent")
        kc_inner.pack(fill="x", padx=16, pady=14)

        k_top = ctk.CTkFrame(kc_inner, fg_color="transparent")
        k_top.pack(fill="x", pady=(0, 4))

        k_title = ctk.CTkLabel(
            k_top,
            text="⚡ VFS Streaming Cache (Temporary)",
            font=Fonts.BODY_BOLD,
            text_color=Colors.TEXT_PRIMARY,
        )
        k_title.pack(side="left")

        purge_btn = ctk.CTkButton(
            k_top,
            text="Purge Cache",
            font=Fonts.CAPTION,
            fg_color=Colors.STATUS_WARNING,
            hover_color="#D97706",
            height=26,
            width=90,
            command=self._handle_purge_cache,
        )
        purge_btn.pack(side="right")

        self.cache_detail_lbl = ctk.CTkLabel(
            kc_inner,
            text=f"Quota Limit: {self.account.cache_size} (TTL: {self.account.cache_expiry})\nCalculating cache size...",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_SECONDARY,
            justify="left",
        )
        self.cache_detail_lbl.pack(anchor="w")

        # Close button
        close_btn = ctk.CTkButton(
            self.inner,
            text="Close",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=36,
            width=100,
            command=self.destroy,
        )
        close_btn.pack(side="right")

    def _load_data(self):
        """Asynchronously load metrics from storage manager."""

        def _on_done(b: StorageBreakdown):
            self.after(0, lambda: self._apply_data(b))

        self.storage_manager.calculate_async(self.account, _on_done)

    def _apply_data(self, b: StorageBreakdown):
        # Cloud
        self.cloud_quota_lbl.configure(text=f"{b.formatted_cloud_used} / {b.formatted_cloud_total}")
        self.cloud_prog.set(b.cloud_percentage / 100.0)

        remaining_bytes = max(0, b.cloud_total_bytes - b.cloud_used_bytes)
        formatted_free = StorageBreakdown.format_bytes(remaining_bytes)
        exact_text = "Exact quota from Google Drive API" if b.is_quota_exact else "Cached account metadata"
        self.cloud_detail_lbl.configure(
            text=f"Free: {formatted_free} ({100.0 - b.cloud_percentage:.1f}% available)  •  {exact_text}"
        )

        # Offline
        if self.account.offline_enabled:
            self.offline_detail_lbl.configure(
                text=f"Directory: {self.account.offline_path}\nUsed on Disk: {b.formatted_offline_used} ({b.offline_file_count} files stored)"
            )
        else:
            self.offline_detail_lbl.configure(
                text="Offline storage mode is currently disabled for this account."
            )

        # Cache
        self.cache_detail_lbl.configure(
            text=f"Limit: {b.vfs_cache_limit} (TTL: {self.account.cache_expiry})\nUsed on Disk: {b.formatted_cache_used} (Temporary streaming chunks)"
        )

    def _handle_purge_cache(self):
        res = messagebox.askyesno(
            "Purge VFS Streaming Cache",
            f"Are you sure you want to purge the local VFS streaming cache for '{self.account.display_name}'?\n\n"
            "This will free up local disk space without deleting any files from Google Drive or your offline folder.",
        )
        if res:
            ok = self.storage_manager.purge_vfs_cache(self.account.id)
            if ok:
                messagebox.showinfo("Purge Complete", "VFS streaming cache has been purged.")
                self._load_data()
                if self.on_cache_purged:
                    self.on_cache_purged()
            else:
                messagebox.showerror(
                    "Error",
                    "Could not purge VFS cache. The drive might currently be actively streaming files.",
                )
