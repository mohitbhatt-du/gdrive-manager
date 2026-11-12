"""Streaming Mode management view for mounting Google Drive as Windows drives."""

from typing import List, Callable, Optional
import customtkinter as ctk
from app.models.account import Account
from app.config.theme import Colors, Fonts, Dimensions
from app.ui.assets import get_symbol_icon, get_drive_hardware_icon
from app.utils.platform_checks import is_winfsp_installed, is_rclone_installed

class StreamingPage(ctk.CTkFrame):
    """View dedicated to managing Windows drive mounts, VFS caching, and WinFsp status."""

    def __init__(
        self,
        master,
        accounts: List[Account],
        on_toggle_mount: Optional[Callable[[Account], None]] = None,
        on_open_drive: Optional[Callable[[Account], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.accounts = accounts
        self.on_toggle_mount = on_toggle_mount
        self.on_open_drive = on_open_drive

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))

        title = ctk.CTkLabel(
            header,
            text="Streaming Drives (WinFsp)",
            font=Fonts.HERO,
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Mount your Google Drives directly as Windows drive letters with smart on-demand VFS caching",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # WinFsp / rclone environment banner
        self._build_driver_status_banner()

        # Mount Table Container
        table_card = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        table_card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        # Table Header
        tbl_header = ctk.CTkFrame(table_card, fg_color=Colors.CARD_INNER, height=40, corner_radius=Dimensions.CARD_CORNER_RADIUS)
        tbl_header.pack(fill="x", padx=10, pady=(10, 6))

        cols = [
            ("Drive", 0.12),
            ("Account / Remote", 0.35),
            ("VFS Cache", 0.18),
            ("Status", 0.15),
            ("Actions", 0.20),
        ]

        for name, weight in cols:
            lbl = ctk.CTkLabel(
                tbl_header,
                text=name.upper(),
                font=Fonts.BADGE,
                text_color=Colors.TEXT_MUTED
            )
            lbl.pack(side="left", padx=12, expand=True, fill="x")

        # Scrollable rows
        self.row_scroll = ctk.CTkScrollableFrame(table_card, fg_color="transparent")
        self.row_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.render_rows()

    def _build_driver_status_banner(self):
        winfsp_ok = is_winfsp_installed()
        rclone_ok = is_rclone_installed()

        banner = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        banner.pack(fill="x", padx=28, pady=(0, 16))

        b_box = ctk.CTkFrame(banner, fg_color="transparent")
        b_box.pack(fill="x", padx=16, pady=12)

        # WinFsp status
        fsp_color = Colors.STATUS_MOUNTED if winfsp_ok else Colors.STATUS_WARNING
        fsp_text = "Installed & Active" if winfsp_ok else "Not Detected (Required for Windows drive letters)"
        
        fsp_row = ctk.CTkFrame(b_box, fg_color="transparent")
        fsp_row.pack(side="left", padx=(0, 28))

        fsp_icon = ctk.CTkLabel(fsp_row, text="●", text_color=fsp_color, font=Fonts.CARD_TITLE)
        fsp_icon.pack(side="left", padx=(0, 8))

        fsp_lbl = ctk.CTkLabel(
            fsp_row,
            text=f"WinFsp Driver: {fsp_text}",
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY
        )
        fsp_lbl.pack(side="left")

        # Rclone status
        rcl_color = Colors.STATUS_MOUNTED if rclone_ok else Colors.STATUS_WARNING
        rcl_text = "Available" if rclone_ok else "Not in PATH (Will be downloaded or configured in Phase 2)"
        
        rcl_row = ctk.CTkFrame(b_box, fg_color="transparent")
        rcl_row.pack(side="left")

        rcl_icon = ctk.CTkLabel(rcl_row, text="●", text_color=rcl_color, font=Fonts.CARD_TITLE)
        rcl_icon.pack(side="left", padx=(0, 8))

        rcl_lbl = ctk.CTkLabel(
            rcl_row,
            text=f"rclone Engine: {rcl_text}",
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY
        )
        rcl_lbl.pack(side="left")

    def render_rows(self):
        for w in self.row_scroll.winfo_children():
            w.destroy()

        streaming_accounts = [a for a in self.accounts if a.streaming_enabled]
        if not streaming_accounts:
            lbl = ctk.CTkLabel(
                self.row_scroll,
                text="No drives currently configured for streaming mode.",
                font=Fonts.SUBTITLE,
                text_color=Colors.TEXT_MUTED
            )
            lbl.pack(pady=40)
            return

        for acc in streaming_accounts:
            row = ctk.CTkFrame(
                self.row_scroll,
                fg_color=Colors.CARD_INNER,
                corner_radius=Dimensions.CARD_CORNER_RADIUS,
                height=50
            )
            row.pack(fill="x", pady=4)

            # Drive Letter
            letter_lbl = ctk.CTkLabel(
                row,
                text=f"  {acc.drive_letter}  ",
                font=Fonts.BADGE,
                text_color=Colors.TEXT_PRIMARY,
                fg_color=Colors.ACCENT_PRIMARY if acc.is_mounted else Colors.BG_SIDEBAR,
                corner_radius=6,
                height=26
            )
            letter_lbl.pack(side="left", padx=(14, 16))

            # Display Name & Remote
            name_box = ctk.CTkFrame(row, fg_color="transparent")
            name_box.pack(side="left", fill="x", expand=True)

            dname = ctk.CTkLabel(name_box, text=acc.display_name, font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
            dname.pack(anchor="w")

            rname = ctk.CTkLabel(name_box, text=f"Remote: {acc.remote_name} ({acc.email})", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
            rname.pack(anchor="w")

            # Cache Limit
            cache_lbl = ctk.CTkLabel(
                row,
                text=f"{acc.cache_size} (TTL: {acc.cache_expiry})",
                font=Fonts.CAPTION,
                text_color=Colors.TEXT_SECONDARY
            )
            cache_lbl.pack(side="left", padx=16)

            # Status Pill
            st_color = Colors.STATUS_MOUNTED if acc.is_mounted else Colors.STATUS_MUTED
            st_text = "MOUNTED" if acc.is_mounted else "UNMOUNTED"
            st_pill = ctk.CTkLabel(
                row,
                text=f" ● {st_text} ",
                font=Fonts.CAPTION,
                text_color=st_color,
                fg_color=Colors.INPUT_BG,
                corner_radius=6,
                height=24
            )
            st_pill.pack(side="left", padx=16)

            # Actions
            act_box = ctk.CTkFrame(row, fg_color="transparent")
            act_box.pack(side="right", padx=14)

            mount_txt = "Unmount" if acc.is_mounted else "Mount"
            m_btn = ctk.CTkButton(
                act_box,
                text=mount_txt,
                font=Fonts.BUTTON,
                fg_color=Colors.CARD_HOVER if acc.is_mounted else Colors.ACCENT_PRIMARY,
                hover_color=Colors.ACCENT_HOVER,
                corner_radius=6,
                width=80,
                height=30,
                command=lambda a=acc: self._handle_toggle(a)
            )
            m_btn.pack(side="left", padx=(0, 6))

            if acc.is_mounted:
                open_btn = ctk.CTkButton(
                    act_box,
                    text="Open",
                    font=Fonts.BUTTON,
                    fg_color=Colors.CARD_BG,
                    hover_color=Colors.CARD_HOVER,
                    border_width=1,
                    border_color=Colors.CARD_BORDER,
                    corner_radius=6,
                    width=60,
                    height=30,
                    command=lambda a=acc: self._handle_open(a)
                )
                open_btn.pack(side="left")

    def _handle_toggle(self, acc: Account):
        if self.on_toggle_mount:
            self.on_toggle_mount(acc)

    def _handle_open(self, acc: Account):
        if self.on_open_drive:
            self.on_open_drive(acc)

    def update_accounts(self, accounts: List[Account]):
        self.accounts = accounts
        self.render_rows()
