"""Offline Mode and synchronization management view."""

from typing import List, Callable, Optional
from tkinter import filedialog
import customtkinter as ctk
from app.models.account import Account
from app.config.theme import Colors, Fonts, Dimensions
from app.ui.assets import get_symbol_icon

class OfflinePage(ctk.CTkFrame):
    """View dedicated to offline local folders, selective sync, and two-way bisync."""

    def __init__(
        self,
        master,
        accounts: List[Account],
        on_start_sync: Optional[Callable[[Account, str, str, bool], None]] = None,
        **kwargs
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.accounts = accounts
        self.on_start_sync = on_start_sync

        self.selected_account: Optional[Account] = accounts[0] if accounts else None
        self.local_path_var = ctk.StringVar(value=self.selected_account.offline_path if self.selected_account else "")
        self.sync_type_var = ctk.StringVar(value="Cloud -> Local (Download/Copy)")
        self.dry_run_var = ctk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))

        title = ctk.CTkLabel(
            header,
            text="Offline Storage & Synchronization",
            font=Fonts.HERO,
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Keep full local copies of your files, configure one-way mirrors, or maintain bidirectional bi-sync",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Main Configuration Container
        form_card = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        form_card.pack(fill="x", padx=28, pady=(0, 20))

        card_inner = ctk.CTkFrame(form_card, fg_color="transparent")
        card_inner.pack(fill="x", padx=20, pady=20)

        # 1. Target Account Selector
        acc_lbl = ctk.CTkLabel(card_inner, text="Select Google Account:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        acc_lbl.pack(anchor="w", pady=(0, 4))

        account_names = [f"{a.display_name} ({a.email})" for a in self.accounts] or ["No Accounts Available"]
        self.account_menu = ctk.CTkOptionMenu(
            card_inner,
            values=account_names,
            command=self._on_account_selected,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            button_hover_color=Colors.ACCENT_HOVER,
            dropdown_fg_color=Colors.CARD_BG,
            height=36
        )
        self.account_menu.pack(fill="x", pady=(0, 16))

        # 2. Local Storage Directory
        dir_lbl = ctk.CTkLabel(card_inner, text="Local Destination Directory:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        dir_lbl.pack(anchor="w", pady=(0, 4))

        path_row = ctk.CTkFrame(card_inner, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, 16))

        self.path_entry = ctk.CTkEntry(
            path_row,
            textvariable=self.local_path_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.INPUT_BORDER,
            height=36
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        browse_btn = ctk.CTkButton(
            path_row,
            text="Browse...",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=36,
            command=self._browse_directory
        )
        browse_btn.pack(side="right")

        # 3. Synchronization Operation Type
        sync_lbl = ctk.CTkLabel(card_inner, text="Operation Mode:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        sync_lbl.pack(anchor="w", pady=(0, 4))

        sync_modes = [
            "Cloud -> Local (Download/Copy - Safe, preserves existing local)",
            "Cloud -> Local (Mirror/Sync - Deletes local files deleted on cloud)",
            "Local -> Cloud (Upload/Copy)",
            "Local -> Cloud (Mirror/Sync - Deletes cloud files deleted locally)",
            "Two-Way Bi-Sync (Safe baseline synchronization)",
        ]
        self.sync_menu = ctk.CTkOptionMenu(
            card_inner,
            values=sync_modes,
            variable=self.sync_type_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            button_hover_color=Colors.ACCENT_HOVER,
            dropdown_fg_color=Colors.CARD_BG,
            height=36
        )
        self.sync_menu.pack(fill="x", pady=(0, 16))

        # 4. Dry Run & Safety Checkbox
        dry_chk = ctk.CTkCheckBox(
            card_inner,
            text="Dry Run Preview (Simulate changes without modifying or deleting files first)",
            variable=self.dry_run_var,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER
        )
        dry_chk.pack(anchor="w", pady=(0, 20))

        # 5. Start Operation Button
        start_btn = ctk.CTkButton(
            card_inner,
            text="Start Synchronization Task",
            image=get_symbol_icon("sync", 16, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=40,
            command=self._handle_start
        )
        start_btn.pack(anchor="w")

    def _on_account_selected(self, val: str):
        for acc in self.accounts:
            if val.startswith(acc.display_name):
                self.selected_account = acc
                if acc.offline_path:
                    self.local_path_var.set(acc.offline_path)
                break

    def _browse_directory(self):
        folder = filedialog.askdirectory(title="Select Local Offline Directory")
        if folder:
            self.local_path_var.set(folder)

    def _handle_start(self):
        if self.on_start_sync and self.selected_account:
            self.on_start_sync(
                self.selected_account,
                self.local_path_var.get(),
                self.sync_type_var.get(),
                self.dry_run_var.get()
            )
