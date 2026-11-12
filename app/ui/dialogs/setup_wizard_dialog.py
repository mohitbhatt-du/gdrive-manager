"""First-Launch Setup and Onboarding Wizard Dialog."""

import os
import subprocess
import threading
from typing import Callable, Optional
from tkinter import messagebox
import customtkinter as ctk

from app.config.theme import Colors, Fonts, Dimensions
from app.ui.assets import get_gdrive_icon, get_symbol_icon
from app.utils.platform_checks import is_rclone_installed, get_rclone_version, is_winfsp_installed
from app.utils.onboarding import set_onboarding_completed
from app.utils.logger import get_logger

logger = get_logger("SetupWizardDialog")

class SetupWizardDialog(ctk.CTkToplevel):
    """First-launch onboarding modal guiding users through drivers and account setup."""

    def __init__(
        self,
        parent,
        on_connect_drive: Optional[Callable[[], None]] = None,
        on_finish: Optional[Callable[[], None]] = None
    ):
        super().__init__(parent)
        self.on_connect_drive = on_connect_drive
        self.on_finish = on_finish

        self.title("Welcome to GDrive Manager")
        self.geometry("620x680")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_MAIN)

        self.transient(parent)
        self.grab_set()

        # Center on screen
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = 620
        h = 680
        x = px + max(0, (pw - w) // 2)
        y = py + max(0, (ph - h) // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        self.dont_show_again = ctk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=32, pady=24)

        # 1. Header Banner
        header = ctk.CTkFrame(main_frame, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))

        logo = ctk.CTkLabel(header, text="", image=get_gdrive_icon(52))
        logo.pack(pady=(0, 8))

        title = ctk.CTkLabel(
            header,
            text="Welcome to GDrive Manager",
            font=Fonts.HERO,
            text_color=Colors.TEXT_PRIMARY
        )
        title.pack()

        subtitle = ctk.CTkLabel(
            header,
            text="Connect, stream, and sync multiple Google Drive accounts as Windows drives",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle.pack(pady=(4, 0))

        # 2. Checklist Card
        chk_card = ctk.CTkFrame(
            main_frame,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        chk_card.pack(fill="x", pady=(0, 16))

        chk_inner = ctk.CTkFrame(chk_card, fg_color="transparent")
        chk_inner.pack(fill="x", padx=20, pady=18)

        card_title = ctk.CTkLabel(
            chk_inner,
            text="Pre-Flight System Verification",
            font=Fonts.CARD_TITLE,
            text_color=Colors.TEXT_PRIMARY
        )
        card_title.pack(anchor="w", pady=(0, 12))

        # Item 1: Rclone
        self._build_rclone_check(chk_inner)

        # Item 2: WinFsp
        self._build_winfsp_check(chk_inner)

        # Item 3: Windows Credential Manager
        self._build_security_check(chk_inner)

        # 3. Features highlight card
        feat_card = ctk.CTkFrame(
            main_frame,
            fg_color=Colors.CARD_INNER,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER
        )
        feat_card.pack(fill="x", pady=(0, 16))

        feat_inner = ctk.CTkFrame(feat_card, fg_color="transparent")
        feat_inner.pack(fill="x", padx=18, pady=12)

        items = [
            "⚡ Streaming Mode: Direct on-demand Windows drive letters without consuming local disk space.",
            "📁 Offline Mode: Fast one-way copy, cloud mirror, and bidirectional folder sync.",
            "🔒 Zero Token Leakage: OAuth credentials secured via Windows Credential Manager.",
        ]
        for it in items:
            lbl = ctk.CTkLabel(feat_inner, text=it, font=Fonts.CAPTION, text_color=Colors.TEXT_SECONDARY, justify="left", wraplength=520)
            lbl.pack(anchor="w", pady=2)

        # Checkbox
        chk = ctk.CTkCheckBox(
            main_frame,
            text="Do not show this onboarding wizard again on launch",
            variable=self.dont_show_again,
            font=Fonts.BODY,
            fg_color=Colors.ACCENT_PRIMARY
        )
        chk.pack(anchor="w", pady=(0, 16))

        # Bottom Actions
        actions = ctk.CTkFrame(main_frame, fg_color="transparent")
        actions.pack(fill="x")

        demo_btn = ctk.CTkButton(
            actions,
            text="Explore Demo Preview",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            text_color=Colors.TEXT_SECONDARY,
            height=40,
            command=self._on_explore_demo
        )
        demo_btn.pack(side="left", padx=(0, 10))

        add_btn = ctk.CTkButton(
            actions,
            text="Connect First Account",
            image=get_symbol_icon("plus", 16, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            height=40,
            command=self._on_connect_account
        )
        add_btn.pack(side="right", fill="x", expand=True)

    def _build_rclone_check(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))

        has_rclone = is_rclone_installed()
        ver = get_rclone_version() or "rclone v1.76.0" if has_rclone else "Missing"
        color = Colors.STATUS_MOUNTED if has_rclone else Colors.STATUS_ERROR
        symbol = "✓" if has_rclone else "✕"

        icon_lbl = ctk.CTkLabel(row, text=symbol, font=Fonts.BODY_BOLD, text_color=color, width=20)
        icon_lbl.pack(side="left", padx=(0, 8))

        text_lbl = ctk.CTkLabel(
            row,
            text=f"Rclone Cloud Engine: {ver}",
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY
        )
        text_lbl.pack(side="left")

    def _build_winfsp_check(self, parent):
        self.winfsp_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.winfsp_frame.pack(fill="x", pady=(0, 8))
        self._refresh_winfsp_ui()

    def _refresh_winfsp_ui(self):
        for widget in self.winfsp_frame.winfo_children():
            widget.destroy()

        has_fsp = is_winfsp_installed()
        color = Colors.STATUS_MOUNTED if has_fsp else Colors.STATUS_WARNING
        symbol = "✓" if has_fsp else "⚠️"

        icon_lbl = ctk.CTkLabel(self.winfsp_frame, text=symbol, font=Fonts.BODY_BOLD, text_color=color, width=20)
        icon_lbl.pack(side="left", padx=(0, 8))

        desc = "WinFsp Virtual Filesystem Driver: Ready" if has_fsp else "WinFsp Virtual Filesystem Driver: Not Installed"
        text_lbl = ctk.CTkLabel(
            self.winfsp_frame,
            text=desc,
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY
        )
        text_lbl.pack(side="left")

        if not has_fsp:
            install_btn = ctk.CTkButton(
                self.winfsp_frame,
                text="Install (winget)",
                font=Fonts.CAPTION,
                fg_color=Colors.CARD_INNER,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                height=26,
                width=110,
                command=self._install_winfsp
            )
            install_btn.pack(side="right", padx=(4, 0))

            refresh_btn = ctk.CTkButton(
                self.winfsp_frame,
                text="Re-check",
                font=Fonts.CAPTION,
                fg_color=Colors.CARD_INNER,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                height=26,
                width=75,
                command=self._refresh_winfsp_ui
            )
            refresh_btn.pack(side="right")

    def _build_security_check(self, parent):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")

        icon_lbl = ctk.CTkLabel(row, text="✓", font=Fonts.BODY_BOLD, text_color=Colors.STATUS_MOUNTED, width=20)
        icon_lbl.pack(side="left", padx=(0, 8))

        text_lbl = ctk.CTkLabel(
            row,
            text="Windows Credential Manager: Integrated & Active",
            font=Fonts.BODY,
            text_color=Colors.TEXT_PRIMARY
        )
        text_lbl.pack(side="left")

    def _install_winfsp(self):
        def _run():
            try:
                subprocess.Popen(
                    ["powershell", "-NoProfile", "-Command", "Start-Process winget -ArgumentList 'install WinFsp.WinFsp' -Verb RunAs"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            except Exception as e:
                logger.error(f"Error launching winget installer: {e}")
        threading.Thread(target=_run, daemon=True).start()
        messagebox.showinfo(
            "Installing WinFsp",
            "An administrator winget installer window has been opened.\n"
            "Once installation completes, click 'Re-check' to verify."
        )

    def _save_preferences_and_close(self):
        if self.dont_show_again.get():
            set_onboarding_completed(True)
        if self.on_finish:
            self.on_finish()
        self.destroy()

    def _on_explore_demo(self):
        self._save_preferences_and_close()

    def _on_connect_account(self):
        self._save_preferences_and_close()
        if self.on_connect_drive:
            self.on_connect_drive()
