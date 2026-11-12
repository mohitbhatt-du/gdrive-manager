"""Reusable modern dark-themed modal confirmation dialog."""

from collections.abc import Callable

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts


class ConfirmationDialog(ctk.CTkToplevel):
    """Modern modal dialog for confirming critical or destructive actions."""

    def __init__(
        self,
        master,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        is_destructive: bool = False,
        on_confirm: Callable[[], None] | None = None,
        on_cancel: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.title(title)
        self.geometry("440x220")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG_MAIN)

        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        # Modal behavior
        self.transient(master)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = master.winfo_x() + (master.winfo_width() // 2) - 220
            y = master.winfo_y() + (master.winfo_height() // 2) - 110
            self.geometry(f"+{x}+{y}")
        except Exception:
            pass

        self._build_ui(title, message, confirm_text, cancel_text, is_destructive)

    def _build_ui(self, title: str, message: str, confirm_text: str, cancel_text: str, is_destructive: bool):
        container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        container.pack(fill="both", expand=True, padx=16, pady=16)

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        t_lbl = ctk.CTkLabel(inner, text=title, font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY)
        t_lbl.pack(anchor="w")

        m_lbl = ctk.CTkLabel(
            inner,
            text=message,
            font=Fonts.BODY,
            text_color=Colors.TEXT_SECONDARY,
            wraplength=360,
            justify="left",
        )
        m_lbl.pack(anchor="w", pady=(8, 20))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(fill="x")

        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_row,
            text=cancel_text,
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=36,
            width=100,
            command=self._handle_cancel,
        )
        cancel_btn.pack(side="right")

        # Confirm button
        btn_fg = Colors.STATUS_ERROR if is_destructive else Colors.ACCENT_PRIMARY
        btn_hover = "#DC2626" if is_destructive else Colors.ACCENT_HOVER

        confirm_btn = ctk.CTkButton(
            btn_row,
            text=confirm_text,
            font=Fonts.BUTTON,
            fg_color=btn_fg,
            hover_color=btn_hover,
            height=36,
            width=110,
            command=self._handle_confirm,
        )
        confirm_btn.pack(side="right", padx=(0, 10))

    def _handle_confirm(self):
        self.destroy()
        if self.on_confirm:
            self.on_confirm()

    def _handle_cancel(self):
        self.destroy()
        if self.on_cancel:
            self.on_cancel()
