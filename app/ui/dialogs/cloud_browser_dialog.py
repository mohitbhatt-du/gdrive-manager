"""In-app Cloud File and Directory Browser dialog.

Enables exploring Google Drive folders, subdirectories, and 'Shared with me' files
directly inside GDrive Manager without requiring WinFsp driver or Windows drive letter mounting.
"""

import threading
import webbrowser
from collections.abc import Callable
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.models.account import Account
from app.services.rclone_service import RcloneService
from app.ui.assets import get_gdrive_icon, get_symbol_icon
from app.utils.logger import get_logger

logger = get_logger("CloudBrowserDialog")


class CloudBrowserDialog(ctk.CTkToplevel):
    """Modal cloud file explorer supporting remote navigation and shared files."""

    def __init__(
        self,
        master,
        account: Account,
        rclone_service: RcloneService,
        all_accounts: list[Account] | None = None,
        on_refresh: Callable[[], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.account = account
        self.rclone_service = rclone_service
        self.all_accounts = all_accounts or [account]
        self.on_refresh = on_refresh

        self.current_path: str = ""
        self.history: list[str] = []
        self.items: list[dict] = []
        self.selected_item: dict | None = None
        self.selected_widget: ctk.CTkFrame | None = None

        self.title(f"Cloud Browser - {account.display_name} ({account.drive_letter})")
        self.geometry("880x680")
        self.minsize(720, 520)
        self.configure(fg_color=Colors.BG_MAIN)

        self.transient(master)
        self.grab_set()

        self._build_ui()

        # Center on master
        self.update_idletasks()
        try:
            x = master.winfo_x() + (master.winfo_width() // 2) - 440
            y = master.winfo_y() + (master.winfo_height() // 2) - 340
            self.geometry(f"+{max(20, x)}+{max(20, y)}")
        except Exception:
            pass

        # Load initial root directory
        self._load_current_directory()

    def _build_ui(self):
        container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        container.pack(fill="both", expand=True, padx=16, pady=16)

        inner = ctk.CTkFrame(container, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=18, pady=16)

        # 1. Header Row
        head_row = ctk.CTkFrame(inner, fg_color="transparent")
        head_row.pack(fill="x", pady=(0, 14))

        icon_lbl = ctk.CTkLabel(head_row, text="", image=get_gdrive_icon(32))
        icon_lbl.pack(side="left", padx=(0, 10))

        title_box = ctk.CTkFrame(head_row, fg_color="transparent")
        title_box.pack(side="left")

        title_lbl = ctk.CTkLabel(
            title_box, text="Cloud File Browser", font=Fonts.CARD_TITLE, text_color=Colors.TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        sub_text = (
            f"Exploring {self.account.display_name} ({self.account.drive_letter}) • No WinFsp mount required"
        )
        self.sub_lbl = ctk.CTkLabel(
            title_box, text=sub_text, font=Fonts.CAPTION, text_color=Colors.TEXT_SECONDARY
        )
        self.sub_lbl.pack(anchor="w")

        # Top Right Badges & Account Selector
        right_box = ctk.CTkFrame(head_row, fg_color="transparent")
        right_box.pack(side="right")

        if len(self.all_accounts) > 1:
            names = [f"{a.display_name} ({a.drive_letter})" for a in self.all_accounts]
            current_name = f"{self.account.display_name} ({self.account.drive_letter})"
            self.acc_combo = ctk.CTkComboBox(
                right_box,
                values=names,
                width=220,
                height=30,
                font=Fonts.CAPTION,
                command=self._on_account_switched,
            )
            self.acc_combo.set(current_name)
            self.acc_combo.pack(side="right", padx=(8, 0))

        direct_badge = ctk.CTkLabel(
            right_box,
            text=" DIRECT CLOUD ACCESS ",
            font=Fonts.BADGE,
            text_color=Colors.ACCENT_CYAN,
            fg_color=Colors.INPUT_BG,
            corner_radius=6,
            height=26,
        )
        direct_badge.pack(side="right")

        # 2. Navigation & Toolbar Row
        nav_bar = ctk.CTkFrame(
            inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS, height=44
        )
        nav_bar.pack(fill="x", pady=(0, 10))

        # Nav Buttons (Back, Up, Refresh)
        self.back_btn = ctk.CTkButton(
            nav_bar,
            text="",
            image=get_symbol_icon("close", 12, Colors.TEXT_PRIMARY),
            width=32,
            height=30,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            corner_radius=6,
            command=self._go_back,
        )
        self.back_btn.pack(side="left", padx=(8, 4), pady=7)

        self.up_btn = ctk.CTkButton(
            nav_bar,
            text="",
            image=get_symbol_icon("arrow_up", 14, Colors.TEXT_PRIMARY),
            width=32,
            height=30,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            corner_radius=6,
            command=self._go_up_directory,
        )
        self.up_btn.pack(side="left", padx=(0, 4), pady=7)

        self.refresh_btn = ctk.CTkButton(
            nav_bar,
            text="",
            image=get_symbol_icon("refresh", 14, Colors.TEXT_PRIMARY),
            width=32,
            height=30,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            corner_radius=6,
            command=self._load_current_directory,
        )
        self.refresh_btn.pack(side="left", padx=(0, 8), pady=7)

        # Path display box
        path_box = ctk.CTkFrame(nav_bar, fg_color=Colors.INPUT_BG, corner_radius=6, height=30)
        path_box.pack(side="left", fill="x", expand=True, padx=(0, 8), pady=7)

        path_icon = ctk.CTkLabel(path_box, text="", image=get_symbol_icon("folder", 12, Colors.ACCENT_LIGHT))
        path_icon.pack(side="left", padx=(8, 4))

        self.path_lbl = ctk.CTkLabel(
            path_box, text="/", font=Fonts.BODY, text_color=Colors.TEXT_PRIMARY, anchor="w"
        )
        self.path_lbl.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # Search filter
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_items())
        search_entry = ctk.CTkEntry(
            nav_bar,
            textvariable=self.search_var,
            placeholder_text="Filter files...",
            font=Fonts.CAPTION,
            width=140,
            height=30,
            corner_radius=6,
            fg_color=Colors.INPUT_BG,
            border_color=Colors.CARD_BORDER,
        )
        search_entry.pack(side="right", padx=(0, 8), pady=7)

        # "Shared with me" Toggle
        self.shared_var = ctk.BooleanVar(value=False)
        self.shared_switch = ctk.CTkSwitch(
            nav_bar,
            text="Shared with Me",
            variable=self.shared_var,
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_PRIMARY,
            progress_color=Colors.ACCENT_PRIMARY,
            command=self._on_toggle_shared,
        )
        self.shared_switch.pack(side="right", padx=(8, 12), pady=7)

        # 3. File List Header Table Row
        header_table = ctk.CTkFrame(inner, fg_color=Colors.CARD_INNER, height=32, corner_radius=6)
        header_table.pack(fill="x", pady=(0, 4))

        # Columns
        name_hdr = ctk.CTkLabel(
            header_table, text="  NAME", font=Fonts.BADGE, text_color=Colors.TEXT_MUTED, anchor="w"
        )
        name_hdr.pack(side="left", fill="x", expand=True, padx=(12, 0))

        size_hdr = ctk.CTkLabel(
            header_table, text="SIZE", font=Fonts.BADGE, text_color=Colors.TEXT_MUTED, width=100, anchor="e"
        )
        size_hdr.pack(side="left", padx=(0, 16))

        type_hdr = ctk.CTkLabel(
            header_table, text="TYPE", font=Fonts.BADGE, text_color=Colors.TEXT_MUTED, width=120, anchor="w"
        )
        type_hdr.pack(side="left", padx=(0, 16))

        mod_hdr = ctk.CTkLabel(
            header_table,
            text="MODIFIED",
            font=Fonts.BADGE,
            text_color=Colors.TEXT_MUTED,
            width=140,
            anchor="w",
        )
        mod_hdr.pack(side="right", padx=(0, 16))

        # 4. Scrollable Files & Directories Container
        self.scroll_list = ctk.CTkScrollableFrame(
            inner,
            fg_color="transparent",
            scrollbar_button_color=Colors.CARD_BORDER,
            scrollbar_button_hover_color=Colors.ACCENT_PRIMARY,
        )
        self.scroll_list.pack(fill="both", expand=True, pady=(0, 12))

        # 5. Bottom Action & Status Footer
        foot_bar = ctk.CTkFrame(
            inner, fg_color=Colors.CARD_INNER, corner_radius=Dimensions.CARD_CORNER_RADIUS, height=48
        )
        foot_bar.pack(fill="x")

        self.status_lbl = ctk.CTkLabel(
            foot_bar,
            text="Ready.",
            font=Fonts.CAPTION,
            text_color=Colors.TEXT_MUTED,
            anchor="w",
        )
        self.status_lbl.pack(side="left", padx=16, pady=10)

        # Action Buttons
        close_btn = ctk.CTkButton(
            foot_bar,
            text="Close",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            command=self.destroy,
        )
        close_btn.pack(side="right", padx=(0, 12), pady=8)

        self.web_btn = ctk.CTkButton(
            foot_bar,
            text="Open in Web",
            image=get_symbol_icon("open", 13, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_BG,
            hover_color=Colors.CARD_HOVER,
            border_width=1,
            border_color=Colors.CARD_BORDER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            command=self._open_in_web_browser,
        )
        self.web_btn.pack(side="right", padx=(0, 8), pady=8)

        self.download_btn = ctk.CTkButton(
            foot_bar,
            text="Download File",
            image=get_symbol_icon("download", 13, Colors.TEXT_PRIMARY),
            compound="left",
            font=Fonts.BUTTON,
            fg_color=Colors.ACCENT_PRIMARY,
            hover_color=Colors.ACCENT_HOVER,
            corner_radius=Dimensions.BUTTON_CORNER_RADIUS,
            height=32,
            state="disabled",
            command=self._handle_download,
        )
        self.download_btn.pack(side="right", padx=(0, 8), pady=8)

    def _on_account_switched(self, choice: str):
        for acc in self.all_accounts:
            if f"{acc.display_name} ({acc.drive_letter})" == choice:
                self.account = acc
                self.title(f"Cloud Browser - {acc.display_name} ({acc.drive_letter})")
                self.sub_lbl.configure(
                    text=f"Exploring {acc.display_name} ({acc.drive_letter}) • No WinFsp mount required"
                )
                self.current_path = ""
                self.history.clear()
                self._load_current_directory()
                break

    def _on_toggle_shared(self):
        # When toggling "Shared with me", reset path to root
        self.current_path = ""
        self.history.clear()
        self._load_current_directory()

    def _go_back(self):
        if self.history:
            prev = self.history.pop()
            self.current_path = prev
            self._load_current_directory(record_history=False)

    def _go_up_directory(self):
        if not self.current_path:
            return
        parts = self.current_path.rstrip("/").split("/")
        if len(parts) <= 1:
            self._navigate_to("")
        else:
            self._navigate_to("/".join(parts[:-1]))

    def _navigate_to(self, target_path: str):
        clean = target_path.strip("/").replace("\\", "/")
        if clean != self.current_path:
            self.history.append(self.current_path)
            self.current_path = clean
            self._load_current_directory(record_history=False)

    def _load_current_directory(self, record_history: bool = True):
        # Update path display
        display_path = "/" + self.current_path if self.current_path else "/"
        if self.shared_var.get():
            display_path = f"[Shared with Me] {display_path}"
        self.path_lbl.configure(text=display_path)

        # Clear selection
        self.selected_item = None
        self.selected_widget = None
        self.download_btn.configure(state="disabled")

        # Disable navigation while loading
        self.status_lbl.configure(text="Querying remote Google Drive...", text_color=Colors.ACCENT_CYAN)
        self.refresh_btn.configure(state="disabled")

        # Clear rows
        for w in self.scroll_list.winfo_children():
            w.destroy()

        # Loading placeholder
        load_lbl = ctk.CTkLabel(
            self.scroll_list,
            text="Fetching cloud files...",
            font=Fonts.BODY,
            text_color=Colors.TEXT_MUTED,
        )
        load_lbl.pack(pady=40)

        # Run query in worker thread to prevent GUI freezing
        def _worker():
            try:
                items = self.rclone_service.list_directory(
                    remote_name=self.account.remote_name,
                    remote_path=self.current_path,
                    shared_with_me=self.shared_var.get(),
                )
            except Exception as e:
                logger.error(f"Error querying cloud directory: {e}")
                items = []

            def _ui():
                if not self.winfo_exists():
                    return
                self.items = items
                self.refresh_btn.configure(state="normal")
                self._render_items(self.items)

            try:
                if self.winfo_exists():
                    self.after(0, _ui)
            except Exception:
                pass

        threading.Thread(target=_worker, daemon=True).start()

    def _filter_items(self):
        query = self.search_var.get().strip().lower()
        if not query:
            self._render_items(self.items)
            return

        filtered = [item for item in self.items if query in str(item.get("Name", "")).lower()]
        self._render_items(filtered)

    def _render_items(self, items: list[dict]):
        for w in self.scroll_list.winfo_children():
            w.destroy()

        if not items:
            empty_msg = (
                "No files or folders found."
                if not self.shared_var.get()
                else "No files or folders have been shared with this Google account yet."
            )
            empty_lbl = ctk.CTkLabel(
                self.scroll_list,
                text=empty_msg,
                font=Fonts.SUBTITLE,
                text_color=Colors.TEXT_MUTED,
            )
            empty_lbl.pack(pady=40)
            self.status_lbl.configure(text="Folder is empty.", text_color=Colors.TEXT_MUTED)
            return

        folder_count = sum(1 for it in items if it.get("IsDir", False))
        file_count = len(items) - folder_count
        self.status_lbl.configure(
            text=f"{len(items)} items ({folder_count} folders, {file_count} files)",
            text_color=Colors.TEXT_MUTED,
        )

        for item in items:
            self._build_item_row(item)

    def _build_item_row(self, item: dict):
        is_dir = item.get("IsDir", False)
        name = item.get("Name", "Unknown")
        size = item.get("Size", -1)
        mod_time = item.get("ModTime", "")

        row = ctk.CTkFrame(
            self.scroll_list,
            fg_color=Colors.CARD_BG,
            corner_radius=6,
            height=36,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        row.pack(fill="x", pady=2)

        # Icon + Name
        icon_name = "folder" if is_dir else "file"
        icon_color = Colors.ACCENT_LIGHT if is_dir else Colors.TEXT_SECONDARY
        ico = ctk.CTkLabel(row, text="", image=get_symbol_icon(icon_name, 14, icon_color))
        ico.pack(side="left", padx=(10, 8), pady=6)

        name_color = Colors.TEXT_PRIMARY if not is_dir else Colors.ACCENT_LIGHT
        name_lbl = ctk.CTkLabel(row, text=name, font=Fonts.BODY, text_color=name_color, anchor="w")
        name_lbl.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # Size
        size_str = "-" if is_dir else Account.format_bytes(max(0, size))
        size_lbl = ctk.CTkLabel(
            row, text=size_str, font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED, width=100, anchor="e"
        )
        size_lbl.pack(side="left", padx=(0, 16))

        # Type
        type_str = "Folder" if is_dir else Path(name).suffix.upper().lstrip(".") or "File"
        type_lbl = ctk.CTkLabel(
            row, text=type_str, font=Fonts.CAPTION, text_color=Colors.TEXT_SECONDARY, width=120, anchor="w"
        )
        type_lbl.pack(side="left", padx=(0, 16))

        # Modified Date
        date_str = mod_time[:10] if len(mod_time) >= 10 else "-"
        mod_lbl = ctk.CTkLabel(
            row, text=date_str, font=Fonts.CAPTION, text_color=Colors.TEXT_MUTED, width=140, anchor="w"
        )
        mod_lbl.pack(side="right", padx=(0, 16))

        # Bind click and double click
        def _on_click(event=None):
            self._select_item(item, row)

        def _on_double_click(event=None):
            if is_dir:
                sub_path = f"{self.current_path}/{name}" if self.current_path else name
                self._navigate_to(sub_path)
            else:
                self._handle_download()

        for w in [row, ico, name_lbl, size_lbl, type_lbl, mod_lbl]:
            w.bind("<Button-1>", _on_click)
            w.bind("<Double-Button-1>", _on_double_click)

    def _select_item(self, item: dict, widget: ctk.CTkFrame):
        if self.selected_widget and self.selected_widget.winfo_exists():
            self.selected_widget.configure(fg_color=Colors.CARD_BG, border_color=Colors.CARD_BORDER)

        self.selected_item = item
        self.selected_widget = widget
        widget.configure(fg_color=Colors.CARD_HOVER, border_color=Colors.ACCENT_PRIMARY)

        is_dir = item.get("IsDir", False)
        name = item.get("Name", "")
        if is_dir:
            self.download_btn.configure(state="disabled")
            self.status_lbl.configure(
                text=f"Selected folder: {name} (Double-click to open)", text_color=Colors.TEXT_PRIMARY
            )
        else:
            self.download_btn.configure(state="normal")
            size_fmt = Account.format_bytes(max(0, item.get("Size", 0)))
            self.status_lbl.configure(
                text=f"Selected file: {name} ({size_fmt})", text_color=Colors.TEXT_PRIMARY
            )

    def _handle_download(self):
        if not self.selected_item or self.selected_item.get("IsDir", False):
            return

        file_name = self.selected_item.get("Name", "downloaded_file")
        ext = Path(file_name).suffix
        save_path = filedialog.asksaveasfilename(
            parent=self,
            title=f"Save '{file_name}' to Local Drive",
            initialfile=file_name,
            filetypes=[(f"{ext} files", f"*{ext}"), ("All files", "*.*")] if ext else [("All files", "*.*")],
        )

        if not save_path:
            return

        remote_path = f"{self.current_path}/{file_name}" if self.current_path else file_name
        self.download_btn.configure(state="disabled")
        self.status_lbl.configure(text=f"Downloading {file_name}...", text_color=Colors.ACCENT_CYAN)

        def _worker():
            ok = self.rclone_service.download_file(
                remote_name=self.account.remote_name,
                remote_path=remote_path,
                local_dest=save_path,
            )

            def _ui():
                self.download_btn.configure(state="normal")
                if ok:
                    self.status_lbl.configure(
                        text=f"Downloaded successfully: {file_name}", text_color=Colors.STATUS_MOUNTED
                    )
                    messagebox.showinfo(
                        "Download Complete",
                        f"File successfully downloaded to:\n{save_path}",
                        parent=self,
                    )
                else:
                    self.status_lbl.configure(
                        text=f"Download failed for {file_name}", text_color=Colors.STATUS_WARNING
                    )
                    messagebox.showerror(
                        "Download Error",
                        f"Failed to download '{file_name}'. Check logs for details.",
                        parent=self,
                    )

            self.after(0, _ui)

        threading.Thread(target=_worker, daemon=True).start()

    def _open_in_web_browser(self):
        """Open the current folder or account in Google Drive web client."""
        url = "https://drive.google.com"
        if self.shared_var.get():
            url = "https://drive.google.com/drive/shared-with-me"
        elif self.selected_item and self.selected_item.get("ID"):
            url = f"https://drive.google.com/open?id={self.selected_item['ID']}"
        webbrowser.open(url)
