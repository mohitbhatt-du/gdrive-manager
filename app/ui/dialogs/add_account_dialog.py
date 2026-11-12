"""Add Google Drive Account modal dialog with live Google OAuth integration."""

from typing import Callable, Optional
from tkinter import filedialog, messagebox
import customtkinter as ctk

from app.models.account import Account
from app.config.theme import Colors, Fonts, Dimensions
from app.ui.assets import get_gdrive_icon, get_symbol_icon
from app.utils.platform_checks import get_available_drive_letters
from app.core.auth_manager import AuthManager

class AddAccountDialog(ctk.CTkToplevel):
    """Modal dialog for configuring and connecting a new Google Drive account."""

    def __init__(
        self,
        master,
        auth_manager: Optional[AuthManager] = None,
        on_account_created: Optional[Callable[[Account], None]] = None,
        **kwargs
    ):
        super().__init__(master, **kwargs)
        self.title("Add Google Drive Account")
        self.geometry("520x660")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_MAIN)

        self.auth_manager = auth_manager
        self.on_account_created = on_account_created

        # Form variables
        self.name_var = ctk.StringVar(value="")
        self.letter_var = ctk.StringVar()
        self.mode_var = ctk.StringVar(value="Hybrid (Streaming + Offline)")
        self.offline_path_var = ctk.StringVar(value="")
        self.cache_size_var = ctk.StringVar(value="15G")
        self.status_var = ctk.StringVar(value="")

        # Modal setup
        self.transient(master)
        self.grab_set()

        self._init_available_letters()
        self._build_ui()

        # Center on master
        self.update_idletasks()
        try:
            x = master.winfo_x() + (master.winfo_width() // 2) - 260
            y = master.winfo_y() + (master.winfo_height() // 2) - 330
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

    def _init_available_letters(self):
        letters = get_available_drive_letters()
        self.available_letters = letters or ["G:", "H:", "I:", "J:", "K:", "Z:"]
        self.letter_var.set(self.available_letters[0])

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
        inner.pack(fill="both", expand=True, padx=22, pady=20)

        # Header with Logo
        head_row = ctk.CTkFrame(inner, fg_color="transparent")
        head_row.pack(fill="x", pady=(0, 16))

        logo = ctk.CTkLabel(head_row, text="", image=get_gdrive_icon(36))
        logo.pack(side="left", padx=(0, 12))

        head_box = ctk.CTkFrame(head_row, fg_color="transparent")
        head_box.pack(side="left")

        t_lbl = ctk.CTkLabel(head_box, text="Connect Google Account", font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY)
        t_lbl.pack(anchor="w")

        s_lbl = ctk.CTkLabel(head_box, text="Mount as a virtual drive or maintain offline storage", font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED)
        s_lbl.pack(anchor="w")

        # 1. Display Name Entry
        n_lbl = ctk.CTkLabel(inner, text="Account Display Name:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        n_lbl.pack(anchor="w", pady=(0, 4))

        self.name_entry = ctk.CTkEntry(
            inner,
            textvariable=self.name_var,
            placeholder_text="e.g. Personal Google Drive or Work Drive",
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.INPUT_BORDER,
            height=36
        )
        self.name_entry.pack(fill="x", pady=(0, 14))

        # 2. Windows Drive Letter Selection
        l_lbl = ctk.CTkLabel(inner, text="Assign Windows Drive Letter:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        l_lbl.pack(anchor="w", pady=(0, 4))

        letter_menu = ctk.CTkOptionMenu(
            inner,
            values=self.available_letters,
            variable=self.letter_var,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            button_hover_color=Colors.ACCENT_HOVER,
            dropdown_fg_color=Colors.CARD_BG,
            height=36
        )
        letter_menu.pack(fill="x", pady=(0, 14))

        # 3. Operating Mode Selection
        m_lbl = ctk.CTkLabel(inner, text="Storage Operating Mode:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        m_lbl.pack(anchor="w", pady=(0, 4))

        modes = [
            "Hybrid (Streaming + Offline)",
            "Streaming Only (Explorer Virtual Drive)",
            "Offline Only (Local Directory Sync)"
        ]
        mode_menu = ctk.CTkOptionMenu(
            inner,
            values=modes,
            variable=self.mode_var,
            command=self._on_mode_changed,
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            button_color=Colors.ACCENT_PRIMARY,
            button_hover_color=Colors.ACCENT_HOVER,
            dropdown_fg_color=Colors.CARD_BG,
            height=36
        )
        mode_menu.pack(fill="x", pady=(0, 14))

        # 4. Offline Destination Directory (Conditional/Optional)
        self.offline_frame = ctk.CTkFrame(inner, fg_color="transparent")
        self.offline_frame.pack(fill="x", pady=(0, 14))

        o_lbl = ctk.CTkLabel(self.offline_frame, text="Offline Local Directory:", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY)
        o_lbl.pack(anchor="w", pady=(0, 4))

        path_row = ctk.CTkFrame(self.offline_frame, fg_color="transparent")
        path_row.pack(fill="x")

        path_entry = ctk.CTkEntry(
            path_row,
            textvariable=self.offline_path_var,
            placeholder_text="e.g. D:/GDriveManager/Personal",
            font=Fonts.BODY,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.INPUT_BORDER,
            height=36
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            path_row,
            text="Browse...",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=36,
            command=self._browse_offline_path
        )
        browse_btn.pack(side="right")

        # 5. Security & Live Status Box
        info_box = ctk.CTkFrame(
            inner,
            fg_color=Colors.CARD_INNER,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        info_box.pack(fill="x", pady=(0, 14))

        info_text = (
            "🔒 Standard Google OAuth 2.0 flow is used. Refresh tokens are secured directly "
            "in Windows Credential Manager. No plain-text tokens or passwords are ever stored."
        )
        info_lbl = ctk.CTkLabel(
            info_box,
            text=info_text,
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_SECONDARY,
            wraplength=420,
            justify="left"
        )
        info_lbl.pack(padx=14, pady=(10, 4))

        # Dynamic Status Label
        self.live_status_lbl = ctk.CTkLabel(
            info_box,
            textvariable=self.status_var,
            font=Fonts.BODY_BOLD,
            text_color=Colors.ACCENT_LIGHT
        )
        self.live_status_lbl.pack(padx=14, pady=(0, 8))

        # 6. Action Buttons
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x", side="bottom")

        self.cancel_btn = ctk.CTkButton(
            btn_row,
            text="Cancel",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=38,
            width=100,
            command=self.destroy
        )
        self.cancel_btn.pack(side="right")

        self.submit_btn = ctk.CTkButton(
            btn_row,
            text="Connect with Google",
            image=get_symbol_icon("plus", 14, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            height=38,
            width=180,
            command=self._handle_submit
        )
        self.submit_btn.pack(side="right", padx=(0, 10))

    def _on_mode_changed(self, mode: str):
        if "Offline" in mode:
            self.offline_frame.pack(fill="x", pady=(0, 14))
        else:
            self.offline_frame.pack_forget()

    def _browse_offline_path(self):
        folder = filedialog.askdirectory(title="Select Offline Destination Folder")
        if folder:
            self.offline_path_var.set(folder)

    def _handle_submit(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Please provide a display name for this account.")
            self.name_entry.focus_set()
            return

        mode_str = self.mode_var.get()
        streaming_enabled = "Streaming" in mode_str
        offline_enabled = "Offline" in mode_str

        # If live AuthManager is present and rclone is available, launch real OAuth
        if self.auth_manager and self.auth_manager.rclone_service.is_available():
            self.submit_btn.configure(state="disabled", text="Authenticating...")
            self.cancel_btn.configure(state="disabled")
            self.status_var.set("Connecting to Google OAuth...")

            def on_status(msg: str):
                self.after(0, lambda: self.status_var.set(msg))

            def on_success(account: Account):
                def _done():
                    self.destroy()
                    if self.on_account_created:
                        self.on_account_created(account)
                self.after(0, _done)

            def on_error(err: str):
                def _err():
                    self.submit_btn.configure(state="normal", text="Connect with Google")
                    self.cancel_btn.configure(state="normal")
                    self.status_var.set("")
                    messagebox.showerror("Authentication Error", err)
                self.after(0, _err)

            self.auth_manager.start_google_auth(
                account_name=name,
                drive_letter=self.letter_var.get(),
                streaming_enabled=streaming_enabled,
                offline_enabled=offline_enabled,
                offline_path=self.offline_path_var.get(),
                cache_size=self.cache_size_var.get(),
                on_status_update=on_status,
                on_success=on_success,
                on_error=on_error
            )
        else:
            # When rclone binary is not yet detected on system
            account_id = name.lower().replace(" ", "_")
            new_account = Account(
                id=account_id,
                email=f"{account_id}@gmail.com",
                display_name=name,
                remote_name=f"remote_{account_id}",
                drive_letter=self.letter_var.get(),
                streaming_enabled=streaming_enabled,
                offline_enabled=offline_enabled,
                offline_path=self.offline_path_var.get(),
                cache_size=self.cache_size_var.get(),
                used_storage_bytes=0,
                total_storage_bytes=15 * 1024 * 1024 * 1024,
                is_mounted=False,
                status="Connected",
                is_sample=False
            )
            self.destroy()
            if self.on_account_created:
                self.on_account_created(new_account)
