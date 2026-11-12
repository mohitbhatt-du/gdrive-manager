"""Main dashboard view displaying account cards, statistics, and quick actions."""

from collections.abc import Callable

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.models.account import Account
from app.ui.assets import get_drive_hardware_icon
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
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.accounts = accounts
        self.on_add_drive = on_add_drive
        self.on_open_drive = on_open_drive
        self.on_toggle_mount = on_toggle_mount
        self.on_settings = on_settings

        self.cards: list[DriveCard] = []

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

        # Right Header: "+ Add GDrive" Primary Button
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
        """Build summary metric pills."""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.pack(fill="x", padx=28, pady=(0, 16))

        total_drives = len(self.accounts)
        mounted_count = sum(1 for a in self.accounts if a.is_mounted)
        total_used_bytes = sum(a.used_storage_bytes for a in self.accounts)
        total_alloc_bytes = sum(a.total_storage_bytes for a in self.accounts)

        formatted_used = Account.format_bytes(total_used_bytes)
        formatted_alloc = Account.format_bytes(total_alloc_bytes)

        stats = [
            ("Total Accounts", f"{total_drives} Active", Colors.ACCENT_LIGHT),
            ("Streaming Drives", f"{mounted_count} Mounted", Colors.STATUS_MOUNTED),
            ("Cloud Usage", f"{formatted_used} of {formatted_alloc}", Colors.ACCENT_CYAN),
        ]

        for title, val, accent in stats:
            pill = ctk.CTkFrame(
                stats_frame,
                fg_color=Colors.CARD_BG,
                corner_radius=Dimensions.CARD_CORNER_RADIUS,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                height=52,
            )
            pill.pack(side="left", padx=(0, 12), fill="x", expand=True)

            pill_box = ctk.CTkFrame(pill, fg_color="transparent")
            pill_box.pack(padx=14, pady=8, fill="x")

            t_lbl = ctk.CTkLabel(
                pill_box, text=title.upper(), font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED
            )
            t_lbl.pack(anchor="w")

            v_lbl = ctk.CTkLabel(pill_box, text=val, font=Fonts.BODY_BOLD, text_color=accent)
            v_lbl.pack(anchor="w")

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
        """Update accounts list and redraw cards."""
        self.accounts = accounts
        self.render_cards()
