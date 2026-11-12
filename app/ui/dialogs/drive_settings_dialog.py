"""Drive Settings & Account Configuration modal dialog with Hybrid Mode conflict validation."""

from typing import Callable, Optional
from pathlib import Path
from tkinter import filedialog, messagebox
import customtkinter as ctk

from app.models.account import Account
from app.config.theme import Colors, Fonts, Dimensions
from app.ui.assets import get_symbol_icon
from app.utils.platform_checks import get_available_drive_letters
from app.ui.dialogs.confirmation_dialog import ConfirmationDialog
from app.core.storage_manager import StorageManager

class DriveSettingsDialog(ctk.CTkToplevel):
    """Modal dialog for fine-tuning individual Google Drive account settings and hybrid mode."""

    def __init__(
        self,
        master,
        account: Account,
        storage_manager: Optional[StorageManager] = None,
        on_account_updated: Optional[Callable[[Account], None]] = None,
        on_account_deleted: Optional[Callable[[Account], None]] = None,
        on_view_storage: Optional[Callable[[Account], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.account = account
        self.storage_manager = storage_manager
        self.on_account_updated = on_account_updated
        self.on_account_deleted = on_account_deleted
        self.on_view_storage = on_view_storage

        self.title(f"Drive Options - {account.display_name}")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_MAIN)

        # Form variables
        self.name_var = ctk.StringVar(value=account.display_name)
        self.letter_var = ctk.StringVar(value=account.drive_letter)
        self.streaming_var = ctk.BooleanVar(value=account.streaming_enabled)
        self.offline_var = ctk.BooleanVar(value=account.offline_enabled)
        self.cache_size_var = ctk.StringVar(value=account.cache_size)
        self.cache_expiry_var = ctk.StringVar(value=account.cache_expiry)
        self.read_only_var = ctk.BooleanVar(value=account.read_only)
        self.auto_mount_var = ctk.BooleanVar(value=account.auto_mount)
        self.offline_path_var = ctk.StringVar(value=account.offline_path)

        # Modal setup
        self.transient(master)
        self.grab_set()

        self._build_ui()

        # Center on master
        self.update_idletasks()
        try:
            x = master.winfo_x() + (master.winfo_width() // 2) - 260
            y = master.winfo_y() + (master.winfo_height() // 2) - 340
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _build_ui(self):
        container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        container.pack(fill="both", expand=True, padx=16, pady=16)

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=22, pady=18)

        # Header with Storage Details button
        head_row = ctk.CTkFrame(inner, fg_color="transparent")
        head_row.pack(fill="x", pady=(0, 10))

        head_box = ctk.CTkFrame(head_row, fg_color="transparent")
        head_box.pack(side="left")

        t_lbl = ctk.CTkLabel(head_box, text="Drive & Account Options", font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY)
        t_lbl.pack(anchor="w")

        em_lbl = ctk.CTkLabel(head_box, text=f"Remote: {self.account.remote_name} ({self.account.email})", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
        em_lbl.pack(anchor="w")

        storage_btn = ctk.CTkButton(
            head_row,
            text="Storage Quota",
            font=Fonts.CAPTION,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=28,
            command=self._handle_view_storage
        )
        storage_btn.pack(side="right")

        # 1. Display Name
        n_lbl = ctk.CTkLabel(inner, text="Display Name:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        n_lbl.pack(anchor="w", pady=(0, 2))

        n_entry = ctk.CTkEntry(
            inner,
            textvariable=self.name_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.INPUT_BORDER,
            height=32
        )
        n_entry.pack(fill="x", pady=(0, 10))

        # 2. Operating Modes (Hybrid separation)
        mode_box = ctk.CTkFrame(inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS)
        mode_box.pack(fill="x", pady=(0, 10))

        mode_inner = ctk.CTkFrame(mode_box, fg_color="transparent")
        mode_inner.pack(fill="x", padx=12, pady=8)

        m_title = ctk.CTkLabel(mode_inner, text="Storage Modes (Independent Configuration):", font=Fonts.BADGE, text_color=Colors.TEXT_MUTED)
        m_title.pack(anchor="w", pady=(0, 4))

        st_chk = ctk.CTkCheckBox(
            mode_inner,
            text="Enable Streaming Mode (Virtual drive letter)",
            variable=self.streaming_var,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY
        )
        st_chk.pack(anchor="w", pady=(0, 4))

        off_chk = ctk.CTkCheckBox(
            mode_inner,
            text="Enable Offline Storage (Local directory backup/mirror)",
            variable=self.offline_var,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY
        )
        off_chk.pack(anchor="w")

        # 3. Drive Letter & Cache Limits (Two columns)
        two_col = ctk.CTkFrame(inner, fg_color="transparent")
        two_col.pack(fill="x", pady=(0, 10))

        # Drive Letter
        c1 = ctk.CTkFrame(two_col, fg_color="transparent")
        c1.pack(side="left", fill="x", expand=True, padx=(0, 8))

        l_lbl = ctk.CTkLabel(c1, text="Assigned Drive Letter:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        l_lbl.pack(anchor="w", pady=(0, 2))

        avail = [self.account.drive_letter] + get_available_drive_letters()
        avail = list(dict.fromkeys(avail))

        letter_menu = ctk.CTkOptionMenu(
            c1,
            values=avail,
            variable=self.letter_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            height=32
        )
        letter_menu.pack(fill="x")

        # Cache Limit
        c2 = ctk.CTkFrame(two_col, fg_color="transparent")
        c2.pack(side="right", fill="x", expand=True, padx=(8, 0))

        cs_lbl = ctk.CTkLabel(c2, text="Max Cache Size:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        cs_lbl.pack(anchor="w", pady=(0, 2))

        cache_menu = ctk.CTkOptionMenu(
            c2,
            values=["5G", "10G", "15G", "25G", "50G", "100G"],
            variable=self.cache_size_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            height=32
        )
        cache_menu.pack(fill="x")

        # 4. Offline Directory
        o_lbl = ctk.CTkLabel(inner, text="Offline Local Directory:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        o_lbl.pack(anchor="w", pady=(0, 2))

        path_row = ctk.CTkFrame(inner, fg_color="transparent")
        path_row.pack(fill="x", pady=(0, 10))

        path_entry = ctk.CTkEntry(
            path_row,
            textvariable=self.offline_path_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.INPUT_BORDER,
            height=32
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        b_btn = ctk.CTkButton(
            path_row,
            text="Browse...",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=32,
            command=self._browse_path
        )
        b_btn.pack(side="right")

        # 5. Toggles (Read-Only & Auto-Mount)
        toggles_box = ctk.CTkFrame(inner, fg_color="transparent")
        toggles_box.pack(fill="x", pady=(0, 12))

        ro_chk = ctk.CTkCheckBox(
            toggles_box,
            text="Mount as Read-Only (Prevents cloud modifications)",
            variable=self.read_only_var,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY
        )
        ro_chk.pack(anchor="w", pady=(0, 6))

        am_chk = ctk.CTkCheckBox(
            toggles_box,
            text="Automatically mount this drive when application starts",
            variable=self.auto_mount_var,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY
        )
        am_chk.pack(anchor="w")

        # 6. Danger Zone: Remove Account
        danger_box = ctk.CTkFrame(
            inner,
            fg_color=Colors.CARD_INNER,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        danger_box.pack(fill="x", pady=(0, 14))

        danger_inner = ctk.CTkFrame(danger_box, fg_color="transparent")
        danger_inner.pack(fill="x", padx=12, pady=8)

        rem_desc = ctk.CTkLabel(
            danger_inner,
            text="Disconnect account and release assigned Windows drive letter.",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED
        )
        rem_desc.pack(side="left")

        rem_btn = ctk.CTkButton(
            danger_inner,
            text="Remove Drive",
            font=Fonts.BUTTON,
            fg_color=Colors.STATUS_ERROR,
            hover_color="#DC2626",
            height=28,
            command=self._handle_remove
        )
        rem_btn.pack(side="right")

        # 7. Bottom Action Buttons
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")

        cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=36,
            width=90,
            command=self.destroy
        )
        cancel_btn.pack(side="right")

        save_btn = ctk.CTkButton(
            btn_row,
            text="Save Changes",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            height=36,
            width=130,
            command=self._handle_save
        )
        save_btn.pack(side="right", padx=(0, 10))

    def _browse_path(self):
        folder = filedialog.askdirectory(title="Select Offline Directory")
        if folder:
            self.offline_path_var.set(folder)

    def _handle_view_storage(self):
        if self.on_view_storage:
            self.on_view_storage(self.account)

    def _handle_save(self):
        # Hybrid Mode conflict validation
        offline_p = self.offline_path_var.get().strip()
        assigned_letter = self.letter_var.get().upper().rstrip("\\")

        if self.offline_var.get() and offline_p:
            clean_off = os.path.abspath(offline_p).upper()
            if clean_off.startswith(f"{assigned_letter}\\") or clean_off == f"{assigned_letter}:" or clean_off == f"{assigned_letter}:\\":
                messagebox.showerror(
                    "Storage Target Conflict",
                    f"Hybrid Mode Violation: The offline directory cannot be placed inside the virtual streaming drive {assigned_letter}:\\!\n\n"
                    "Streaming and offline storage must use separate physical disk locations and independent configurations."
                )
                return

        self.account.display_name = self.name_var.get().strip() or self.account.display_name
        self.account.drive_letter = self.letter_var.get()
        self.account.streaming_enabled = self.streaming_var.get()
        self.account.offline_enabled = self.offline_var.get()
        self.account.cache_size = self.cache_size_var.get()
        self.account.read_only = self.read_only_var.get()
        self.account.auto_mount = self.auto_mount_var.get()
        self.account.offline_path = offline_p

        self.destroy()
        if self.on_account_updated:
            self.on_account_updated(self.account)

    def _handle_remove(self):
        ConfirmationDialog(
            self,
            title="Remove Drive Account",
            message=f"Are you sure you want to remove '{self.account.display_name}'? The drive will be unmounted.",
            confirm_text="Remove",
            is_destructive=True,
            on_confirm=self._do_remove
        )

    def _do_remove(self):
        self.destroy()
        if self.on_account_deleted:
            self.on_account_deleted(self.account)
