import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.process import Process
from algorithms.fcfs import fcfs_scheduling
from algorithms.round_robin import round_robin_scheduling
from algorithms.sjf_np import sjf_non_preemptive
from algorithms.ljf_np import ljf_non_preemptive
from algorithms.priority_np import priority_non_preemptive
from algorithms.priority_p import priority_preemptive
from algorithms.srtf import srtf_scheduling


class SchedulerApp:
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

    def __init__(self, root):
        self.root = root
        self.root.title("OS Process Scheduler Simulator")
        self.root.state("zoomed")
        self.root.configure(bg="#0b0d10")

        self.processes = []
        self.selected_process_index = None
        self.last_result_rows = []
        self.last_comparison_rows = []
        self._setup_styles()

        # ------------------ MAIN SCROLLABLE CANVAS ------------------
        main_canvas = tk.Canvas(root, bg="#0b0d10", highlightthickness=0)
        main_canvas.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        scroll_y.pack(side="right", fill="y")

        main_canvas.configure(yscrollcommand=scroll_y.set)

        self.main_frame = tk.Frame(main_canvas, bg="#0b0d10")
        self.canvas_window = main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def resize_frame(event):
            main_canvas.itemconfig(self.canvas_window, width=event.width)

        main_canvas.bind("<Configure>", resize_frame)

        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        # ------------------ Title ------------------
        header_frame = tk.Frame(self.main_frame, bg="#11161c", highlightthickness=1, highlightbackground="#232a33")
        header_frame.pack(fill="x", padx=24, pady=(24, 16))

        header_text = tk.Frame(header_frame, bg="#11161c")
        header_text.pack(side="left", fill="both", expand=True, padx=24, pady=22)

        tk.Label(
            header_text,
            text="Operating Systems Scheduler Lab",
            font=("Segoe UI", 11, "bold"),
            fg="#7dd3fc",
            bg="#11161c",
        ).pack(anchor="w")
        tk.Label(
            header_text,
            text="OS Process Scheduler Simulator",
            font=("Segoe UI", 28, "bold"),
            fg="#f8fafc",
            bg="#11161c",
        ).pack(anchor="w", pady=(8, 0))
        tk.Label(
            header_text,
            text="Build workloads, compare CPU scheduling strategies, and inspect execution timelines in one place.",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#11161c",
        ).pack(anchor="w", pady=(8, 0))


        # ------------------ Input Frame ------------------
        input_frame = tk.Frame(self.main_frame, padx=22, pady=20, bg="#14181d", bd=0, highlightthickness=1, highlightbackground="#232a33")
        input_frame.pack(fill="x", padx=24, pady=(0, 14))

        tk.Label(input_frame, text="Add Process", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").grid(row=0, column=0, columnspan=10, sticky="w", pady=(0, 4))
        tk.Label(input_frame, text="Enter process details manually or load a demo workload.",
                 font=("Segoe UI", 10), fg="#7f8b99", bg="#14181d").grid(row=1, column=0, columnspan=10, sticky="w", pady=(0, 14))

        tk.Label(input_frame, text="PID", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#14181d").grid(row=2, column=0, sticky="w", pady=(0, 6))
        tk.Label(input_frame, text="Arrival", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#14181d").grid(row=2, column=2, sticky="w", pady=(0, 6))
        tk.Label(input_frame, text="Burst", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#14181d").grid(row=2, column=4, sticky="w", pady=(0, 6))
        tk.Label(input_frame, text="Priority", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#14181d").grid(row=2, column=6, sticky="w", pady=(0, 6))

        self.pid_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.at_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.bt_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.pr_entry = tk.Entry(input_frame, width=12, **self.entry_style)

        self.pid_entry.grid(row=2, column=1, padx=(0, 12), pady=(0, 6), sticky="ew")
        self.at_entry.grid(row=2, column=3, padx=(0, 12), pady=(0, 6), sticky="ew")
        self.bt_entry.grid(row=2, column=5, padx=(0, 12), pady=(0, 6), sticky="ew")
        self.pr_entry.grid(row=2, column=7, padx=(0, 12), pady=(0, 6), sticky="ew")

        self.add_update_button = tk.Button(
            input_frame,
            text="Add Process",
            command=self.add_or_update_process,
            **self.button_style
        )
        self.add_update_button.grid(row=2, column=8, padx=(6, 8), sticky="ew")

        self.cancel_edit_button = tk.Button(
            input_frame,
            text="Cancel",
            command=self.cancel_edit,
            **self.secondary_button_style
        )
        self.cancel_edit_button.grid(row=2, column=9, sticky="ew")
        self.cancel_edit_button.grid_remove()

        self.demo_button = tk.Button(
            input_frame,
            text="Load Demo Case",
            command=self.load_demo_case,
            **self.secondary_button_style
        )
        self.demo_button.grid(row=3, column=8, columnspan=2, pady=(12, 0), sticky="ew")

        for entry in (self.pid_entry, self.at_entry, self.bt_entry, self.pr_entry):
            entry.bind("<Return>", self.on_add_process_enter)

        for column in (1, 3, 5, 7, 8, 9):
            input_frame.grid_columnconfigure(column, weight=1)

        # ------------------ Table ------------------
        table_outer = tk.Frame(self.main_frame, bg="#14181d", highlightthickness=1, highlightbackground="#232a33")
        table_outer.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        table_header = tk.Frame(table_outer, bg="#14181d")
        table_header.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(table_header, text="Queued Processes", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").pack(side="left")

        table_actions = tk.Frame(table_header, bg="#14181d")
        table_actions.pack(side="right")

        tk.Button(
            table_actions,
            text="Delete Selected",
            command=self.delete_selected_process,
            **self.secondary_button_style
        ).pack(side="left", padx=(0, 8))
        tk.Button(
            table_actions,
            text="Clear All",
            command=self.clear_all_processes,
            **self.secondary_button_style
        ).pack(side="left")

        table_frame = tk.Frame(table_outer, bg="#14181d")
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.tree = ttk.Treeview(
            table_frame,
            columns=("PID", "AT", "BT", "PR"),
            show="headings",
            style="Scheduler.Treeview"
        )

        for col in ("PID", "AT", "BT", "PR"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=table_scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        table_scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        # ------------------ Algorithm Frame ------------------
        algo_frame = tk.Frame(self.main_frame, padx=22, pady=20, bg="#14181d", bd=0, highlightthickness=1, highlightbackground="#232a33")
        algo_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.algo_var = tk.StringVar()

        tk.Label(algo_frame, text="Simulation Controls", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").grid(row=0, column=0, columnspan=5, sticky="w", pady=(0, 4))
        tk.Label(algo_frame, text="Pick an algorithm, tune the controls, then simulate or compare all methods.",
                 font=("Segoe UI", 10), fg="#7f8b99", bg="#14181d").grid(row=1, column=0, columnspan=5, sticky="w", pady=(0, 14))

        self.algo_dropdown = ttk.Combobox(
            algo_frame,
            textvariable=self.algo_var,
            values=self.ALGORITHMS,
            state="readonly",
            width=30,
            style="Scheduler.TCombobox"
        )
        self.algo_dropdown.grid(row=2, column=0, padx=(0, 16), sticky="ew")
        self.algo_dropdown.current(0)

        tk.Label(algo_frame, text="Time Quantum", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#14181d").grid(row=2, column=1, sticky="w", padx=(0, 10))
        self.quantum_entry = tk.Entry(algo_frame, width=10, **self.entry_style)
        self.quantum_entry.grid(row=2, column=2, sticky="ew")
        self.quantum_entry.insert(0, "3")

        tk.Button(algo_frame, text="Simulate",
                  command=self.simulate, **self.button_style).grid(row=2, column=3, padx=(16, 0), sticky="ew")
        tk.Button(algo_frame, text="Compare All",
                  command=self.compare_algorithms, **self.secondary_button_style).grid(row=2, column=4, padx=(12, 0), sticky="ew")

        algo_frame.grid_columnconfigure(0, weight=3)
        algo_frame.grid_columnconfigure(2, weight=1)
        algo_frame.grid_columnconfigure(3, weight=1)
        algo_frame.grid_columnconfigure(4, weight=1)
        self.algo_dropdown.bind("<<ComboboxSelected>>", self.on_algorithm_change)
        self.update_quantum_state()

        summary_frame = tk.Frame(self.main_frame, bg="#0b0d10")
        summary_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.summary_cards = {}
        for card_title in ("Processes", "Algorithm", "Avg WT", "Avg TAT"):
            card = tk.Frame(summary_frame, bg="#14181d", highlightthickness=1, highlightbackground="#232a33", padx=20, pady=16)
            card.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(card, text=card_title, font=("Segoe UI", 10, "bold"),
                     fg="#7f8b99", bg="#14181d").pack(anchor="w")
            value_label = tk.Label(card, text="-", font=("Segoe UI", 18, "bold"),
                                   fg="#f9fafb", bg="#14181d")
            value_label.pack(anchor="w", pady=(6, 0))
            self.summary_cards[card_title] = value_label
        summary_frame.winfo_children()[-1].pack_configure(padx=(0, 0))
        self.update_summary_cards()

        # ------------------ Results ------------------
        output_frame = tk.Frame(self.main_frame, bg="#14181d", highlightthickness=1, highlightbackground="#232a33")
        output_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        tk.Label(output_frame, text="Results", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").pack(anchor="w", padx=20, pady=(18, 10))

        results_table_frame = tk.Frame(output_frame, bg="#14181d")
        results_table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        self.results_tree = ttk.Treeview(
            results_table_frame,
            columns=("PID", "CT", "TAT", "WT"),
            show="headings",
            style="Scheduler.Treeview",
            height=6
        )
        for col in ("PID", "CT", "TAT", "WT"):
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, anchor="center", width=120)

        results_scroll = ttk.Scrollbar(results_table_frame, orient="vertical", command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=results_scroll.set)
        self.results_tree.pack(side="left", fill="both", expand=True)
        results_scroll.pack(side="right", fill="y")

        self.averages_label = tk.Label(
            output_frame,
            text="Average Waiting Time: -    Average Turnaround Time: -",
            font=("Segoe UI", 10, "bold"),
            fg="#cbd5e1",
            bg="#14181d",
        )
        self.averages_label.pack(anchor="w", padx=20, pady=(0, 18))

        export_frame = tk.Frame(output_frame, bg="#14181d")
        export_frame.pack(fill="x", padx=20, pady=(0, 18))
        tk.Button(
            export_frame,
            text="Export Current Results",
            command=self.export_current_results,
            **self.secondary_button_style
        ).pack(side="left")

        # ------------------ Math Solution ------------------
        solution_frame = tk.Frame(self.main_frame, bg="#14181d", highlightthickness=1, highlightbackground="#232a33")
        solution_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        tk.Label(solution_frame, text="Working", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").pack(anchor="w", padx=20, pady=(18, 10))
        self.solution_text = tk.Text(solution_frame, height=8, **self.text_style)
        self.solution_text.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        comparison_frame = tk.Frame(self.main_frame, bg="#14181d", highlightthickness=1, highlightbackground="#232a33")
        comparison_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        tk.Label(comparison_frame, text="Algorithm Comparison", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").pack(anchor="w", padx=20, pady=(18, 10))

        comparison_table_frame = tk.Frame(comparison_frame, bg="#14181d")
        comparison_table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        self.comparison_tree = ttk.Treeview(
            comparison_table_frame,
            columns=("Algorithm", "Avg WT", "Avg TAT"),
            show="headings",
            style="Scheduler.Treeview",
            height=7
        )
        for col, width in (("Algorithm", 260), ("Avg WT", 120), ("Avg TAT", 120)):
            self.comparison_tree.heading(col, text=col)
            self.comparison_tree.column(col, anchor="center", width=width)

        comparison_scroll = ttk.Scrollbar(comparison_table_frame, orient="vertical", command=self.comparison_tree.yview)
        self.comparison_tree.configure(yscrollcommand=comparison_scroll.set)
        self.comparison_tree.pack(side="left", fill="both", expand=True)
        comparison_scroll.pack(side="right", fill="y")

        comparison_export_frame = tk.Frame(comparison_frame, bg="#14181d")
        comparison_export_frame.pack(fill="x", padx=20, pady=(0, 12))
        tk.Button(
            comparison_export_frame,
            text="Export Comparison",
            command=self.export_comparison_results,
            **self.secondary_button_style
        ).pack(side="left")

        self.best_algorithm_label = tk.Label(
            comparison_frame,
            text="Best Algorithm: -",
            font=("Segoe UI", 10, "bold"),
            fg="#cbd5e1",
            bg="#14181d",
        )
        self.best_algorithm_label.pack(anchor="w", padx=20, pady=(0, 18))

        # ------------------ Gantt Chart ------------------
        gantt_frame = tk.Frame(self.main_frame, bg="#14181d", highlightthickness=1, highlightbackground="#232a33")
        gantt_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        tk.Label(gantt_frame, text="Gantt Chart", font=("Segoe UI", 15, "bold"),
                 fg="#f9fafb", bg="#14181d").pack(anchor="w", padx=20, pady=(18, 6))
        tk.Label(gantt_frame, text="Execution timeline of the currently selected scheduling strategy.",
                 font=("Segoe UI", 10), fg="#7f8b99", bg="#14181d").pack(anchor="w", padx=20, pady=(0, 12))

        self.gantt_canvas = tk.Canvas(
            gantt_frame,
            height=240,
            bg="#101419",
            highlightthickness=1,
            highlightbackground="#29323c"
        )
        self.gantt_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 18))
        self.show_gantt_chart([])

        footer_frame = tk.Frame(self.main_frame, bg="#0b0d10")
        footer_frame.pack(fill="x", padx=24, pady=(0, 24))
        tk.Label(
            footer_frame,
            text="Operating Systems Mini Project  |  CPU Scheduling Simulator  |  Built with Python and Tkinter",
            font=("Segoe UI", 9),
            fg="#667281",
            bg="#0b0d10",
        ).pack(anchor="center")

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TScrollbar",
            troughcolor="#14181d",
            background="#3b4450",
            bordercolor="#14181d",
            arrowcolor="#e5e7eb",
        )
        style.configure(
            "Scheduler.Treeview",
            background="#101419",
            foreground="#e5e7eb",
            fieldbackground="#101419",
            borderwidth=0,
            rowheight=38,
            font=("Segoe UI", 10),
        )
        style.map(
            "Scheduler.Treeview",
            background=[("selected", "#243244")],
            foreground=[("selected", "#f9fafb")],
        )
        style.configure(
            "Scheduler.Treeview.Heading",
            background="#182028",
            foreground="#f3f4f6",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Scheduler.Treeview.Heading", background=[("active", "#212a34")])
        style.configure(
            "Scheduler.TCombobox",
            fieldbackground="#0f1419",
            background="#0f1419",
            foreground="#f3f4f6",
            arrowcolor="#f3f4f6",
            bordercolor="#2a3440",
            lightcolor="#2a3440",
            darkcolor="#2a3440",
            padding=10,
        )

        self.entry_style = {
            "font": ("Segoe UI", 10),
            "bg": "#0f1419",
            "fg": "#f3f4f6",
            "insertbackground": "#f3f4f6",
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": "#2a3440",
            "highlightcolor": "#38bdf8",
        }
        self.button_style = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": "#2563eb",
            "fg": "#eff6ff",
            "activebackground": "#1d4ed8",
            "activeforeground": "#ffffff",
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "padx": 18,
            "pady": 11,
        }
        self.secondary_button_style = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": "#1b222b",
            "fg": "#dbe4ee",
            "activebackground": "#26303b",
            "activeforeground": "#ffffff",
            "relief": "flat",
            "bd": 0,
            "cursor": "hand2",
            "padx": 18,
            "pady": 11,
        }
        self.text_style = {
            "font": ("Consolas", 10),
            "bg": "#101419",
            "fg": "#e5e7eb",
            "insertbackground": "#f3f4f6",
            "relief": "flat",
            "bd": 0,
            "padx": 14,
            "pady": 14,
            "highlightthickness": 1,
            "highlightbackground": "#29323c",
            "highlightcolor": "#38bdf8",
        }

    # ------------------ Add Process ------------------
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
        pid = self.pid_entry.get()
        at = self.at_entry.get()
        bt = self.bt_entry.get()
        pr = self.pr_entry.get()

        if not (pid and at.isdigit() and bt.isdigit() and pr.isdigit()):
            messagebox.showerror("Error", "Enter valid inputs")
            return

        process = Process(pid, int(at), int(bt), int(pr))

        if self.selected_process_index is None:
            self.processes.append(process)
            self.tree.insert("", "end", values=(pid, at, bt, pr))
        else:
            self.processes[self.selected_process_index] = process
            item_id = self.tree.get_children()[self.selected_process_index]
            self.tree.item(item_id, values=(pid, at, bt, pr))
            self.cancel_edit()
            self.clear_process_form()
            self.update_summary_cards()
            return

        self.clear_process_form()
        self.update_summary_cards()

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
        self.tree.delete(item_id)
        del self.processes[item_index]
        self.cancel_edit()
        self.clear_simulation_outputs()
        self.update_summary_cards()

    def clear_all_processes(self):
        self.processes.clear()
        self.tree.delete(*self.tree.get_children())
        self.cancel_edit()
        self.clear_simulation_outputs()
        self.update_summary_cards()

    def load_demo_case(self):
        self.clear_all_processes()

        for pid, at, bt, pr in self.DEMO_PROCESSES:
            process = Process(pid, at, bt, pr)
            self.processes.append(process)
            self.tree.insert("", "end", values=(pid, at, bt, pr))

        self.update_summary_cards()
        self.simulate(show_errors=False)
        self.compare_algorithms()

    def update_summary_cards(self, avg_wt="-", avg_tat="-"):
        self.summary_cards["Processes"].configure(text=str(len(self.processes)))
        self.summary_cards["Algorithm"].configure(text=self.algo_var.get() or "-")
        self.summary_cards["Avg WT"].configure(text=avg_wt)
        self.summary_cards["Avg TAT"].configure(text=avg_tat)

    def clear_simulation_outputs(self):
        self.gantt_canvas.delete("all")
        self.solution_text.delete("1.0", tk.END)
        self.results_tree.delete(*self.results_tree.get_children())
        self.averages_label.configure(text="Average Waiting Time: -    Average Turnaround Time: -")
        self.comparison_tree.delete(*self.comparison_tree.get_children())
        self.best_algorithm_label.configure(text="Best Algorithm: -")
        self.last_result_rows = []
        self.last_comparison_rows = []
        self.update_summary_cards()

    def update_quantum_state(self):
        is_round_robin = self.algo_var.get() == "Round Robin"
        quantum_state = "normal" if is_round_robin else "disabled"
        self.quantum_entry.configure(state=quantum_state)

    def on_algorithm_change(self, event=None):
        self.update_quantum_state()
        self.update_summary_cards()

        if not self.processes:
            return

        if self.algo_var.get() == "Round Robin" and not self.quantum_entry.get().isdigit():
            return

        self.simulate(show_errors=False)

    def run_algorithm(self, algorithm_name, process_list):
        if algorithm_name == "FCFS":
            return fcfs_scheduling(process_list)
        if algorithm_name == "SJF (Non Preemptive)":
            return sjf_non_preemptive(process_list)
        if algorithm_name == "LJF (Non Preemptive)":
            return ljf_non_preemptive(process_list)
        if algorithm_name == "Round Robin":
            tq = self.quantum_entry.get()
            if not tq.isdigit():
                raise ValueError("Enter valid quantum")
            return round_robin_scheduling(process_list, int(tq))
        if algorithm_name == "Priority (Non Preemptive)":
            return priority_non_preemptive(process_list)
        if algorithm_name == "Priority (Preemptive)":
            return priority_preemptive(process_list)
        if algorithm_name == "SRTF (Preemptive SJF)":
            return srtf_scheduling(process_list)
        raise ValueError("Unsupported algorithm selected")

    def compare_algorithms(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes added")
            return

        self.comparison_tree.delete(*self.comparison_tree.get_children())
        self.last_comparison_rows = []

        for algorithm_name in self.ALGORITHMS:
            process_list = [
                Process(p.pid, p.arrival_time, p.burst_time, p.priority)
                for p in self.processes
            ]

            try:
                result, _ = self.run_algorithm(algorithm_name, process_list)
            except ValueError:
                return

            avg_wt = sum(p.waiting_time for p in result) / len(result)
            avg_tat = sum(p.turnaround_time for p in result) / len(result)
            row = (algorithm_name, f"{avg_wt:.2f}", f"{avg_tat:.2f}", avg_wt, avg_tat)
            self.last_comparison_rows.append(row)
            self.comparison_tree.insert("", "end", values=row[:3])

        best_row = min(self.last_comparison_rows, key=lambda row: (row[3], row[4], row[0]))
        self.best_algorithm_label.configure(
            text=f"Best Algorithm: {best_row[0]}  |  Avg WT: {best_row[1]}  |  Avg TAT: {best_row[2]}"
        )

    def export_current_results(self):
        if not self.last_result_rows:
            messagebox.showerror("Error", "Run a simulation before exporting")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Current Results"
        )
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Algorithm", self.algo_var.get()])
            writer.writerow(["Average Waiting Time", self.summary_cards["Avg WT"].cget("text")])
            writer.writerow(["Average Turnaround Time", self.summary_cards["Avg TAT"].cget("text")])
            writer.writerow([])
            writer.writerow(["PID", "Completion Time", "Turnaround Time", "Waiting Time"])
            writer.writerows(self.last_result_rows)

        messagebox.showinfo("Export Complete", f"Results exported to:\n{file_path}")

    def export_comparison_results(self):
        if not self.last_comparison_rows:
            messagebox.showerror("Error", "Run algorithm comparison before exporting")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            title="Export Algorithm Comparison"
        )
        if not file_path:
            return

        with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["Algorithm", "Average Waiting Time", "Average Turnaround Time"])
            for algorithm_name, avg_wt, avg_tat, _, _ in self.last_comparison_rows:
                writer.writerow([algorithm_name, avg_wt, avg_tat])

        messagebox.showinfo("Export Complete", f"Comparison exported to:\n{file_path}")

    # ------------------ Gantt ------------------
    def show_gantt_chart(self, timeline):
        self.gantt_canvas.delete("all")

        if not timeline:
            self.gantt_canvas.create_text(
                420, 110,
                text="Run a simulation to view the execution timeline.",
                fill="#7f8b99",
                font=("Segoe UI", 11)
            )
            return

        scale = 44
        y1, y2 = 72, 136
        colors = ["#3b82f6", "#14b8a6", "#f59e0b", "#8b5cf6", "#ef4444", "#22c55e", "#06b6d4"]

        self.gantt_canvas.create_text(
            24, 28,
            text="Timeline",
            anchor="w",
            fill="#e2e8f0",
            font=("Segoe UI", 11, "bold")
        )
        self.gantt_canvas.create_line(24, y2 + 10, 980, y2 + 10, fill="#2a3440", width=1)

        for index, (pid, start, end) in enumerate(timeline):
            x1 = 30 + start * scale
            x2 = 30 + end * scale

            self.gantt_canvas.create_rectangle(x1, y1, x2, y2,
                                               fill=colors[index % len(colors)], outline="#0f1419", width=1)
            self.gantt_canvas.create_text((x1 + x2) / 2,
                                          (y1 + y2) / 2,
                                          text=pid,
                                          fill="#f3f4f6",
                                          font=("Segoe UI", 10, "bold"))

            self.gantt_canvas.create_text(x1, y2 + 30, text=str(start), fill="#c2c8d0", font=("Segoe UI", 10))

        self.gantt_canvas.create_text(
            30 + timeline[-1][2] * scale,
            y2 + 30,
            text=str(timeline[-1][2]),
            fill="#c2c8d0",
            font=("Segoe UI", 10)
        )

    # ------------------ Simulate ------------------
    def simulate(self, show_errors=True):
        if not self.processes:
            if show_errors:
                messagebox.showerror("Error", "No processes added")
            return

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
        execution_order = " -> ".join(pid for pid, _, _ in timeline if pid != "IDLE")
        self.solution_text.insert(tk.END, f"Execution Order: {execution_order}\n\n")

        for p in result:
            row = (p.pid, p.completion_time, p.turnaround_time, p.waiting_time)
            self.last_result_rows.append(row)
            self.results_tree.insert(
                "",
                "end",
                values=row
            )

            self.solution_text.insert(
                tk.END,
                f"{p.pid}: TAT={p.completion_time}-{p.arrival_time}={p.turnaround_time}, "
                f"WT={p.turnaround_time}-{p.burst_time}={p.waiting_time}\n"
            )

        avg_wt = sum(p.waiting_time for p in result) / len(result)
        avg_tat = sum(p.turnaround_time for p in result) / len(result)
        self.averages_label.configure(
            text=f"Average Waiting Time: {avg_wt:.2f}    Average Turnaround Time: {avg_tat:.2f}"
        )
        self.update_summary_cards(f"{avg_wt:.2f}", f"{avg_tat:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
