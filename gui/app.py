import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, font as tkfont

from core.process import Process
from algorithms.fcfs import fcfs_scheduling
from algorithms.round_robin import round_robin_scheduling
from algorithms.sjf_np import sjf_non_preemptive
from algorithms.ljf_np import ljf_non_preemptive
from algorithms.priority_np import priority_non_preemptive
from algorithms.priority_p import priority_preemptive
from algorithms.srtf import srtf_scheduling
from .theme import Palette, configure_ttk_styles, build_widget_styles


class SchedulerApp:

    DISPLAY_FONT_CANDIDATES = ("Stencil", "Impact", "Segoe UI", "Helvetica")
    UI_FONT_CANDIDATES = ("Segoe UI", "Helvetica", "Arial", "TkDefaultFont")
    MONO_FONT_CANDIDATES = ("Consolas", "Menlo", "Courier New", "TkFixedFont")

    ALGORITHMS = [
        "FCFS",
        "SJF (Non Preemptive)",
        "LJF (Non Preemptive)",
        "Round Robin",
        "Priority (Non Preemptive)",
        "Priority (Preemptive)",
        "SRTF (Preemptive SJF)",
    ]
    DEMO_PROCESSES = [
        ("P1", 0, 3, 2),
        ("P2", 1, 6, 1),
        ("P3", 2, 1, 4),
        ("P4", 2, 2, 3),
    ]
    ALGORITHM_HELP = {
        "FCFS": "Runs processes in arrival order. Simple and fair, but long jobs can delay shorter ones.",
        "SJF (Non Preemptive)": "Selects the shortest available burst next. Low average waiting time, but once started a process runs to completion.",
        "LJF (Non Preemptive)": "Selects the longest available burst next. Useful mainly for comparison and academic analysis.",
        "Round Robin": "Executes each ready process for a fixed time quantum, then rotates. Good for time-sharing systems.",
        "Priority (Non Preemptive)": "Runs the highest-priority available process next. Lower numeric priority value is treated as higher priority.",
        "Priority (Preemptive)": "Always favors the highest-priority ready process, even if it must interrupt the current one.",
        "SRTF (Preemptive SJF)": "Runs the process with the shortest remaining time. It is the preemptive version of SJF.",
    }

    ALGORITHM_DISPATCH = {
        "FCFS": lambda procs, tq: fcfs_scheduling(procs),
        "SJF (Non Preemptive)": lambda procs, tq: sjf_non_preemptive(procs),
        "LJF (Non Preemptive)": lambda procs, tq: ljf_non_preemptive(procs),
        "Round Robin": lambda procs, tq: round_robin_scheduling(procs, tq),
        "Priority (Non Preemptive)": lambda procs, tq: priority_non_preemptive(procs),
        "Priority (Preemptive)": lambda procs, tq: priority_preemptive(procs),
        "SRTF (Preemptive SJF)": lambda procs, tq: srtf_scheduling(procs),
    }

    PROJECT_INFO = {
        "team_members": "Hemang Mistry and Pari Barot",
        "roll_numbers": "14885 & 15704",
        "course": "Python Programming",
        "semester": "Semester 4",
        "institution": "Institute Of Advanced Research",
    }

    PRESETS = {
        "Basic Example": {
            "description": "A simple 4-process workload for general testing.",
            "processes": [
                ("P1", 0, 3, 2),
                ("P2", 1, 6, 1),
                ("P3", 2, 1, 4),
                ("P4", 2, 2, 3),
            ],
        },
        "Convoy Effect (FCFS)": {
            "description": "One long process blocks many short ones. Try FCFS vs SJF — SJF wins big.",
            "processes": [
                ("P1", 0, 20, 1),
                ("P2", 1, 2, 1),
                ("P3", 2, 2, 1),
                ("P4", 3, 2, 1),
                ("P5", 4, 2, 1),
            ],
        },
        "Starvation (Priority)": {
            "description": "Low-priority process arrives first but keeps getting interrupted. Shows why preemptive priority can starve.",
            "processes": [
                ("P1", 0, 8, 5),
                ("P2", 1, 4, 1),
                ("P3", 2, 4, 1),
                ("P4", 3, 4, 1),
            ],
        },
        "Round Robin Advantage": {
            "description": "Mixed burst times where RR gives fairer response times than FCFS or SJF.",
            "processes": [
                ("P1", 0, 10, 3),
                ("P2", 1, 4, 2),
                ("P3", 2, 3, 1),
                ("P4", 3, 5, 4),
            ],
        },
        "SRTF Showcase": {
            "description": "New short processes keep arriving. SRTF preempts aggressively; SJF (non-preemptive) lags behind.",
            "processes": [
                ("P1", 0, 8, 2),
                ("P2", 1, 4, 1),
                ("P3", 2, 2, 3),
                ("P4", 3, 1, 4),
            ],
        },
        "Identical Arrivals": {
            "description": "All processes arrive at t=0. Pure burst-time comparison; SJF should dominate.",
            "processes": [
                ("P1", 0, 6, 3),
                ("P2", 0, 8, 1),
                ("P3", 0, 7, 4),
                ("P4", 0, 3, 2),
                ("P5", 0, 4, 5),
            ],
        },
    }

    def __init__(self, root):
        self.root = root
        self.root.title("OS Process Scheduler Simulator")
        self._apply_zoomed_state()

        self._resolve_fonts()

        self.processes = []
        self.selected_process_index = None
        self.last_result_rows = []
        self.last_comparison_rows = []
        self.last_metrics = {}
        self.last_timeline = []

        self._build_ui()

    def _build_ui(self):
        self.root.configure(bg=Palette.BG_APP)

        self._setup_styles()
        self._build_main_layout()
        self._build_processes_tab()
        self._build_simulation_tab()
        self._build_comparison_tab()
        self._build_footer()
        self._bind_shortcuts()

        self.refresh_process_tree()
        self.update_summary_cards()
        self.show_gantt_chart(self.last_timeline)

        if self.algo_var.get():
            self.update_quantum_state()
            self.algorithm_help_label.configure(
                text=self.ALGORITHM_HELP.get(self.get_selected_algorithm(), ""))

        if self.last_result_rows:
            self._repopulate_results()

        if self.last_comparison_rows:
            self._repopulate_comparison()

    def toggle_theme(self):
        new_theme = "light" if Palette.current_name() == "dark" else "dark"
        Palette.set_theme(new_theme)

        saved_algo = self.algo_var.get() if hasattr(self, "algo_var") else None
        saved_quantum = self.quantum_entry.get() if hasattr(self, "quantum_entry") else "3"

        for child in self.root.winfo_children():
            child.destroy()

        self._build_ui()

        if saved_algo:
            self.algo_var.set(saved_algo)
            self.algorithm_help_label.configure(
                text=self.ALGORITHM_HELP.get(saved_algo, ""))
        self.quantum_entry.delete(0, tk.END)
        self.quantum_entry.insert(0, saved_quantum)
        self.update_quantum_state()

    def show_help_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Help & About")
        dialog.configure(bg=Palette.BG_APP)
        dialog.geometry("680x640")
        dialog.transient(self.root)
        dialog.grab_set()

        container = tk.Frame(dialog, bg=Palette.BG_APP)
        container.pack(fill="both", expand=True, padx=24, pady=24)

        header = tk.Frame(container, bg=Palette.BG_APP)
        header.pack(fill="x", pady=(0, 18))
        tk.Label(
            header, text="Help & About",
            font=(self.DISPLAY_FONT, 18, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_APP,
        ).pack(anchor="w")
        tk.Label(
            header, text="Quick reference for algorithms, shortcuts, and project info.",
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_APP,
        ).pack(anchor="w", pady=(4, 0))

        body_canvas = tk.Canvas(
            container, bg=Palette.BG_APP, highlightthickness=0,
        )
        body_scroll = ttk.Scrollbar(
            container, orient="vertical", command=body_canvas.yview,
        )
        body = tk.Frame(body_canvas, bg=Palette.BG_APP)
        body_canvas.configure(yscrollcommand=body_scroll.set)
        body_canvas.pack(side="left", fill="both", expand=True)
        body_scroll.pack(side="right", fill="y")
        body_window = body_canvas.create_window((0, 0), window=body, anchor="nw")
        body.bind(
            "<Configure>",
            lambda _e: body_canvas.configure(scrollregion=body_canvas.bbox("all")),
        )
        body_canvas.bind(
            "<Configure>",
            lambda e: body_canvas.itemconfigure(body_window, width=e.width),
        )

        def on_wheel(event):
            if event.num == 4:
                body_canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                body_canvas.yview_scroll(1, "units")
            elif event.delta:
                body_canvas.yview_scroll(-1 if event.delta > 0 else 1, "units")

        body_canvas.bind("<Enter>", lambda _e: dialog.bind_all("<MouseWheel>", on_wheel))
        body_canvas.bind("<Leave>", lambda _e: dialog.unbind_all("<MouseWheel>"))

        self._help_section(body, "Scheduling Algorithms")
        for name, desc in self.ALGORITHM_HELP.items():
            self._help_row(body, name, desc, color=Palette.PRIMARY)

        self._help_section(body, "Key Formulas", top_pad=18)
        formulas = [
            ("Turnaround Time", "TAT = Completion Time − Arrival Time"),
            ("Waiting Time",    "WT = Turnaround Time − Burst Time"),
            ("Response Time",   "RT = Start Time − Arrival Time"),
            ("CPU Utilization", "Util = (Total Burst / Completion Time) × 100%"),
            ("Idle Time",       "Idle = Completion Time − Total Burst Time"),
        ]
        for label, formula in formulas:
            self._help_row(body, label, formula, color=Palette.ACCENT, mono=True)

        self._help_section(body, "Keyboard Shortcuts", top_pad=18)
        shortcuts = [
            ("Ctrl + N",        "Focus the Process ID field to start a new entry"),
            ("Ctrl + R / F5",   "Run the simulation with the current algorithm"),
            ("Ctrl + Shift + C","Compare all algorithms on the current workload"),
            ("Ctrl + E",        "Export the current results to CSV"),
            ("Esc",             "Cancel process edit mode"),
            ("Delete",          "Remove the selected process from the list"),
        ]
        for key, desc in shortcuts:
            self._help_row(body, key, desc, color=Palette.INFO, mono=True)

        self._help_section(body, "Project Information", top_pad=18)
        info = self.PROJECT_INFO
        self._help_row(body, "Team Members", info.get("team_members", "—"), color=Palette.SUCCESS)
        self._help_row(body, "Roll Numbers", info.get("roll_numbers", "—"), color=Palette.SUCCESS)
        self._help_row(body, "Course",       info.get("course", "—"),       color=Palette.SUCCESS)
        self._help_row(body, "Semester",     info.get("semester", "—"),     color=Palette.SUCCESS)
        self._help_row(body, "Institution",  info.get("institution", "—"),  color=Palette.SUCCESS)

        tk.Frame(body, bg=Palette.BG_APP, height=12).pack()

        footer = tk.Frame(container, bg=Palette.BG_APP)
        footer.pack(fill="x", pady=(16, 0))
        tk.Button(
            footer, text="Close",
            command=dialog.destroy, **self.button_style,
        ).pack(side="right")

        dialog.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - dialog.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{max(0, x)}+{max(0, y)}")

    def _help_section(self, parent, title, top_pad=0):
        if top_pad:
            tk.Frame(parent, bg=Palette.BG_APP, height=top_pad).pack()
        tk.Label(
            parent, text=title.upper(),
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_APP,
        ).pack(anchor="w", pady=(0, 8))

    def _help_row(self, parent, label, desc, color=None, mono=False):
        row = tk.Frame(
            parent, bg=Palette.BG_SURFACE,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        row.pack(fill="x", pady=(0, 6))
        if color:
            tk.Frame(row, bg=color, width=3).pack(side="left", fill="y")
        inner = tk.Frame(row, bg=Palette.BG_SURFACE)
        inner.pack(side="left", fill="x", expand=True, padx=14, pady=10)
        tk.Label(
            inner, text=label,
            font=(self.MONO_FONT if mono else self.UI_FONT, 10, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        tk.Label(
            inner, text=desc,
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_SECONDARY, bg=Palette.BG_SURFACE,
            wraplength=560, justify="left",
        ).pack(anchor="w", pady=(2, 0))

    def _repopulate_results(self):
        self.results_tree.delete(*self.results_tree.get_children())
        for row in self.last_result_rows:
            self.results_tree.insert(
                "", "end", values=row,
                tags=(self._next_row_tag(self.results_tree),))
        if self.last_metrics:
            m = self.last_metrics
            self.averages_label.configure(
                text=f"Average Waiting Time: {m['avg_wt']:.2f}    Average Turnaround Time: {m['avg_tat']:.2f}")
            self.performance_label.configure(
                text=f"Response Time Avg: {m['avg_rt']:.2f}    CPU Idle Time: {m['idle_time']}    "
                     f"CPU Utilization: {m['cpu_util']:.2f}%")
            self.update_summary_cards(
                f"{m['avg_wt']:.2f}", f"{m['avg_tat']:.2f}",
                str(m['idle_time']), f"{m['cpu_util']:.2f}%")

    def _repopulate_comparison(self):
        self.comparison_tree.delete(*self.comparison_tree.get_children())
        for row in self.last_comparison_rows:
            self.comparison_tree.insert(
                "", "end", values=row[:3],
                tags=(self._next_row_tag(self.comparison_tree),))
        if self.last_comparison_rows:
            best_row = min(self.last_comparison_rows, key=lambda r: (r[3], r[4], r[0]))
            self.best_algorithm_label.configure(
                text=f"{best_row[0]}   ·   Avg WT: {best_row[1]}   ·   Avg TAT: {best_row[2]}")
        self.highlight_selected_algorithm()


    def _apply_zoomed_state(self):
        try:
            self.root.state("zoomed")
        except tk.TclError:
            try:
                self.root.attributes("-zoomed", True)
            except tk.TclError:
                self.root.geometry("1400x900")

    def _resolve_fonts(self):
        available = set(tkfont.families())

        def pick(candidates):
            for name in candidates:
                if name in available or name.startswith("Tk"):
                    return name
            return "TkDefaultFont"

        self.DISPLAY_FONT = pick(self.DISPLAY_FONT_CANDIDATES)
        self.UI_FONT = pick(self.UI_FONT_CANDIDATES)
        self.MONO_FONT = pick(self.MONO_FONT_CANDIDATES)


    def _card(self, parent, **pack_kwargs):
        frame = tk.Frame(
            parent,
            bg=Palette.BG_SURFACE,
            highlightthickness=1,
            highlightbackground=Palette.BORDER,
            bd=0,
        )
        if pack_kwargs:
            frame.pack(**pack_kwargs)
        return frame

    def _section_title(self, parent, text, subtitle=None):
        tk.Label(
            parent, text=text,
            font=(self.DISPLAY_FONT, 14, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", padx=22, pady=(20, 2))
        if subtitle:
            tk.Label(
                parent, text=subtitle,
                font=(self.UI_FONT, 9),
                fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
            ).pack(anchor="w", padx=22, pady=(0, 14))
        else:
            tk.Frame(parent, bg=Palette.BG_SURFACE, height=6).pack()


    def _build_main_layout(self):
        self.main_frame = tk.Frame(self.root, bg=Palette.BG_APP)
        self.main_frame.pack(fill="both", expand=True)

        header_frame = tk.Frame(
            self.main_frame, bg=Palette.BG_SURFACE,
            highlightthickness=0,
        )
        header_frame.pack(fill="x")

        header_inner = tk.Frame(header_frame, bg=Palette.BG_SURFACE)
        header_inner.pack(fill="x", padx=32, pady=20)

        header_text = tk.Frame(header_inner, bg=Palette.BG_SURFACE)
        header_text.pack(side="left", fill="y")

        brand_row = tk.Frame(header_text, bg=Palette.BG_SURFACE)
        brand_row.pack(anchor="w")

        logo_box = tk.Frame(
            brand_row, bg=Palette.PRIMARY, width=32, height=32,
        )
        logo_box.pack(side="left")
        logo_box.pack_propagate(False)
        tk.Label(
            logo_box, text="⚙", font=(self.UI_FONT, 16, "bold"),
            fg=Palette.PRIMARY_TEXT, bg=Palette.PRIMARY,
        ).pack(expand=True)

        title_col = tk.Frame(brand_row, bg=Palette.BG_SURFACE)
        title_col.pack(side="left", padx=(14, 0))
        tk.Label(
            title_col, text="Process Scheduler",
            font=(self.DISPLAY_FONT, 16, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        tk.Label(
            title_col, text="Operating Systems Simulator",
            font=(self.UI_FONT, 9),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")

        header_right = tk.Frame(header_inner, bg=Palette.BG_SURFACE)
        header_right.pack(side="right", fill="y")

        self.status_pill = tk.Frame(
            header_right, bg=Palette.BG_SURFACE_2,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        self.status_pill.pack(side="left", padx=(0, 12))
        pill_inner = tk.Frame(self.status_pill, bg=Palette.BG_SURFACE_2)
        pill_inner.pack(padx=14, pady=8)
        self.status_dot = tk.Canvas(
            pill_inner, width=8, height=8, bg=Palette.BG_SURFACE_2,
            highlightthickness=0,
        )
        self.status_dot.pack(side="left", padx=(0, 8))
        self.status_dot.create_oval(1, 1, 7, 7, fill=Palette.TEXT_MUTED, outline="")
        self.header_process_count_label = tk.Label(
            pill_inner, text="0 processes",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.TEXT_SECONDARY, bg=Palette.BG_SURFACE_2,
        )
        self.header_process_count_label.pack(side="left")

        self.algo_pill = tk.Frame(
            header_right, bg=Palette.BG_SURFACE_2,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        self.algo_pill.pack(side="left", padx=(0, 12))
        algo_pill_inner = tk.Frame(self.algo_pill, bg=Palette.BG_SURFACE_2)
        algo_pill_inner.pack(padx=14, pady=8)
        tk.Label(
            algo_pill_inner, text="ALG",
            font=(self.UI_FONT, 8, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE_2,
        ).pack(side="left", padx=(0, 8))
        self.header_algorithm_label = tk.Label(
            algo_pill_inner, text="FCFS",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.PRIMARY, bg=Palette.BG_SURFACE_2,
        )
        self.header_algorithm_label.pack(side="left")

        theme_icon = "☀" if Palette.current_name() == "dark" else "☾"
        self.theme_toggle_btn = tk.Button(
            header_right, text=theme_icon,
            font=(self.UI_FONT, 12),
            bg=Palette.BG_SURFACE_2, fg=Palette.TEXT_SECONDARY,
            activebackground=Palette.GHOST_BG_HOVER,
            activeforeground=Palette.TEXT_PRIMARY,
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=6,
            highlightthickness=1,
            highlightbackground=Palette.BORDER_SOFT,
            command=self.toggle_theme,
        )
        self.theme_toggle_btn.pack(side="left")

        self.help_btn = tk.Button(
            header_right, text="?",
            font=(self.UI_FONT, 11, "bold"),
            bg=Palette.BG_SURFACE_2, fg=Palette.TEXT_SECONDARY,
            activebackground=Palette.GHOST_BG_HOVER,
            activeforeground=Palette.TEXT_PRIMARY,
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=6,
            highlightthickness=1,
            highlightbackground=Palette.BORDER_SOFT,
            command=self.show_help_dialog,
        )
        self.help_btn.pack(side="left", padx=(8, 0))

        separator = tk.Frame(self.main_frame, bg=Palette.BORDER_SOFT, height=1)
        separator.pack(fill="x")

        self.notebook = ttk.Notebook(self.main_frame, style="Scheduler.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=32, pady=(16, 16))

        self.processes_tab = tk.Frame(self.notebook, bg=Palette.BG_APP)
        self.simulation_tab = tk.Frame(self.notebook, bg=Palette.BG_APP)
        self.comparison_tab = tk.Frame(self.notebook, bg=Palette.BG_APP)

        self.notebook.add(self.processes_tab, text="  Processes  ")
        self.notebook.add(self.simulation_tab, text="  Simulation  ")
        self.notebook.add(self.comparison_tab, text="  Comparison  ")

        self.processes_page = self._make_scrollable_tab(self.processes_tab)
        self.simulation_page = self._make_scrollable_tab(self.simulation_tab)
        self.comparison_page = self._make_scrollable_tab(self.comparison_tab)

    def _build_processes_tab(self):

        input_card = self._card(self.processes_page)
        input_card.pack(fill="x", pady=(0, 16))

        self._section_title(
            input_card, "Add Process",
            "Fill in the fields below or load the sample workload to get started."
        )

        input_frame = tk.Frame(input_card, bg=Palette.BG_SURFACE)
        input_frame.pack(fill="x", padx=24, pady=(0, 20))

        fields = [
            ("Process ID", "pid_entry"),
            ("Arrival Time", "at_entry"),
            ("Burst Time", "bt_entry"),
            ("Priority", "pr_entry"),
        ]
        for col_index, (label, attr) in enumerate(fields):
            col_frame = tk.Frame(input_frame, bg=Palette.BG_SURFACE)
            col_frame.grid(row=0, column=col_index, sticky="ew", padx=(0, 14))
            tk.Label(
                col_frame, text=label,
                font=(self.UI_FONT, 9, "bold"),
                fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
            ).pack(anchor="w", pady=(0, 6))
            entry = tk.Entry(col_frame, **self.entry_style)
            entry.pack(fill="x", ipady=6)
            setattr(self, attr, entry)
            input_frame.grid_columnconfigure(col_index, weight=1)

        button_row = tk.Frame(input_card, bg=Palette.BG_SURFACE)
        button_row.pack(fill="x", padx=24, pady=(0, 22))

        self.add_update_button = tk.Button(
            button_row, text="+  Add Process",
            command=self.add_or_update_process, **self.button_style)
        self.add_update_button.pack(side="left")

        self.cancel_edit_button = tk.Button(
            button_row, text="Cancel",
            command=self.cancel_edit, **self.secondary_button_style)
        self.cancel_edit_button.pack(side="left", padx=(10, 0))
        self.cancel_edit_button.pack_forget()

        preset_frame = tk.Frame(button_row, bg=Palette.BG_SURFACE)
        preset_frame.pack(side="right")
        tk.Label(
            preset_frame, text="Load preset:",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(side="left", padx=(0, 8))
        self.preset_var = tk.StringVar()
        self.preset_dropdown = ttk.Combobox(
            preset_frame, textvariable=self.preset_var,
            values=list(self.PRESETS.keys()),
            state="readonly", width=28, style="Scheduler.TCombobox",
        )
        self.preset_dropdown.pack(side="left")
        self.preset_dropdown.bind("<<ComboboxSelected>>", self._on_preset_selected)

        for entry in (self.pid_entry, self.at_entry, self.bt_entry, self.pr_entry):
            entry.bind("<Return>", self.on_add_process_enter)


        table_outer = self._card(self.processes_page)
        table_outer.pack(fill="both", expand=True, pady=(0, 16))

        table_header = tk.Frame(table_outer, bg=Palette.BG_SURFACE)
        table_header.pack(fill="x", padx=24, pady=(20, 14))

        title_col = tk.Frame(table_header, bg=Palette.BG_SURFACE)
        title_col.pack(side="left")
        tk.Label(
            title_col, text="Queued Processes",
            font=(self.DISPLAY_FONT, 14, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        tk.Label(
            title_col, text="Click any row to edit its values.",
            font=(self.UI_FONT, 9),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(2, 0))

        table_actions = tk.Frame(table_header, bg=Palette.BG_SURFACE)
        table_actions.pack(side="right")

        tk.Button(
            table_actions, text="Delete Selected",
            command=self.delete_selected_process,
            **self.secondary_button_style,
        ).pack(side="left", padx=(0, 10))
        tk.Button(
            table_actions, text="Clear All",
            command=self.clear_all_processes,
            **self.danger_button_style,
        ).pack(side="left")

        table_frame = tk.Frame(table_outer, bg=Palette.BG_SURFACE)
        table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self.tree = ttk.Treeview(
            table_frame, columns=("PID", "AT", "BT", "PR"),
            show="headings", style="Scheduler.Treeview")
        for col, header in (("PID", "Process ID"), ("AT", "Arrival"),
                            ("BT", "Burst"), ("PR", "Priority")):
            self.tree.heading(col, text=header)
            self.tree.column(col, width=150, anchor="center")

        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=table_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        table_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self._apply_tree_row_styles(self.tree)

        self.processes_empty_label = tk.Label(
            table_frame,
            text="No processes yet. Add one above or pick a preset to get started.",
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        )

    def _build_simulation_tab(self):

        summary_frame = tk.Frame(self.simulation_page, bg=Palette.BG_APP)
        summary_frame.pack(fill="x", pady=(0, 16))

        self.summary_cards = {}
        card_defs = [
            ("Processes", Palette.PRIMARY),
            ("Algorithm", Palette.PRIMARY),
            ("Avg WT", Palette.ACCENT),
            ("Avg TAT", Palette.ACCENT),
            ("Idle Time", Palette.WARNING),
            ("CPU Util", Palette.SUCCESS),
        ]
        for card_title, accent_color in card_defs:
            self.summary_cards[card_title] = self._make_stat_card(
                summary_frame, card_title, accent_color)
        summary_frame.winfo_children()[-1].pack_configure(padx=(0, 0))

        algo_card = self._card(self.simulation_page)
        algo_card.pack(fill="x", pady=(0, 16))

        self._section_title(
            algo_card, "Simulation Controls",
            "Choose a scheduling algorithm, set parameters, and run the simulation."
        )

        algo_frame = tk.Frame(algo_card, bg=Palette.BG_SURFACE)
        algo_frame.pack(fill="x", padx=24, pady=(0, 18))

        self.algo_var = tk.StringVar()

        algo_col = tk.Frame(algo_frame, bg=Palette.BG_SURFACE)
        algo_col.grid(row=0, column=0, sticky="ew", padx=(0, 16))
        tk.Label(
            algo_col, text="Algorithm",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(0, 6))
        self.algo_dropdown = ttk.Combobox(
            algo_col, textvariable=self.algo_var, values=self.ALGORITHMS,
            state="readonly", style="Scheduler.TCombobox")
        self.algo_dropdown.pack(fill="x")
        self.algo_dropdown.current(0)

        quantum_col = tk.Frame(algo_frame, bg=Palette.BG_SURFACE)
        quantum_col.grid(row=0, column=1, sticky="ew", padx=(0, 16))
        tk.Label(
            quantum_col, text="Time Quantum",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(0, 6))
        self.quantum_entry = tk.Entry(quantum_col, **self.entry_style)
        self.quantum_entry.pack(fill="x", ipady=6)
        self.quantum_entry.insert(0, "3")

        action_col = tk.Frame(algo_frame, bg=Palette.BG_SURFACE)
        action_col.grid(row=0, column=2, sticky="e")
        tk.Label(
            action_col, text=" ",
            font=(self.UI_FONT, 9, "bold"),
            bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(0, 6))
        action_buttons = tk.Frame(action_col, bg=Palette.BG_SURFACE)
        action_buttons.pack(fill="x")
        tk.Button(
            action_buttons, text="▶  Simulate",
            command=self.simulate, **self.button_style,
        ).pack(side="left")
        tk.Button(
            action_buttons, text="Compare All",
            command=self.compare_algorithms, **self.secondary_button_style,
        ).pack(side="left", padx=(10, 0))

        algo_frame.grid_columnconfigure(0, weight=3)
        algo_frame.grid_columnconfigure(1, weight=1)
        algo_frame.grid_columnconfigure(2, weight=0)

        help_chip = tk.Frame(
            algo_card, bg=Palette.BG_SURFACE_2,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        help_chip.pack(fill="x", padx=24, pady=(0, 22))
        help_inner = tk.Frame(help_chip, bg=Palette.BG_SURFACE_2)
        help_inner.pack(fill="x", padx=14, pady=12)
        tk.Label(
            help_inner, text="ⓘ",
            font=(self.UI_FONT, 12, "bold"),
            fg=Palette.INFO, bg=Palette.BG_SURFACE_2,
        ).pack(side="left", padx=(0, 10), anchor="n")
        self.algorithm_help_label = tk.Label(
            help_inner, text=self.ALGORITHM_HELP[self.get_selected_algorithm()],
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_SECONDARY, bg=Palette.BG_SURFACE_2,
            wraplength=900, justify="left",
        )
        self.algorithm_help_label.pack(side="left", fill="x", expand=True)

        self.algo_dropdown.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        self.update_quantum_state()

        gantt_card = self._card(self.simulation_page)
        gantt_card.pack(fill="x", pady=(0, 16))
        self._section_title(
            gantt_card, "Execution Timeline",
            "Visual representation of when each process runs on the CPU."
        )

        self.gantt_canvas = tk.Canvas(
            gantt_card, height=220, bg=Palette.BG_SURFACE_2,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        self.gantt_canvas.pack(fill="x", padx=24, pady=(0, 24))

        output_card = self._card(self.simulation_page)
        output_card.pack(fill="both", expand=True, pady=(0, 16))

        output_header = tk.Frame(output_card, bg=Palette.BG_SURFACE)
        output_header.pack(fill="x", padx=24, pady=(20, 14))
        title_col = tk.Frame(output_header, bg=Palette.BG_SURFACE)
        title_col.pack(side="left")
        tk.Label(
            title_col, text="Per-Process Metrics",
            font=(self.DISPLAY_FONT, 14, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        tk.Label(
            title_col, text="Completion, turnaround, waiting, and response times.",
            font=(self.UI_FONT, 9),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(2, 0))
        tk.Button(
            output_header, text="Export Results",
            command=self.export_current_results,
            **self.secondary_button_style,
        ).pack(side="right")

        results_table_frame = tk.Frame(output_card, bg=Palette.BG_SURFACE)
        results_table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 12))

        self.results_tree = ttk.Treeview(
            results_table_frame, columns=("PID", "CT", "TAT", "WT", "RT"),
            show="headings", style="Scheduler.Treeview", height=6)
        for col, header in (("PID", "Process"), ("CT", "Completion"),
                            ("TAT", "Turnaround"), ("WT", "Waiting"), ("RT", "Response")):
            self.results_tree.heading(col, text=header)
            self.results_tree.column(col, anchor="center", width=120)

        results_scroll = ttk.Scrollbar(
            results_table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scroll.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scroll.pack(side="right", fill="y")
        self._apply_tree_row_styles(self.results_tree)

        metric_strip = tk.Frame(output_card, bg=Palette.BG_SURFACE)
        metric_strip.pack(fill="x", padx=24, pady=(0, 8))
        self.averages_label = tk.Label(
            metric_strip,
            text="Average Waiting Time: —    Average Turnaround Time: —",
            font=(self.UI_FONT, 10, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        )
        self.averages_label.pack(anchor="w")
        self.performance_label = tk.Label(
            metric_strip,
            text="Response Time Avg: —    CPU Idle Time: —    CPU Utilization: —",
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        )
        self.performance_label.pack(anchor="w", pady=(4, 22))

        solution_card = self._card(self.simulation_page)
        solution_card.pack(fill="both", expand=True, pady=(0, 16))
        self._section_title(
            solution_card, "Calculation Breakdown",
            "Step-by-step math showing how each metric was derived."
        )
        self.solution_text = tk.Text(solution_card, height=8, **self.text_style)
        self.solution_text.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        footer_actions = tk.Frame(self.simulation_page, bg=Palette.BG_APP)
        footer_actions.pack(fill="x", pady=(0, 10))
        tk.Button(
            footer_actions, text="Reset Simulation",
            command=self.reset_simulation,
            **self.secondary_button_style,
        ).pack(side="left")

    def _build_comparison_tab(self):
        best_card = self._card(self.comparison_page)
        best_card.pack(fill="x", pady=(0, 16))

        best_inner = tk.Frame(best_card, bg=Palette.BG_SURFACE)
        best_inner.pack(fill="x", padx=24, pady=20)

        best_left = tk.Frame(best_inner, bg=Palette.BG_SURFACE)
        best_left.pack(side="left", fill="both", expand=True)

        trophy_row = tk.Frame(best_left, bg=Palette.BG_SURFACE)
        trophy_row.pack(anchor="w")
        tk.Label(
            trophy_row, text="🏆",
            font=(self.UI_FONT, 16),
            bg=Palette.BG_SURFACE,
        ).pack(side="left", padx=(0, 10))
        tk.Label(
            trophy_row, text="BEST PERFORMING ALGORITHM",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.SUCCESS, bg=Palette.BG_SURFACE,
        ).pack(side="left")

        self.best_algorithm_label = tk.Label(
            best_left, text="Run the comparison to see which algorithm performs best",
            font=(self.DISPLAY_FONT, 15, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        )
        self.best_algorithm_label.pack(anchor="w", pady=(8, 0))

        tk.Button(
            best_inner, text="Export Comparison",
            command=self.export_comparison_results,
            **self.secondary_button_style,
        ).pack(side="right", anchor="n")

        comparison_card = self._card(self.comparison_page)
        comparison_card.pack(fill="both", expand=True, pady=(0, 16))

        self._section_title(
            comparison_card, "Side-by-Side Comparison",
            "Every algorithm evaluated on the current process set. Lowest values are best."
        )

        comparison_table_frame = tk.Frame(comparison_card, bg=Palette.BG_SURFACE)
        comparison_table_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        self.comparison_tree = ttk.Treeview(
            comparison_table_frame, columns=("Algorithm", "Avg WT", "Avg TAT"),
            show="headings", style="Scheduler.Treeview", height=7)
        for col, header, width in (
            ("Algorithm", "Algorithm", 280),
            ("Avg WT", "Avg. Waiting Time", 160),
            ("Avg TAT", "Avg. Turnaround", 160),
        ):
            self.comparison_tree.heading(col, text=header)
            self.comparison_tree.column(col, anchor="center", width=width)

        comparison_scroll = ttk.Scrollbar(
            comparison_table_frame, orient="vertical", command=self.comparison_tree.yview)
        self.comparison_tree.configure(yscrollcommand=comparison_scroll.set)
        self.comparison_tree.pack(side="left", fill="both", expand=True)
        comparison_scroll.pack(side="right", fill="y")
        self.comparison_tree.tag_configure(
            "selected_algorithm",
            background=Palette.ROW_SELECTED, foreground=Palette.ROW_SELECTED_FG)
        self._apply_tree_row_styles(self.comparison_tree)

    def _build_footer(self):
        footer_frame = tk.Frame(self.main_frame, bg=Palette.BG_APP)
        footer_frame.pack(fill="x", padx=28, pady=(0, 24))
        tk.Label(
            footer_frame,
            text="Operating Systems Mini Project  ·  CPU Scheduling Simulator  ·  Built with Python and Tkinter",
            font=(self.UI_FONT, 9),
            fg=Palette.TEXT_SUBTLE, bg=Palette.BG_APP,
        ).pack(anchor="center")
        tk.Label(
            footer_frame,
            text="Shortcuts: Ctrl+N new process  ·  Ctrl+R / F5 simulate  ·  Ctrl+Shift+C compare  ·  Ctrl+E export  ·  Esc cancel edit",
            font=(self.UI_FONT, 8),
            fg=Palette.TEXT_SUBTLE, bg=Palette.BG_APP,
        ).pack(anchor="center", pady=(4, 0))


    def _setup_styles(self):
        configure_ttk_styles(self.UI_FONT)
        styles = build_widget_styles(self.UI_FONT, self.MONO_FONT)
        self.entry_style = styles["entry"]
        self.button_style = styles["button"]
        self.secondary_button_style = styles["secondary_button"]
        self.danger_button_style = styles["danger_button"]
        self.text_style = styles["text"]

    def _add_tab_banner(self, parent, title, subtitle):
        banner = tk.Frame(
            parent, bg=Palette.BG_SURFACE,
            highlightthickness=1, highlightbackground=Palette.BORDER,
        )
        banner.pack(fill="x", pady=(0, 16))
        accent = tk.Frame(banner, bg=Palette.PRIMARY, width=4)
        accent.pack(side="left", fill="y")
        body = tk.Frame(banner, bg=Palette.BG_SURFACE)
        body.pack(side="left", fill="both", expand=True, padx=20, pady=18)
        tk.Label(
            body, text=title,
            font=(self.DISPLAY_FONT, 14, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        tk.Label(
            body, text=subtitle,
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(6, 0))

    def _make_stat_card(self, parent, title, accent_color=Palette.PRIMARY):
        wrapper = tk.Frame(
            parent, bg=Palette.BG_SURFACE,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        wrapper.pack(side="left", fill="both", expand=True, padx=(0, 10))

        inner = tk.Frame(wrapper, bg=Palette.BG_SURFACE)
        inner.pack(fill="both", expand=True, padx=20, pady=18)

        label_row = tk.Frame(inner, bg=Palette.BG_SURFACE)
        label_row.pack(fill="x")
        tk.Frame(label_row, bg=accent_color, width=3, height=12).pack(
            side="left", padx=(0, 8))
        tk.Label(
            label_row, text=title.upper(),
            font=(self.UI_FONT, 8, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(side="left")

        value_label = tk.Label(
            inner, text="—",
            font=(self.DISPLAY_FONT, 22, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        )
        value_label.pack(anchor="w", pady=(10, 0))
        return value_label

    def _make_scrollable_tab(self, parent):
        canvas = tk.Canvas(parent, bg=Palette.BG_APP, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        content = tk.Frame(canvas, bg=Palette.BG_APP)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        window_id = canvas.create_window((0, 0), window=content, anchor="nw")

        def resize_content(event):
            canvas.itemconfigure(window_id, width=event.width)

        def update_scrollregion(_event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_mousewheel(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.delta:
                step = -1 if event.delta > 0 else 1
                canvas.yview_scroll(step, "units")
            return "break"

        def on_enter(_event):
            self.root.bind_all("<MouseWheel>", on_mousewheel)
            self.root.bind_all("<Button-4>", on_mousewheel)
            self.root.bind_all("<Button-5>", on_mousewheel)

        def on_leave(_event):
            self.root.unbind_all("<MouseWheel>")
            self.root.unbind_all("<Button-4>")
            self.root.unbind_all("<Button-5>")

        canvas.bind("<Configure>", resize_content)
        content.bind("<Configure>", update_scrollregion)
        canvas.bind("<Enter>", on_enter)
        canvas.bind("<Leave>", on_leave)

        return content

    def _next_row_tag(self, tree):
        return "evenrow" if len(tree.get_children()) % 2 == 0 else "oddrow"

    def _apply_tree_row_styles(self, tree):
        tree.tag_configure("evenrow", background=Palette.ROW_EVEN, foreground=Palette.TEXT_PRIMARY)
        tree.tag_configure("oddrow", background=Palette.ROW_ODD, foreground=Palette.TEXT_PRIMARY)


    def _bind_shortcuts(self):

        self.root.bind_all("<Control-n>", lambda e: self._focus_new_process())
        self.root.bind_all("<Control-N>", lambda e: self._focus_new_process())

        self.root.bind_all("<Control-r>", lambda e: self.simulate())
        self.root.bind_all("<Control-R>", lambda e: self.simulate())
        self.root.bind_all("<F5>", lambda e: self.simulate())

        self.root.bind_all("<Control-Shift-C>", lambda e: self.compare_algorithms())

        self.root.bind_all("<Control-e>", lambda e: self.export_current_results())
        self.root.bind_all("<Control-E>", lambda e: self.export_current_results())

        self.root.bind_all("<Escape>", lambda e: self.cancel_edit()
                           if self.selected_process_index is not None else None)

        self.tree.bind("<Delete>", lambda e: self.delete_selected_process())


        for entry, field in (
            (self.pid_entry, "pid"), (self.at_entry, "at"),
            (self.bt_entry, "bt"), (self.pr_entry, "pr"),
        ):
            entry.bind("<KeyRelease>", lambda e, w=entry, f=field: self._live_validate(w, f))

    def _focus_new_process(self):
        if self.selected_process_index is not None:
            self.cancel_edit()
        self.notebook.select(self.processes_tab)
        self.pid_entry.focus_set()


    def _mark_invalid(self, entry):
        entry.configure(
            highlightbackground=Palette.DANGER,
            highlightcolor=Palette.DANGER,
        )

    def _mark_valid(self, entry):
        entry.configure(
            highlightbackground=Palette.BORDER,
            highlightcolor=Palette.BORDER_FOCUS,
        )

    def _live_validate(self, entry, field):
        value = entry.get().strip()
        if field == "pid":

            if not value:
                self._mark_valid(entry)
                return
            is_duplicate = any(
                p.pid == value and idx != self.selected_process_index
                for idx, p in enumerate(self.processes)
            )
            if is_duplicate:
                self._mark_invalid(entry)
            else:
                self._mark_valid(entry)
            return


        if not value:
            self._mark_valid(entry)
            return
        try:
            n = int(value)
        except ValueError:
            self._mark_invalid(entry)
            return
        if n < 0:
            self._mark_invalid(entry)
            return
        if field == "bt" and n == 0:
            self._mark_invalid(entry)
            return
        self._mark_valid(entry)

    def _reset_all_entry_borders(self):
        for entry in (self.pid_entry, self.at_entry, self.bt_entry, self.pr_entry):
            self._mark_valid(entry)


    @staticmethod
    def _parse_int(value, field_name, allow_zero=True):
        try:
            n = int(value.strip())
        except (ValueError, AttributeError):
            raise ValueError(f"{field_name} must be an integer")
        if n < 0:
            raise ValueError(f"{field_name} must be non-negative")
        if n == 0 and not allow_zero:
            raise ValueError(f"{field_name} must be greater than zero")
        return n


    def get_selected_algorithm(self):
        return self.algo_var.get() or self.ALGORITHMS[0]

    def clear_process_form(self):
        self.pid_entry.delete(0, tk.END)
        self.at_entry.delete(0, tk.END)
        self.bt_entry.delete(0, tk.END)
        self.pr_entry.delete(0, tk.END)
        self.pid_entry.focus_set()

    def set_edit_mode(self, editing):
        if editing:
            self.add_update_button.configure(text="Update Process")
            self.cancel_edit_button.pack(side="left", padx=(10, 0))
        else:
            self.add_update_button.configure(text="+  Add Process")
            self.cancel_edit_button.pack_forget()

    def add_or_update_process(self):
        pid = self.pid_entry.get().strip()
        if not pid:
            messagebox.showerror("Invalid input", "PID is required")
            return

        try:
            at = self._parse_int(self.at_entry.get(), "Arrival time")
            bt = self._parse_int(self.bt_entry.get(), "Burst time", allow_zero=False)
            pr = self._parse_int(self.pr_entry.get(), "Priority")
        except ValueError as error:
            messagebox.showerror("Invalid input", str(error))
            return

        duplicate_pid = any(
            existing_process.pid == pid and index != self.selected_process_index
            for index, existing_process in enumerate(self.processes)
        )
        if duplicate_pid:
            messagebox.showerror("Invalid input", "PID must be unique")
            return

        process = Process(pid, at, bt, pr)

        if self.selected_process_index is None:
            self.processes.append(process)
        else:
            self.processes[self.selected_process_index] = process
            self.cancel_edit()
            self.clear_process_form()
            self.update_summary_cards()
            self.refresh_process_tree()
            self._reset_all_entry_borders()
            return

        self.clear_process_form()
        self.refresh_process_tree()
        self.update_summary_cards()
        self._reset_all_entry_borders()

        if self.algo_var.get():
            self.simulate(show_errors=False, navigate=False)

    def on_add_process_enter(self, event=None):
        self.add_or_update_process()

    def on_tree_select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return

        item_id = selection[0]
        item_index = self.tree.index(item_id)
        process = self.processes[item_index]

        self.selected_process_index = item_index
        self.set_edit_mode(True)

        self.clear_process_form()
        self.pid_entry.insert(0, process.pid)
        self.at_entry.insert(0, process.arrival_time)
        self.bt_entry.insert(0, process.burst_time)
        self.pr_entry.insert(0, process.priority)
        self._reset_all_entry_borders()

    def cancel_edit(self):
        self.selected_process_index = None
        self.tree.selection_remove(*self.tree.selection())
        self.set_edit_mode(False)
        self.clear_process_form()

    def delete_selected_process(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showerror("Error", "Select a process to delete")
            return

        item_id = selection[0]
        item_index = self.tree.index(item_id)
        del self.processes[item_index]
        self.cancel_edit()
        self.refresh_process_tree()
        self.clear_simulation_outputs()
        self.update_summary_cards()

    def clear_all_processes(self):

        if self.processes:
            if not messagebox.askyesno(
                "Clear all processes?",
                "This will remove all queued processes and reset the simulation. Continue?",
                icon="warning",
            ):
                return
        self.processes.clear()
        self.refresh_process_tree()
        self.cancel_edit()
        self.clear_simulation_outputs()
        self.update_summary_cards()
        self._reset_all_entry_borders()

    def load_demo_case(self):
        self._load_preset("Basic Example")

    def _on_preset_selected(self, event=None):
        name = self.preset_var.get()
        if not name:
            return
        self._load_preset(name)
        self.preset_dropdown.selection_clear()

    def _load_preset(self, name):
        preset = self.PRESETS.get(name)
        if not preset:
            return
        if self.processes:
            if not messagebox.askyesno(
                "Load preset?",
                f"This will replace the current workload with the “{name}” preset.\n\n"
                f"{preset['description']}\n\nContinue?",
                icon="question",
            ):
                return
        self.processes.clear()
        self.cancel_edit()
        for pid, at, bt, pr in preset["processes"]:
            self.processes.append(Process(pid, at, bt, pr))
        self.refresh_process_tree()
        self.update_summary_cards()
        self._reset_all_entry_borders()
        self.simulate(show_errors=False, navigate=False)
        self.compare_algorithms(navigate=False)


    def update_summary_cards(self, avg_wt="—", avg_tat="—", idle_time="—", cpu_util="—"):
        selected_algorithm = self.get_selected_algorithm()
        process_count = len(self.processes)
        self.summary_cards["Processes"].configure(text=str(process_count))
        self.summary_cards["Algorithm"].configure(text=selected_algorithm)
        self.summary_cards["Avg WT"].configure(text=avg_wt)
        self.summary_cards["Avg TAT"].configure(text=avg_tat)
        self.summary_cards["Idle Time"].configure(text=idle_time)
        self.summary_cards["CPU Util"].configure(text=cpu_util)
        self.header_algorithm_label.configure(text=selected_algorithm)
        plural = "process" if process_count == 1 else "processes"
        self.header_process_count_label.configure(text=f"{process_count} {plural}")
        if hasattr(self, "status_dot"):
            self.status_dot.delete("all")
            dot_color = Palette.SUCCESS if process_count > 0 else Palette.TEXT_MUTED
            self.status_dot.configure(bg=Palette.BG_SURFACE_2)
            self.status_dot.create_oval(1, 1, 7, 7, fill=dot_color, outline="")

    def refresh_process_tree(self):
        self.tree.delete(*self.tree.get_children())
        for process in self.processes:
            self.tree.insert(
                "", "end",
                values=(process.pid, process.arrival_time,
                        process.burst_time, process.priority),
                tags=(self._next_row_tag(self.tree),))
        if hasattr(self, "processes_empty_label"):
            if self.processes:
                self.processes_empty_label.place_forget()
            else:
                self.processes_empty_label.place(relx=0.5, rely=0.5, anchor="center")

    def clear_simulation_outputs(self):
        self.gantt_canvas.delete("all")
        self.show_gantt_chart([])
        self.solution_text.delete("1.0", tk.END)
        self.results_tree.delete(*self.results_tree.get_children())
        self.averages_label.configure(
            text="Average Waiting Time: —    Average Turnaround Time: —")
        self.performance_label.configure(
            text="Response Time Avg: —    CPU Idle Time: —    CPU Utilization: —")
        self.last_result_rows = []
        self.last_metrics = {}
        self.last_timeline = []
        self.update_summary_cards()

    def update_quantum_state(self):
        is_round_robin = self.algo_var.get() == "Round Robin"
        self.quantum_entry.configure(state="normal" if is_round_robin else "disabled")

    def on_algorithm_change(self, event=None):
        self.update_quantum_state()
        self.update_summary_cards()
        self.algorithm_help_label.configure(
            text=self.ALGORITHM_HELP.get(self.get_selected_algorithm(), ""))
        self.highlight_selected_algorithm()

        if not self.processes:
            return
        if self.algo_var.get() == "Round Robin" and not self.quantum_entry.get().strip().isdigit():
            return

        self.simulate(show_errors=False, navigate=False)


    def run_algorithm(self, algorithm_name, process_list):
        runner = self.ALGORITHM_DISPATCH.get(algorithm_name)
        if runner is None:
            raise ValueError(f"Unsupported algorithm: {algorithm_name}")

        tq = None
        if algorithm_name == "Round Robin":
            raw = self.quantum_entry.get().strip()
            if not raw.isdigit() or int(raw) <= 0:
                raise ValueError("Enter a valid time quantum (positive integer)")
            tq = int(raw)

        return runner(process_list, tq)

    def compare_algorithms(self, navigate=True):
        if not self.processes:
            messagebox.showerror("Error", "No processes added")
            return

        if navigate:
            self.notebook.select(self.comparison_tab)
        self.comparison_tree.delete(*self.comparison_tree.get_children())
        self.last_comparison_rows = []

        for algorithm_name in self.ALGORITHMS:
            process_list = [
                Process(p.pid, p.arrival_time, p.burst_time, p.priority)
                for p in self.processes
            ]

            try:
                result, _ = self.run_algorithm(algorithm_name, process_list)
            except ValueError as error:
                self.comparison_tree.insert(
                    "", "end",
                    values=(algorithm_name, "N/A", str(error)),
                    tags=(self._next_row_tag(self.comparison_tree),))
                continue

            avg_wt = sum(p.waiting_time for p in result) / len(result)
            avg_tat = sum(p.turnaround_time for p in result) / len(result)
            row = (algorithm_name, f"{avg_wt:.2f}", f"{avg_tat:.2f}", avg_wt, avg_tat)
            self.last_comparison_rows.append(row)
            self.comparison_tree.insert(
                "", "end", values=row[:3],
                tags=(self._next_row_tag(self.comparison_tree),))

        if self.last_comparison_rows:
            best_row = min(self.last_comparison_rows, key=lambda row: (row[3], row[4], row[0]))
            self.best_algorithm_label.configure(
                text=f"{best_row[0]}   ·   Avg WT: {best_row[1]}   ·   Avg TAT: {best_row[2]}")
        else:
            self.best_algorithm_label.configure(text="Run comparison to see results")
        self.highlight_selected_algorithm()

    def highlight_selected_algorithm(self):
        if not self.last_comparison_rows:
            return
        selected_algorithm = self.get_selected_algorithm()
        for item_id in self.comparison_tree.get_children():
            row_values = self.comparison_tree.item(item_id, "values")
            if row_values and row_values[0] == selected_algorithm:
                self.comparison_tree.item(item_id, tags=("selected_algorithm",))
            else:
                self.comparison_tree.item(item_id, tags=())


    def export_current_results(self):
        if not self.last_result_rows or not self.last_metrics:
            messagebox.showerror("Error", "Run a simulation before exporting")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Current Results")
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Algorithm", self.last_metrics["algorithm"]])
                writer.writerow(["Average Waiting Time", f"{self.last_metrics['avg_wt']:.2f}"])
                writer.writerow(["Average Turnaround Time", f"{self.last_metrics['avg_tat']:.2f}"])
                writer.writerow(["CPU Idle Time", str(self.last_metrics["idle_time"])])
                writer.writerow(["CPU Utilization", f"{self.last_metrics['cpu_util']:.2f}%"])
                writer.writerow([])
                writer.writerow(["PID", "Completion Time", "Turnaround Time",
                                 "Waiting Time", "Response Time"])
                writer.writerows(self.last_result_rows)
        except OSError as error:
            messagebox.showerror("Export failed", f"Could not write file:\n{error}")
            return

        messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")

    def export_comparison_results(self):
        if not self.last_comparison_rows:
            messagebox.showerror("Error", "Run algorithm comparison before exporting")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Algorithm Comparison")
        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(["Algorithm", "Average Waiting Time", "Average Turnaround Time"])
                for algorithm_name, avg_wt, avg_tat, _, _ in self.last_comparison_rows:
                    writer.writerow([algorithm_name, avg_wt, avg_tat])
        except OSError as error:
            messagebox.showerror("Export failed", f"Could not write file:\n{error}")
            return

        messagebox.showinfo("Export Complete", f"Comparison exported to:\n{file_path}")

    def reset_simulation(self):
        self.clear_simulation_outputs()
        self.update_summary_cards()


    def show_gantt_chart(self, timeline, animate=False):
        if hasattr(self, "_gantt_anim_job") and self._gantt_anim_job:
            try:
                self.root.after_cancel(self._gantt_anim_job)
            except Exception:
                pass
            self._gantt_anim_job = None

        self.gantt_canvas.delete("all")

        if not timeline:
            self.gantt_canvas.update_idletasks()
            w = self.gantt_canvas.winfo_width() or 800
            h = self.gantt_canvas.winfo_height() or 220
            self.gantt_canvas.create_text(
                w // 2, h // 2 - 10,
                text="📊",
                fill=Palette.TEXT_MUTED, font=(self.UI_FONT, 20))
            self.gantt_canvas.create_text(
                w // 2, h // 2 + 20,
                text="Run a simulation to view the execution timeline",
                fill=Palette.TEXT_MUTED, font=(self.UI_FONT, 10))
            return

        scale = 44
        y1, y2 = 72, 136
        colors = Palette.GANTT_COLORS

        self.gantt_canvas.create_text(
            24, 28, text="Timeline", anchor="w",
            fill=Palette.TEXT_PRIMARY, font=(self.DISPLAY_FONT, 11, "bold"))
        self.gantt_canvas.create_line(
            24, y2 + 10, 980, y2 + 10,
            fill=Palette.BORDER, width=1)

        if not animate:
            for index, (pid, start, end) in enumerate(timeline):
                self._draw_gantt_block(index, pid, start, end, scale, y1, y2, colors)
            self.gantt_canvas.create_text(
                30 + timeline[-1][2] * scale, y2 + 30,
                text=str(timeline[-1][2]),
                fill=Palette.TEXT_SECONDARY, font=(self.UI_FONT, 10))
            return

        self._animate_gantt(timeline, 0, scale, y1, y2, colors)

    def _draw_gantt_block(self, index, pid, start, end, scale, y1, y2, colors):
        x1 = 30 + start * scale
        x2 = 30 + end * scale
        self.gantt_canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=colors[index % len(colors)],
            outline=Palette.BG_SURFACE_2, width=1)
        self.gantt_canvas.create_text(
            (x1 + x2) / 2, (y1 + y2) / 2,
            text=pid, fill="#ffffff",
            font=(self.UI_FONT, 10, "bold"))
        self.gantt_canvas.create_text(
            x1, y2 + 30, text=str(start),
            fill=Palette.TEXT_SECONDARY, font=(self.UI_FONT, 10))

    def _animate_gantt(self, timeline, index, scale, y1, y2, colors):
        if index >= len(timeline):
            self.gantt_canvas.create_text(
                30 + timeline[-1][2] * scale, y2 + 30,
                text=str(timeline[-1][2]),
                fill=Palette.TEXT_SECONDARY, font=(self.UI_FONT, 10))
            self._gantt_anim_job = None
            return

        pid, start, end = timeline[index]
        self._draw_gantt_block(index, pid, start, end, scale, y1, y2, colors)

        delay = 220 if len(timeline) <= 12 else max(80, 2000 // len(timeline))
        self._gantt_anim_job = self.root.after(
            delay,
            lambda: self._animate_gantt(timeline, index + 1, scale, y1, y2, colors),
        )


    def simulate(self, show_errors=True, navigate=True):
        if not self.processes:
            if show_errors:
                messagebox.showerror("Error", "No processes added")
            return

        if navigate:
            self.notebook.select(self.simulation_tab)

        process_list = [
            Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            for p in self.processes
        ]

        algo = self.algo_var.get()

        try:
            result, timeline = self.run_algorithm(algo, process_list)
        except ValueError as error:
            if show_errors:
                messagebox.showerror("Error", str(error))
            return

        self.show_gantt_chart(timeline, animate=navigate)
        self.last_timeline = timeline

        self.results_tree.delete(*self.results_tree.get_children())
        self.solution_text.delete("1.0", tk.END)
        self.last_result_rows = []

        execution_order = " → ".join(pid for pid, _, _ in timeline if pid != "IDLE")
        self.solution_text.insert(tk.END, f"Execution Order: {execution_order}\n\n")

        for p in result:
            response_time = p.start_time - p.arrival_time
            row = (p.pid, p.completion_time, p.turnaround_time,
                   p.waiting_time, response_time)
            self.last_result_rows.append(row)
            self.results_tree.insert(
                "", "end", values=row,
                tags=(self._next_row_tag(self.results_tree),))

            self.solution_text.insert(
                tk.END,
                f"{p.pid}: TAT={p.completion_time}-{p.arrival_time}={p.turnaround_time}, "
                f"WT={p.turnaround_time}-{p.burst_time}={p.waiting_time}, "
                f"RT={p.start_time}-{p.arrival_time}={response_time}\n")

        avg_wt = sum(p.waiting_time for p in result) / len(result)
        avg_tat = sum(p.turnaround_time for p in result) / len(result)
        avg_rt = sum(p.start_time - p.arrival_time for p in result) / len(result)
        completion_time = max(p.completion_time for p in result)
        total_burst_time = sum(p.burst_time for p in result)
        idle_time = max(0, completion_time - total_burst_time)
        cpu_utilization = (total_burst_time / completion_time * 100) if completion_time else 0

        self.last_metrics = {
            "algorithm": algo,
            "avg_wt": avg_wt,
            "avg_tat": avg_tat,
            "avg_rt": avg_rt,
            "idle_time": idle_time,
            "cpu_util": cpu_utilization,
        }

        self.averages_label.configure(
            text=f"Average Waiting Time: {avg_wt:.2f}    Average Turnaround Time: {avg_tat:.2f}")
        self.performance_label.configure(
            text=f"Response Time Avg: {avg_rt:.2f}    CPU Idle Time: {idle_time}    "
                 f"CPU Utilization: {cpu_utilization:.2f}%")
        self.update_summary_cards(
            f"{avg_wt:.2f}", f"{avg_tat:.2f}",
            str(idle_time), f"{cpu_utilization:.2f}%")
        self.highlight_selected_algorithm()


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()