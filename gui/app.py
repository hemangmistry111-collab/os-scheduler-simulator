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
from theme import Palette, configure_ttk_styles, build_widget_styles


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

    def __init__(self, root):
        self.root = root
        self.root.title("OS Process Scheduler Simulator")
        self._apply_zoomed_state()
        self.root.configure(bg=Palette.BG_APP)

        self._resolve_fonts()


        self.processes = []
        self.selected_process_index = None
        self.last_result_rows = []
        self.last_comparison_rows = []
        self.last_metrics = {}

        self._setup_styles()
        self._build_main_layout()
        self._build_processes_tab()
        self._build_simulation_tab()
        self._build_comparison_tab()
        self._build_footer()
        self._bind_shortcuts()

        self.update_summary_cards()
        self.show_gantt_chart([])


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
            highlightthickness=1, highlightbackground=Palette.BORDER,
        )
        header_frame.pack(fill="x", padx=28, pady=(24, 18))


        header_text = tk.Frame(header_frame, bg=Palette.BG_SURFACE)
        header_text.pack(side="left", fill="both", expand=True, padx=28, pady=24)


        eyebrow_row = tk.Frame(header_text, bg=Palette.BG_SURFACE)
        eyebrow_row.pack(anchor="w")
        tk.Frame(eyebrow_row, bg=Palette.PRIMARY, width=3, height=14).pack(
            side="left", padx=(0, 8))
        tk.Label(
            eyebrow_row, text="OPERATING SYSTEMS SCHEDULER LAB",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(side="left")

        tk.Label(
            header_text, text="OS Process Scheduler Simulator",
            font=(self.DISPLAY_FONT, 26, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(10, 0))
        tk.Label(
            header_text,
            text="Build workloads, compare CPU scheduling strategies, and inspect execution timelines in one place.",
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w", pady=(8, 0))


        header_stats = tk.Frame(header_frame, bg=Palette.BG_SURFACE)
        header_stats.pack(side="right", padx=28, pady=24)

        stat_card = tk.Frame(
            header_stats, bg=Palette.BG_SURFACE_2,
            highlightthickness=1, highlightbackground=Palette.BORDER,
            padx=18, pady=14,
        )
        stat_card.pack(anchor="e")
        tk.Label(
            stat_card, text="CURRENT WORKSPACE",
            font=(self.UI_FONT, 8, "bold"),
            fg=Palette.ACCENT, bg=Palette.BG_SURFACE_2,
        ).pack(anchor="w")
        self.header_algorithm_label = tk.Label(
            stat_card, text="Algorithm: FCFS",
            font=(self.UI_FONT, 10, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE_2,
        )
        self.header_algorithm_label.pack(anchor="w", pady=(10, 2))
        self.header_process_count_label = tk.Label(
            stat_card, text="Processes: 0",
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE_2,
        )
        self.header_process_count_label.pack(anchor="w")


        self.notebook = ttk.Notebook(self.main_frame, style="Scheduler.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=28, pady=(0, 18))

        self.processes_tab = tk.Frame(self.notebook, bg=Palette.BG_APP)
        self.simulation_tab = tk.Frame(self.notebook, bg=Palette.BG_APP)
        self.comparison_tab = tk.Frame(self.notebook, bg=Palette.BG_APP)

        self.notebook.add(self.processes_tab, text="  Processes  ")
        self.notebook.add(self.simulation_tab, text="  Simulation  ")
        self.notebook.add(self.comparison_tab, text="  Comparison  ")

        self.processes_page = self._make_scrollable_tab(self.processes_tab)
        self.simulation_page = self._make_scrollable_tab(self.simulation_tab)
        self.comparison_page = self._make_scrollable_tab(self.comparison_tab)

        self._add_tab_banner(
            self.processes_page,
            "Process Workspace",
            "Create, edit, and organize the workload before running any scheduling strategy."
        )
        self._add_tab_banner(
            self.simulation_page,
            "Simulation Studio",
            "Run one algorithm at a time, inspect metrics, and review the Gantt execution flow."
        )
        self._add_tab_banner(
            self.comparison_page,
            "Comparison Board",
            "Compare every available algorithm on the same process set and spot the best performer."
        )

    def _build_processes_tab(self):

        input_card = self._card(self.processes_page)
        input_card.pack(fill="x", pady=(0, 16))

        self._section_title(
            input_card, "Add Process",
            "Enter process details manually or load a demo workload."
        )

        input_frame = tk.Frame(input_card, bg=Palette.BG_SURFACE)
        input_frame.pack(fill="x", padx=22, pady=(0, 22))


        for col_index, header in (
            (1, "Process ID"), (3, "Arrival"), (5, "Burst"), (7, "Priority"),
        ):
            tk.Label(
                input_frame, text=header,
                font=(self.UI_FONT, 9, "bold"),
                fg=Palette.TEXT_SECONDARY, bg=Palette.BG_SURFACE,
            ).grid(row=0, column=col_index, sticky="w", padx=(0, 14), pady=(0, 6))

        self.pid_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.at_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.bt_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.pr_entry = tk.Entry(input_frame, width=12, **self.entry_style)

        self.pid_entry.grid(row=1, column=1, padx=(0, 14), pady=(0, 6), sticky="ew", ipady=4)
        self.at_entry.grid(row=1, column=3, padx=(0, 14), pady=(0, 6), sticky="ew", ipady=4)
        self.bt_entry.grid(row=1, column=5, padx=(0, 14), pady=(0, 6), sticky="ew", ipady=4)
        self.pr_entry.grid(row=1, column=7, padx=(0, 14), pady=(0, 6), sticky="ew", ipady=4)

        self.add_update_button = tk.Button(
            input_frame, text="Add Process",
            command=self.add_or_update_process, **self.button_style)
        self.add_update_button.grid(row=1, column=8, padx=(8, 8), sticky="ew")

        self.cancel_edit_button = tk.Button(
            input_frame, text="Cancel",
            command=self.cancel_edit, **self.secondary_button_style)
        self.cancel_edit_button.grid(row=1, column=9, sticky="ew")
        self.cancel_edit_button.grid_remove()

        self.demo_button = tk.Button(
            input_frame, text="Load Demo Case",
            command=self.load_demo_case, **self.secondary_button_style)
        self.demo_button.grid(row=2, column=8, columnspan=2, pady=(14, 0), sticky="ew")

        for entry in (self.pid_entry, self.at_entry, self.bt_entry, self.pr_entry):
            entry.bind("<Return>", self.on_add_process_enter)

        for column in (1, 3, 5, 7, 8, 9):
            input_frame.grid_columnconfigure(column, weight=1)


        table_outer = self._card(self.processes_page)
        table_outer.pack(fill="both", expand=True, pady=(0, 16))

        table_header = tk.Frame(table_outer, bg=Palette.BG_SURFACE)
        table_header.pack(fill="x", padx=22, pady=(20, 14))

        title_col = tk.Frame(table_header, bg=Palette.BG_SURFACE)
        title_col.pack(side="left")
        tk.Label(
            title_col, text="Queued Processes",
            font=(self.DISPLAY_FONT, 14, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        tk.Label(
            title_col, text="Click a row to edit, then save your changes.",
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
        table_frame.pack(fill="both", expand=True, padx=22, pady=(0, 22))

        self.tree = ttk.Treeview(
            table_frame, columns=("PID", "AT", "BT", "PR"),
            show="headings", style="Scheduler.Treeview")
        for col in ("PID", "AT", "BT", "PR"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=table_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        table_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self._apply_tree_row_styles(self.tree)

    def _build_simulation_tab(self):

        algo_card = self._card(self.simulation_page)
        algo_card.pack(fill="x", pady=(0, 16))

        self._section_title(
            algo_card, "Simulation Controls",
            "Pick an algorithm, tune the controls, then simulate or compare all methods."
        )

        algo_frame = tk.Frame(algo_card, bg=Palette.BG_SURFACE)
        algo_frame.pack(fill="x", padx=22, pady=(0, 22))

        self.algo_var = tk.StringVar()

        self.algo_dropdown = ttk.Combobox(
            algo_frame, textvariable=self.algo_var, values=self.ALGORITHMS,
            state="readonly", width=30, style="Scheduler.TCombobox")
        self.algo_dropdown.grid(row=0, column=0, padx=(0, 16), sticky="ew")
        self.algo_dropdown.current(0)

        tk.Label(
            algo_frame, text="Time Quantum",
            font=(self.UI_FONT, 9, "bold"),
            fg=Palette.TEXT_SECONDARY, bg=Palette.BG_SURFACE,
        ).grid(row=0, column=1, sticky="w", padx=(0, 10))
        self.quantum_entry = tk.Entry(algo_frame, width=10, **self.entry_style)
        self.quantum_entry.grid(row=0, column=2, sticky="ew", ipady=4)
        self.quantum_entry.insert(0, "3")

        tk.Button(
            algo_frame, text="Simulate",
            command=self.simulate, **self.button_style,
        ).grid(row=0, column=3, padx=(16, 0), sticky="ew")
        tk.Button(
            algo_frame, text="Compare All",
            command=self.compare_algorithms, **self.secondary_button_style,
        ).grid(row=0, column=4, padx=(12, 0), sticky="ew")


        help_chip = tk.Frame(
            algo_card, bg=Palette.BG_INPUT,
            highlightthickness=1, highlightbackground=Palette.BORDER_SOFT,
        )
        help_chip.pack(fill="x", padx=22, pady=(0, 22))
        help_inner = tk.Frame(help_chip, bg=Palette.BG_INPUT)
        help_inner.pack(fill="x", padx=14, pady=12)
        tk.Label(
            help_inner, text="ⓘ",
            font=(self.UI_FONT, 11, "bold"),
            fg=Palette.PRIMARY, bg=Palette.BG_INPUT,
        ).pack(side="left", padx=(0, 10), anchor="n")
        self.algorithm_help_label = tk.Label(
            help_inner, text=self.ALGORITHM_HELP[self.get_selected_algorithm()],
            font=(self.UI_FONT, 10),
            fg=Palette.TEXT_SECONDARY, bg=Palette.BG_INPUT,
            wraplength=900, justify="left",
        )
        self.algorithm_help_label.pack(side="left", fill="x", expand=True)

        algo_frame.grid_columnconfigure(0, weight=3)
        algo_frame.grid_columnconfigure(2, weight=1)
        algo_frame.grid_columnconfigure(3, weight=1)
        algo_frame.grid_columnconfigure(4, weight=1)
        self.algo_dropdown.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        self.update_quantum_state()


        summary_frame = tk.Frame(self.simulation_page, bg=Palette.BG_APP)
        summary_frame.pack(fill="x", pady=(0, 16))

        self.summary_cards = {}
        card_defs = [
            ("Processes", Palette.PRIMARY),
            ("Algorithm", Palette.PRIMARY),
            ("Avg WT", Palette.ACCENT),
            ("Avg TAT", Palette.ACCENT),
            ("Idle Time", Palette.TEXT_SECONDARY),
            ("CPU Util", Palette.SUCCESS),
        ]
        for card_title, accent_color in card_defs:
            self.summary_cards[card_title] = self._make_stat_card(
                summary_frame, card_title, accent_color)
        summary_frame.winfo_children()[-1].pack_configure(padx=(0, 0))


        output_card = self._card(self.simulation_page)
        output_card.pack(fill="both", expand=True, pady=(0, 16))

        self._section_title(output_card, "Results")

        results_table_frame = tk.Frame(output_card, bg=Palette.BG_SURFACE)
        results_table_frame.pack(fill="both", expand=True, padx=22, pady=(0, 12))

        self.results_tree = ttk.Treeview(
            results_table_frame, columns=("PID", "CT", "TAT", "WT", "RT"),
            show="headings", style="Scheduler.Treeview", height=6)
        for col in ("PID", "CT", "TAT", "WT", "RT"):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, anchor="center", width=108)

        results_scroll = ttk.Scrollbar(
            results_table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scroll.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scroll.pack(side="right", fill="y")
        self._apply_tree_row_styles(self.results_tree)


        metric_strip = tk.Frame(output_card, bg=Palette.BG_SURFACE)
        metric_strip.pack(fill="x", padx=22, pady=(0, 8))
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
        self.performance_label.pack(anchor="w", pady=(4, 0))

        export_frame = tk.Frame(output_card, bg=Palette.BG_SURFACE)
        export_frame.pack(fill="x", padx=22, pady=(12, 22))
        tk.Button(
            export_frame, text="Export Current Results",
            command=self.export_current_results,
            **self.secondary_button_style,
        ).pack(side="left")


        solution_card = self._card(self.simulation_page)
        solution_card.pack(fill="both", expand=True, pady=(0, 16))
        self._section_title(solution_card, "Working")
        self.solution_text = tk.Text(solution_card, height=8, **self.text_style)
        self.solution_text.pack(fill="both", expand=True, padx=22, pady=(0, 22))


        gantt_card = self._card(self.simulation_page)
        gantt_card.pack(fill="both", expand=True, pady=(0, 16))
        self._section_title(
            gantt_card, "Gantt Chart",
            "Execution timeline of the currently selected scheduling strategy."
        )

        self.gantt_canvas = tk.Canvas(
            gantt_card, height=240, bg=Palette.BG_INPUT,
            highlightthickness=1, highlightbackground=Palette.BORDER,
        )
        self.gantt_canvas.pack(fill="both", expand=True, padx=22, pady=(0, 22))


        footer_actions = tk.Frame(self.simulation_page, bg=Palette.BG_APP)
        footer_actions.pack(fill="x", pady=(0, 10))
        tk.Button(
            footer_actions, text="Reset Simulation",
            command=self.reset_simulation,
            **self.secondary_button_style,
        ).pack(side="left")

    def _build_comparison_tab(self):
        comparison_card = self._card(self.comparison_page)
        comparison_card.pack(fill="both", expand=True)
        self._section_title(comparison_card, "Algorithm Comparison")

        comparison_table_frame = tk.Frame(comparison_card, bg=Palette.BG_SURFACE)
        comparison_table_frame.pack(fill="both", expand=True, padx=22, pady=(0, 22))

        self.comparison_tree = ttk.Treeview(
            comparison_table_frame, columns=("Algorithm", "Avg WT", "Avg TAT"),
            show="headings", style="Scheduler.Treeview", height=7)
        for col, width in (("Algorithm", 260), ("Avg WT", 120), ("Avg TAT", 120)):
            self.comparison_tree.heading(col, text=col)
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

        comparison_export_frame = tk.Frame(comparison_card, bg=Palette.BG_SURFACE)
        comparison_export_frame.pack(fill="x", padx=22, pady=(0, 16))
        tk.Button(
            comparison_export_frame, text="Export Comparison",
            command=self.export_comparison_results,
            **self.secondary_button_style,
        ).pack(side="left")


        best_banner = tk.Frame(
            comparison_card, bg=Palette.BG_SURFACE_2,
            highlightthickness=1, highlightbackground=Palette.BORDER,
        )
        best_banner.pack(fill="x", padx=22, pady=(0, 22))

        best_accent = tk.Frame(best_banner, bg=Palette.SUCCESS, width=4)
        best_accent.pack(side="left", fill="y")

        best_inner = tk.Frame(best_banner, bg=Palette.BG_SURFACE_2)
        best_inner.pack(side="left", fill="both", expand=True, padx=16, pady=12)
        tk.Label(
            best_inner, text="★ BEST PERFORMER",
            font=(self.UI_FONT, 8, "bold"),
            fg=Palette.SUCCESS, bg=Palette.BG_SURFACE_2,
        ).pack(anchor="w")
        self.best_algorithm_label = tk.Label(
            best_inner, text="Run comparison to see results",
            font=(self.UI_FONT, 11, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE_2,
        )
        self.best_algorithm_label.pack(anchor="w", pady=(4, 0))

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
            highlightthickness=1, highlightbackground=Palette.BORDER,
        )
        wrapper.pack(side="left", fill="x", expand=True, padx=(0, 12))


        tk.Frame(wrapper, bg=accent_color, height=3).pack(fill="x")

        inner = tk.Frame(wrapper, bg=Palette.BG_SURFACE)
        inner.pack(fill="both", expand=True, padx=20, pady=16)

        tk.Label(
            inner, text=title.upper(),
            font=(self.UI_FONT, 8, "bold"),
            fg=Palette.TEXT_MUTED, bg=Palette.BG_SURFACE,
        ).pack(anchor="w")
        value_label = tk.Label(
            inner, text="—",
            font=(self.DISPLAY_FONT, 20, "bold"),
            fg=Palette.TEXT_PRIMARY, bg=Palette.BG_SURFACE,
        )
        value_label.pack(anchor="w", pady=(8, 0))
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

        canvas.bind("<Configure>", resize_content)
        content.bind("<Configure>", update_scrollregion)

        for widget in (canvas, content):
            widget.bind("<MouseWheel>", on_mousewheel)
            widget.bind("<Button-4>", on_mousewheel)
            widget.bind("<Button-5>", on_mousewheel)

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
            self.cancel_edit_button.grid()
        else:
            self.add_update_button.configure(text="Add Process")
            self.cancel_edit_button.grid_remove()

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
            self.simulate(show_errors=False)

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
        self.clear_all_processes()
        for pid, at, bt, pr in self.DEMO_PROCESSES:
            self.processes.append(Process(pid, at, bt, pr))
        self.refresh_process_tree()
        self.update_summary_cards()
        self.simulate(show_errors=False)
        self.compare_algorithms()


    def update_summary_cards(self, avg_wt="—", avg_tat="—", idle_time="—", cpu_util="—"):
        selected_algorithm = self.get_selected_algorithm()
        self.summary_cards["Processes"].configure(text=str(len(self.processes)))
        self.summary_cards["Algorithm"].configure(text=selected_algorithm)
        self.summary_cards["Avg WT"].configure(text=avg_wt)
        self.summary_cards["Avg TAT"].configure(text=avg_tat)
        self.summary_cards["Idle Time"].configure(text=idle_time)
        self.summary_cards["CPU Util"].configure(text=cpu_util)
        self.header_algorithm_label.configure(text=f"Algorithm: {selected_algorithm}")
        self.header_process_count_label.configure(text=f"Processes: {len(self.processes)}")

    def refresh_process_tree(self):
        self.tree.delete(*self.tree.get_children())
        for process in self.processes:
            self.tree.insert(
                "", "end",
                values=(process.pid, process.arrival_time,
                        process.burst_time, process.priority),
                tags=(self._next_row_tag(self.tree),))

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

        self.simulate(show_errors=False)


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

    def compare_algorithms(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes added")
            return

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


    def show_gantt_chart(self, timeline):
        self.gantt_canvas.delete("all")

        if not timeline:
            self.gantt_canvas.create_text(
                420, 110,
                text="Run a simulation to view the execution timeline.",
                fill=Palette.TEXT_MUTED, font=(self.UI_FONT, 11))
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

        for index, (pid, start, end) in enumerate(timeline):
            x1 = 30 + start * scale
            x2 = 30 + end * scale

            self.gantt_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill=colors[index % len(colors)],
                outline=Palette.BG_INPUT, width=1)
            self.gantt_canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=pid, fill="#ffffff",
                font=(self.UI_FONT, 10, "bold"))
            self.gantt_canvas.create_text(
                x1, y2 + 30, text=str(start),
                fill=Palette.TEXT_SECONDARY, font=(self.UI_FONT, 10))

        self.gantt_canvas.create_text(
            30 + timeline[-1][2] * scale, y2 + 30,
            text=str(timeline[-1][2]),
            fill=Palette.TEXT_SECONDARY, font=(self.UI_FONT, 10))


    def simulate(self, show_errors=True):
        if not self.processes:
            if show_errors:
                messagebox.showerror("Error", "No processes added")
            return

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

        self.show_gantt_chart(timeline)

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