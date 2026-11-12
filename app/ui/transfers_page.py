"""Transfers page displaying real-time upload, download, and synchronization progress."""

from collections.abc import Callable

import customtkinter as ctk

from app.config.theme import Colors, Dimensions, Fonts
from app.models.transfer_job import TransferJob, get_sample_transfers


class TransfersPage(ctk.CTkFrame):
    """View dedicated to managing transfer queues, active streams, and job histories."""

    def __init__(
        self,
        master,
        jobs: list[TransferJob] | None = None,
        on_pause_job: Callable[[TransferJob], None] | None = None,
        on_resume_job: Callable[[TransferJob], None] | None = None,
        on_cancel_job: Callable[[TransferJob], None] | None = None,
        on_retry_job: Callable[[TransferJob], None] | None = None,
        **kwargs,
    ):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.jobs = jobs if jobs is not None else get_sample_transfers()
        self.on_pause_job = on_pause_job
        self.on_resume_job = on_resume_job
        self.on_cancel_job = on_cancel_job
        self.on_retry_job = on_retry_job

        self.filter_var = ctk.StringVar(value="All Transfers")

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(24, 16))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(
            title_box, text="Transfer Queue", font=Fonts.HERO, text_color=Colors.TEXT_PRIMARY
        )
        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_box,
            text="Active downloads, uploads, and synchronization tasks with real-time transfer telemetry",
            font=Fonts.SUBTITLE,
            text_color=Colors.TEXT_SECONDARY,
        )
        subtitle.pack(anchor="w", pady=(2, 0))

        # Filter Segmented Button
        filter_seg = ctk.CTkSegmentedButton(
            header,
            values=["All Transfers", "Active", "Completed", "Failed / Paused"],
            variable=self.filter_var,
            command=self._on_filter_changed,
            font=Fonts.BUTTON,
            fg_color=Colors.CARD_BG,
            selected_color=Colors.ACCENT_PRIMARY,
            selected_hover_color=Colors.ACCENT_HOVER,
            unselected_color=Colors.CARD_INNER,
            unselected_hover_color=Colors.CARD_HOVER,
            height=34,
        )
        filter_seg.pack(side="right")

        # Jobs Container
        container = ctk.CTkFrame(
            self,
            fg_color=Colors.CARD_BG,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        container.pack(fill="both", expand=True, padx=28, pady=(0, 20))

        self.jobs_scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        self.jobs_scroll.pack(fill="both", expand=True, padx=12, pady=12)

        self.render_jobs()

    def _on_filter_changed(self, _=None):
        self.render_jobs()

    def update_jobs(self, jobs: list[TransferJob]):
        """Update job list and refresh display."""
        self.jobs = jobs
        self.render_jobs()

    def render_jobs(self):
        for w in self.jobs_scroll.winfo_children():
            w.destroy()

        mode = self.filter_var.get()
        filtered = []
        for j in self.jobs:
            if mode == "All Transfers":
                filtered.append(j)
            elif mode == "Active" and j.status in ("Running", "Queued"):
                filtered.append(j)
            elif mode == "Completed" and j.status == "Completed":
                filtered.append(j)
            elif mode == "Failed / Paused" and j.status in ("Failed", "Paused", "Cancelled"):
                filtered.append(j)

        if not filtered:
            empty_lbl = ctk.CTkLabel(
                self.jobs_scroll,
                text="No transfer jobs match the selected filter.",
                font=Fonts.SUBTITLE,
                text_color=Colors.TEXT_MUTED,
            )
            empty_lbl.pack(pady=40)
            return

        for job in filtered:
            self._render_job_card(job)

    def _render_job_card(self, job: TransferJob):
        card = ctk.CTkFrame(
            self.jobs_scroll,
            fg_color=Colors.CARD_INNER,
            corner_radius=Dimensions.CARD_CORNER_RADIUS,
            border_width=1,
            border_color=Colors.CARD_BORDER,
        )
        card.pack(fill="x", pady=6)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=16, pady=12)

        # Top row: Item Name, Operation Pill, Status Pill
        top_row = ctk.CTkFrame(inner, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 6))

        name_lbl = ctk.CTkLabel(
            top_row, text=job.item_name, font=Fonts.BODY_BOLD, text_color=Colors.TEXT_PRIMARY
        )
        name_lbl.pack(side="left")

        # Status badge color
        st_colors = {
            "Running": Colors.STATUS_SYNCING,
            "Completed": Colors.STATUS_MOUNTED,
            "Paused": Colors.STATUS_WARNING,
            "Failed": Colors.STATUS_ERROR,
            "Cancelled": Colors.STATUS_MUTED,
            "Queued": Colors.TEXT_SECONDARY,
        }
        st_color = st_colors.get(job.status, Colors.TEXT_SECONDARY)

        status_pill = ctk.CTkLabel(
            top_row,
            text=f"  ● {job.status.upper()}  ",
            font=Fonts.BADGE,
            text_color=st_color,
            fg_color=Colors.INPUT_BG,
            corner_radius=6,
            height=22,
        )
        status_pill.pack(side="right")

        op_pill = ctk.CTkLabel(
            top_row,
            text=f" {job.operation_type} ",
            font=Fonts.BADGE,
            text_color=Colors.ACCENT_LIGHT,
            fg_color=Colors.BG_SIDEBAR_ACTIVE,
            corner_radius=6,
            height=22,
        )
        op_pill.pack(side="right", padx=(0, 8))

        # Progress bar
        prog = ctk.CTkProgressBar(
            inner, height=6, corner_radius=3, fg_color=Colors.PROGRESS_BG, progress_color=st_color
        )
        prog.set(job.progress_percentage / 100.0)
        prog.pack(fill="x", pady=(4, 6))

        # Telemetry & Actions row
        bot_row = ctk.CTkFrame(inner, fg_color="transparent")
        bot_row.pack(fill="x")

        telemetry_txt = f"{job.account_name}  •  {job.formatted_transferred} / {job.formatted_total} ({job.progress_percentage:.1f}%)"
        if job.status == "Running":
            telemetry_txt += f"  •  Speed: {job.formatted_speed}  •  ETA: {job.formatted_eta}"
        elif job.status == "Failed" and job.error_message:
            telemetry_txt = f"{job.account_name}  •  Error: {job.error_message}"

        info_lbl = ctk.CTkLabel(
            bot_row,
            text=telemetry_txt,
            font=Fonts.CAPTION,
            text_color=Colors.STATUS_ERROR if job.status == "Failed" else Colors.TEXT_SECONDARY,
        )
        info_lbl.pack(side="left")

        # Action Buttons
        btn_box = ctk.CTkFrame(bot_row, fg_color="transparent")
        btn_box.pack(side="right")

        if job.status == "Running":
            p_btn = ctk.CTkButton(
                btn_box,
                text="Pause",
                font=Fonts.CAPTION,
                fg_color=Colors.CARD_BG,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                width=54,
                height=26,
                command=lambda j=job: self._handle_pause(j),
            )
            p_btn.pack(side="left", padx=(0, 6))

            c_btn = ctk.CTkButton(
                btn_box,
                text="Cancel",
                font=Fonts.CAPTION,
                fg_color=Colors.CARD_BG,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                width=54,
                height=26,
                command=lambda j=job: self._handle_cancel(j),
            )
            c_btn.pack(side="left")

        elif job.status == "Paused":
            r_btn = ctk.CTkButton(
                btn_box,
                text="Resume",
                font=Fonts.CAPTION,
                fg_color=Colors.ACCENT_PRIMARY,
                hover_color=Colors.ACCENT_HOVER,
                width=60,
                height=26,
                command=lambda j=job: self._handle_resume(j),
            )
            r_btn.pack(side="left", padx=(0, 6))

            c_btn = ctk.CTkButton(
                btn_box,
                text="Cancel",
                font=Fonts.CAPTION,
                fg_color=Colors.CARD_BG,
                hover_color=Colors.CARD_HOVER,
                border_width=1,
                border_color=Colors.CARD_BORDER,
                width=54,
                height=26,
                command=lambda j=job: self._handle_cancel(j),
            )
            c_btn.pack(side="left")

        elif job.status == "Failed":
            ret_btn = ctk.CTkButton(
                btn_box,
                text="Retry",
                font=Fonts.CAPTION,
                fg_color=Colors.ACCENT_PRIMARY,
                hover_color=Colors.ACCENT_HOVER,
                width=60,
                height=26,
                command=lambda j=job: self._handle_retry(j),
            )
            ret_btn.pack(side="left")

    def _handle_pause(self, job: TransferJob):
        job.status = "Paused"
        if self.on_pause_job:
            self.on_pause_job(job)
        self.render_jobs()

    def _handle_resume(self, job: TransferJob):
        job.status = "Running"
        if self.on_resume_job:
            self.on_resume_job(job)
        self.render_jobs()

    def _handle_cancel(self, job: TransferJob):
        job.status = "Cancelled"
        if self.on_cancel_job:
            self.on_cancel_job(job)
        self.render_jobs()

    def _handle_retry(self, job: TransferJob):
        job.status = "Running"
        if self.on_retry_job:
            self.on_retry_job(job)
        self.render_jobs()
