"""Reusable modern Drive Card component for Google Drive accounts."""

from collections.abc import Callable

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.models.account import Account
from app.ui.assets import get_gdrive_icon, get_symbol_icon


class DriveCard(ctk.CTkFrame):
    """Modern dark-themed Drive Card displaying account status, storage, and actions."""

    def __init__(
        self,
        master,
        account: Account,
        on_open_drive: Callable[[Account], None] | None = None,
        on_toggle_mount: Callable[[Account], None] | None = None,
        on_settings: Callable[[Account], None] | None = None,
        on_browse_drive: Callable[[Account], None] | None = None,
        **kwargs,
    ):
        super().__init__(
            master,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            **kwargs,
        )
        self.account = account
        self.on_open_drive = on_open_drive
        self.on_toggle_mount = on_toggle_mount
        self.on_settings = on_settings
        self.on_browse_drive = on_browse_drive

        self._build_ui()

    def _build_ui(self):
        # Configure layout grid
        self.grid_columnconfigure(1, weight=1)

        # Padding container
        pad_x = 18
        pad_y = 16

        # --- Top Row: Drive Icon, Name/Email, Status Badge, Drive Letter Badge ---
        icon_label = ctk.CTkLabel(self, text="", image=get_gdrive_icon(36), width=40)
        icon_label.grid(row=0, column=0, rowspan=2, padx=(pad_x, 12), pady=(pad_y, 0), sticky="nw")

        # Name & Email stack
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=0, column=1, padx=(0, 10), pady=(pad_y, 2), sticky="w")

        name_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        name_row.pack(anchor="w", fill="x")

        display_name_lbl = ctk.CTkLabel(
            name_row, text=self.account.display_name, font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY
        )
        display_name_lbl.pack(side="left")

        if self.account.is_sample:
            sample_tag = ctk.CTkLabel(
                name_row,
                text="SAMPLE DATA",
                font=Fonts.CAPTION,
                text_color=Colors.ACCENT_LIGHT,
                fg_color=Colors.BG_SIDEBAR_ACTIVE,
                corner_radius=4,
                padx=6,
                pady=1,
            )
            sample_tag.pack(side="left", padx=(8, 0))

        email_lbl = ctk.CTkLabel(
            title_frame, text=self.account.email, font=Fonts.CAPTION, text_color=Colors.TEXT_SECONDARY
        )
        email_lbl.pack(anchor="w", pady=(1, 0))

        # Badges Frame (Status Pill & Drive Letter Badge)
        badge_frame = ctk.CTkFrame(self, fg_color="transparent")
        badge_frame.grid(row=0, column=2, padx=(0, pad_x), pady=(pad_y, 0), sticky="ne")

        # Drive Letter Pill
        letter_color = Colors.ACCENT_PRIMARY if self.account.is_mounted else Colors.BG_SIDEBAR
        letter_pill = ctk.CTkLabel(
            badge_frame,
            text=f"  {self.account.drive_letter}  ",
            font=Fonts.BADGE,
            text_color=Colors.TEXT_PRIMARY,
            fg_color=letter_color,
            corner_radius=6,
            height=24,
        )
        letter_pill.pack(side="right", padx=(6, 0))

        # Status Pill
        status_color = (
            Colors.STATUS_MOUNTED
            if self.account.is_mounted
            else (Colors.STATUS_CONNECTED if self.account.status == "Connected" else Colors.STATUS_MUTED)
        )
        status_text = "MOUNTED" if self.account.is_mounted else self.account.status.upper()
        status_pill = ctk.CTkLabel(
            badge_frame,
            text=f"  ● {status_text}  ",
            font=Fonts.CAPTION,
            text_color=status_color,
            fg_color=Colors.INPUT_BG,
            corner_radius=6,
            height=24,
        )
        status_pill.pack(side="right")

        # --- Middle Row: Operating Mode & Storage Progress Bar ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=1, columnspan=2, padx=(0, pad_x), pady=(12, 14), sticky="nsew")

        mode_row = ctk.CTkFrame(content_frame, fg_color="transparent")
        mode_row.pack(fill="x", pady=(0, 6))

        mode_lbl = ctk.CTkLabel(
            mode_row,
            text=f"Mode: {self.account.operating_mode}",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED,
        )
        mode_lbl.pack(side="left")

        storage_text = f"{self.account.formatted_used} / {self.account.formatted_total} ({self.account.storage_percentage:.0f}%)"
        storage_lbl = ctk.CTkLabel(
            mode_row, text=storage_text, font=Fonts.CAPTION, text_color=Colors.TEXT_SECONDARY
        )
        storage_lbl.pack(side="right")

        # Elegant Progress Bar
        pct = self.account.storage_percentage / 100.0
        progress_bar = ctk.CTkProgressBar(
            content_frame,
            height=6,
            corner_radius=3,
            fg_color=Colors.PROGRESS_BG,
            progress_color=Colors.ACCENT_PRIMARY,
        )
        progress_bar.set(pct)
        progress_bar.pack(fill="x")

        # --- Bottom Row: Action Buttons ---
        actions_frame = ctk.CTkFrame(
            self, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS, height=46
        )
        actions_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="ew")

        # Mount/Unmount Button
        mount_text = "Unmount" if self.account.is_mounted else "Mount Drive"
        mount_icon = get_symbol_icon("stop" if self.account.is_mounted else "play", 14, Colors.TEXT_PRIMARY)
        mount_fg = Colors.CARD_HOVER if self.account.is_mounted else Colors.ACCENT_PRIMARY

        self.mount_btn = ctk.CTkButton(
            actions_frame,
            text=mount_text,
            image=mount_icon,
            compound="left",
            font=Fonts.BUTTON,
            fg_color=mount_fg,
            hover_color=Colors.ACCENT_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            command=self._handle_toggle_mount,
        )
        self.mount_btn.pack(side="left", padx=(10, 8), pady=7)

        # Browse In-App Button (Does not require virtual drive mount)
        browse_btn = ctk.CTkButton(
            actions_frame,
            text="Browse",
            image=get_symbol_icon("folder", 14, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            command=self._handle_browse_drive,
        )
        browse_btn.pack(side="left", padx=(0, 8), pady=7)

        # Open in Explorer Button
        open_btn = ctk.CTkButton(
            actions_frame,
            text="Open Drive",
            image=get_symbol_icon("open", 14, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            command=self._handle_open_drive,
        )
        open_btn.pack(side="left", padx=(0, 8), pady=7)

        # Settings / Options Gear Button
        settings_btn = ctk.CTkButton(
            actions_frame,
            text="Options",
            image=get_symbol_icon("gear", 14, Colors.TEXT_SECONDARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color="transparent",
            text_color=Colors.TEXT_SECONDARY,
            hover_color=Colors.CARD_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            command=self._handle_settings,
        )
        settings_btn.pack(side="right", padx=(0, 10), pady=7)

    def _handle_browse_drive(self):
        if self.on_browse_drive:
            self.on_browse_drive(self.account)

    def _handle_open_drive(self):
        if self.on_open_drive:
            self.on_open_drive(self.account)

    def _handle_toggle_mount(self):
        if self.on_toggle_mount:
            self.on_toggle_mount(self.account)

    def _handle_settings(self):
        if self.on_settings:
            self.on_settings(self.account)
