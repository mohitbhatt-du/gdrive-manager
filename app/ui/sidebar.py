"""Modern navigation sidebar component with status footer."""

from collections.abc import Callable

import customtkinter as ctk

from app.__version__ import __version__
from app.config.theme import Colors, Dimensions, Fonts
from app.ui.assets import get_drive_hardware_icon, get_gdrive_icon, get_symbol_icon


class Sidebar(ctk.CTkFrame):
    """Left navigation panel with brand header, nav buttons, and system status footer."""

    def __init__(
        self,
        master,
        on_navigate: Callable[[str], None],
        on_add_drive_click: Callable[[], None],
        version: str = f"v{__version__}",
        **kwargs,
    ):
        super().__init__(
            master, width=Dimensions.SIDEBAR_WIDTH, fg_color=Colors.BG_SIDEBAR, corner_radius=0, **kwargs
        )
        self.on_navigate = on_navigate
        self.on_add_drive_click = on_add_drive_click
        self.version = version
        self.current_page = "drives"
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self.grid_rowconfigure(2, weight=1)  # Expand middle nav space
        self._build_ui()

    def _build_ui(self):
        # 1. Brand Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(24, 20), sticky="ew")

        logo_label = ctk.CTkLabel(header_frame, text="", image=get_gdrive_icon(32), width=36)
        logo_label.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")

        app_title = ctk.CTkLabel(
            title_box, text="GDrive Manager", font=Fonts.SECTION_HEADER, text_color=Colors.TEXT_PRIMARY
        )
        app_title.pack(anchor="w")

        app_subtitle = ctk.CTkLabel(
            title_box, text="Desktop Cloud Sync", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED
        )
        app_subtitle.pack(anchor="w")

        # 2. Primary Action: Add Drive Button
        add_btn = ctk.CTkButton(
            self,
            text="Add Drive",
            image=get_symbol_icon("plus", 16, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=38,
            command=self.on_add_drive_click,
        )
        add_btn.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="ew")

        # 3. Navigation Menu Items
        nav_container = ctk.CTkFrame(self, fg_color="transparent")
        nav_container.grid(row=2, column=0, padx=12, pady=0, sticky="nsew")

        nav_items = [
            ("drives", "My Drives", get_drive_hardware_icon(18, "#8B5CF6")),
            ("streaming", "Streaming", get_symbol_icon("cloud", 18, Colors.TEXT_SECONDARY)),
            ("offline", "Offline Storage", get_symbol_icon("folder", 18, Colors.TEXT_SECONDARY)),
            ("transfers", "Transfers", get_symbol_icon("sync", 18, Colors.TEXT_SECONDARY)),
            ("logs", "Logs & Diagnostics", get_symbol_icon("info", 18, Colors.TEXT_SECONDARY)),
            ("settings", "Settings", get_symbol_icon("gear", 18, Colors.TEXT_SECONDARY)),
            ("about", "About", get_symbol_icon("check", 18, Colors.TEXT_SECONDARY)),
        ]

        for page_id, label, icon in nav_items:
            btn = ctk.CTkButton(
                nav_container,
                text=f"  {label}",
                image=icon,
                compound="left",
                anchor="w",
                font=Fonts.BODY,
                text_color=Colors.TEXT_SECONDARY,
                fg_color="transparent",
                hover_color=Colors.BG_SIDEBAR_HOVER,
                corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
                height=40,
                command=lambda p=page_id: self._handle_nav(p),
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[page_id] = btn

        self.set_active("drives")

        # 4. Bottom Sidebar Status Footer
        footer_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_INNER,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        footer_frame.grid(row=3, column=0, padx=12, pady=16, sticky="ew")

        # System Status Dot & Label
        status_row = ctk.CTkFrame(footer_frame, fg_color="transparent")
        status_row.pack(fill="x", padx=12, pady=(10, 4))

        status_dot = ctk.CTkLabel(status_row, text="●", font=Fonts.BADGE, text_color=Colors.STATUS_MOUNTED)
        status_dot.pack(side="left", padx=(0, 6))

        self.status_label = ctk.CTkLabel(
            status_row, text="Ready & Connected", font=Fonts.CAPTION, text_color=Colors.TEXT_PRIMARY
        )
        self.status_label.pack(side="left")

        # Active account summary
        self.account_summary_lbl = ctk.CTkLabel(
            footer_frame, text="4 Drives Configured", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED
        )
        self.account_summary_lbl.pack(anchor="w", padx=12, pady=(0, 4))

        # Version string
        version_lbl = ctk.CTkLabel(
            footer_frame,
            text=f"GDrive Manager {self.version}",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED,
        )
        version_lbl.pack(anchor="w", padx=12, pady=(0, 10))

    def _handle_nav(self, page_id: str):
        self.set_active(page_id)
        self.on_navigate(page_id)

    def set_active(self, page_id: str):
        self.current_page = page_id
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(
                    fg_color=Colors.BG_SIDEBAR_ACTIVE,
                    text_color=Colors.TEXT_PRIMARY,
                    border_width=1,
                    border_color=Colors.ACCENT_PRIMARY,
                )
            else:
                btn.configure(fg_color="transparent", text_color=Colors.TEXT_SECONDARY, border_width=0)

    def update_status(self, text: str, color: str = Colors.STATUS_MOUNTED):
        self.status_label.configure(text=text, text_color=Colors.TEXT_PRIMARY)

    def update_account_count(self, count: int):
        self.account_summary_lbl.configure(text=f"{count} Drive(s) Configured")
