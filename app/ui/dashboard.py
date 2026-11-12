"""Main dashboard view displaying account cards, statistics, and quick actions."""

from collections.abc import Callable

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.models.account import Account
from app.ui.assets import get_drive_hardware_icon, get_symbol_icon
from app.ui.drive_card import DriveCard


class Dashboard(ctk.CTkFrame):
    """Dashboard view showcasing connected drives, metrics, and management actions."""

    def __init__(
        self,
        master,
        accounts: list[Account],
        on_add_drive: Callable[[], None],
        on_open_drive: Callable[[Account], None] | None = None,
        on_toggle_mount: Callable[[Account], None] | None = None,
        on_settings: Callable[[Account], None] | None = None,
        on_browse_drive: Callable[[Account], None] | None = None,
        on_refresh_storage: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.accounts = accounts
        self.on_add_drive = on_add_drive
        self.on_open_drive = on_open_drive
        self.on_toggle_mount = on_toggle_mount
        self.on_settings = on_settings
        self.on_browse_drive = on_browse_drive
        self.on_refresh_storage = on_refresh_storage

        self.cards: list[DriveCard] = []

        self.total_accounts_lbl: ctk.CTkLabel | None = None
        self.streaming_drives_lbl: ctk.CTkLabel | None = None
        self.cloud_usage_lbl: ctk.CTkLabel | None = None

        self._build_ui()

    def _build_ui(self):
        # 1. Top Header Section
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=28, pady=(24, 16))

        # Title and Subtitle
        text_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        text_box.pack(side="left")

        title_lbl = ctk.CTkLabel(text_box, text="My Drives", font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY)
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            text_box,
            text="Your Google Drive(s) mounted as Windows drives with streaming and offline sync",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Right Header: "+ Add GDrive" Primary Button & Refresh Button
        add_btn = ctk.CTkButton(
            header_frame,
            text="+ Add GDrive",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=38,
            command=self.on_add_drive,
        )
        add_btn.pack(side="right")

        if self.on_refresh_storage:
            refresh_btn = ctk.CTkButton(
                header_frame,
                text="Refresh Storage",
                image=get_symbol_icon("refresh", 14, Colors.TEXT_PRIMARY),
                compound="left",
                font=Fonts.BUTTON,
                fg_color=Colors.CARD_BG,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
                height=38,
                command=self.on_refresh_storage,
            )
            refresh_btn.pack(side="right", padx=(0, 10))

        # 2. Key Metrics Bar (Total Drives, Active Mounts, Cloud Storage)
        self._build_stats_bar()

        # 3. Scrollable Drive Cards Container
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=Colors.CARD_BORDER,
            scrollbar_button_hover_color=Colors.ACCENT_PRIMARY,
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.scroll_frame.grid_columnconfigure((0, 1), weight=1, uniform="card_col")

        self.render_cards()

    def _build_stats_bar(self):
        """Build summary metric pills with dynamic labels."""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=28, pady=(0, 16))

        total_drives = len(self.accounts)
        mounted_count = sum(1 for a in self.accounts if a.is_mounted)
        total_used_bytes = sum(a.used_storage_bytes for a in self.accounts)
        total_alloc_bytes = sum(a.total_storage_bytes for a in self.accounts)

        formatted_used = Account.format_bytes(total_used_bytes)
        formatted_alloc = Account.format_bytes(total_alloc_bytes)

        # 1. Total Accounts Pill
        pill1 = ctk.CTkFrame(
            stats_frame,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=52,
        )
        pill1.pack(side="left", padx=(0, 12), fill="x", expand=True)
        box1 = ctk.CTkFrame(pill1, fg_color="transparent")
        box1.pack(padx=14, pady=8, fill="x")
        t1 = ctk.CTkLabel(box1, text="TOTAL ACCOUNTS", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
        t1.pack(anchor="w")
        self.total_accounts_lbl = ctk.CTkLabel(
            box1, text=f"{total_drives} Active", font=Fonts.BODY_BOLD, text_color=Colors.ACCENT_LIGHT
        )
        self.total_accounts_lbl.pack(anchor="w")

        # 2. Streaming Drives Pill
        pill2 = ctk.CTkFrame(
            stats_frame,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=52,
        )
        pill2.pack(side="left", padx=(0, 12), fill="x", expand=True)
        box2 = ctk.CTkFrame(pill2, fg_color="transparent")
        box2.pack(padx=14, pady=8, fill="x")
        t2 = ctk.CTkLabel(box2, text="STREAMING DRIVES", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
        t2.pack(anchor="w")
        self.streaming_drives_lbl = ctk.CTkLabel(
            box2, text=f"{mounted_count} Mounted", font=Fonts.BODY_BOLD, text_color=Colors.STATUS_MOUNTED
        )
        self.streaming_drives_lbl.pack(anchor="w")

        # 3. Cloud Usage Pill
        pill3 = ctk.CTkFrame(
            stats_frame,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=52,
        )
        pill3.pack(side="left", padx=(0, 12), fill="x", expand=True)
        box3 = ctk.CTkFrame(pill3, fg_color="transparent")
        box3.pack(padx=14, pady=8, fill="x")
        t3 = ctk.CTkLabel(box3, text="CLOUD USAGE", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
        t3.pack(anchor="w")
        self.cloud_usage_lbl = ctk.CTkLabel(
            box3,
            text=f"{formatted_used} of {formatted_alloc}",
            font=Fonts.BODY_BOLD,
            text_color=Colors.ACCENT_CYAN,
        )
        self.cloud_usage_lbl.pack(anchor="w")

    def update_stats(self):
        """Update metrics bar labels with current account numbers and storage totals."""
        total_drives = len(self.accounts)
        mounted_count = sum(1 for a in self.accounts if a.is_mounted)
        total_used_bytes = sum(a.used_storage_bytes for a in self.accounts)
        total_alloc_bytes = sum(a.total_storage_bytes for a in self.accounts)

        formatted_used = Account.format_bytes(total_used_bytes)
        formatted_alloc = Account.format_bytes(total_alloc_bytes)

        if self.total_accounts_lbl and self.total_accounts_lbl.winfo_exists():
            self.total_accounts_lbl.configure(text=f"{total_drives} Active")
        if self.streaming_drives_lbl and self.streaming_drives_lbl.winfo_exists():
            self.streaming_drives_lbl.configure(text=f"{mounted_count} Mounted")
        if self.cloud_usage_lbl and self.cloud_usage_lbl.winfo_exists():
            self.cloud_usage_lbl.configure(text=f"{formatted_used} of {formatted_alloc}")

    def render_cards(self):
        """Render grid of DriveCards or empty state."""
        # Clear existing cards
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
        self.cards.clear()

        if not self.accounts:
            self._render_empty_state()
            return

        for idx, account in enumerate(self.accounts):
            row = idx // 2
            col = idx % 2

            card = DriveCard(
                self.scroll_frame,
                account=account,
                on_open_drive=self.on_open_drive,
                on_toggle_mount=self.on_toggle_mount,
                on_settings=self.on_settings,
                on_browse_drive=self.on_browse_drive,
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            self.cards.append(card)

    def _render_empty_state(self):
        """Display helpful empty state when no accounts are configured."""
        empty_box = ctk.CTkFrame(
            self.scroll_frame,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        empty_box.pack(fill="both", expand=True, padx=40, pady=40)

        icon_lbl = ctk.CTkLabel(empty_box, text="", image=get_drive_hardware_icon(64, "#8B5CF6"))
        icon_lbl.pack(pady=(40, 12))

        msg_lbl = ctk.CTkLabel(
            empty_box,
            text="No Google Drive Accounts Connected",
            font=Fonts.CARD_TITLE,
            text_color=Colors.TEXT_PRIMARY,
        )
        msg_lbl.pack(pady=(0, 6))

        sub_lbl = ctk.CTkLabel(
            empty_box,
            text="Connect your first Google account to mount it as a Windows drive letter\nand enable seamless streaming or local offline synchronization.",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
            justify="center",
        )
        sub_lbl.pack(pady=(0, 20))

        add_btn = ctk.CTkButton(
            empty_box,
            text="+ Add Google Drive Account",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=40,
            command=self.on_add_drive,
        )
        add_btn.pack(pady=(0, 40))

    def update_accounts(self, accounts: list[Account]):
        """Update accounts list, recalculate metrics, and redraw cards."""
        self.accounts = accounts
        self.update_stats()
        self.render_cards()
