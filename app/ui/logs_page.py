"""Interactive in-app logs viewer and diagnostic report generator."""

import subprocess
from tkinter import messagebox

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.utils.paths import LOGS_DIR


class LogsPage(ctk.CTkFrame):
    """View dedicated to real-time application and rclone process logs."""

    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_file = LOGS_DIR / "app.log"
        self.filter_var = ctk.StringVar(value="All Levels")
        self.auto_scroll_var = ctk.BooleanVar(value=True)

        self._build_ui()
        self.refresh_logs()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(
            title_box, text="Diagnostics & Logs", font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Real-time execution diagnostics, rclone subprocess events, and mount telemetry",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Controls row
        ctrl_row = ctk.CTkFrame(header, fg_color="transparent")
        ctrl_row.pack(side="right")

        filter_menu = ctk.CTkOptionMenu(
            ctrl_row,
            values=["All Levels", "INFO", "WARNING", "ERROR", "DEBUG"],
            variable=self.filter_var,
            command=self._on_filter_changed,
            font=Fonts.BODY,
            fg_color=Colors.CARD_BG,
            button_color=Colors.ACCENT_PRIMARY,
            height=34,
            width=120,
        )
        filter_menu.pack(side="left", padx=(0, 8))

        refresh_btn = ctk.CTkButton(
            ctrl_row,
            text="Refresh",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=34,
            width=80,
            command=self.refresh_logs,
        )
        refresh_btn.pack(side="left", padx=(0, 8))

        open_file_btn = ctk.CTkButton(
            ctrl_row,
            text="Open in Notepad",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_INNER,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            height=34,
            width=130,
            command=self._open_in_notepad,
        )
        open_file_btn.pack(side="left")

        # Log Terminal Container
        term_card = ctk.CTkFrame(
            self,
            fg_color=Colors.INPUT_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        term_card.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        self.text_box = ctk.CTkTextbox(
            term_card,
            font=Fonts.CODE,
            text_color=Colors.TEXT_PRIMARY,
            fg_color="transparent",
            wrap="none",
            activate_scrollbars=True,
        )
        self.text_box.pack(fill="both", expand=True, padx=12, pady=12)

    def _on_filter_changed(self, _=None):
        self.refresh_logs()

    def refresh_logs(self):
        """Read log file and display filtered lines."""
        self.text_box.delete("1.0", "end")

        if not self.log_file.exists():
            self.text_box.insert("1.0", "[INFO] No log events recorded yet.\n")
            return

        try:
            with open(self.log_file, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            mode = self.filter_var.get()
            filtered = []
            for line in lines:
                if mode == "All Levels":
                    filtered.append(line)
                elif f"[{mode}]" in line:
                    filtered.append(line)

            content = "".join(filtered[-500:])  # Display latest 500 lines
            self.text_box.insert("1.0", content)
            self.text_box.see("end")
        except Exception as e:
            self.text_box.insert("1.0", f"Error reading log file: {e}\n")

    def _open_in_notepad(self):
        if self.log_file.exists():
            try:
                subprocess.Popen(["notepad.exe", str(self.log_file)])
            except Exception as e:
                messagebox.showerror("Error", f"Could not launch Notepad: {e}")
        else:
            messagebox.showinfo("Logs", "Log file does not exist yet.")
