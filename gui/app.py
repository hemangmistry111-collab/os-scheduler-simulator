import tkinter as tk
from tkinter import ttk, messagebox

from core.process import Process
from algorithms.fcfs import fcfs_scheduling
from algorithms.round_robin import round_robin_scheduling
from algorithms.sjf_np import sjf_non_preemptive
from algorithms.priority_np import priority_non_preemptive
from algorithms.srtf import srtf_scheduling


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Process Scheduler Simulator")
        self.root.state("zoomed")
        self.root.configure(bg="#0f172a")

        self.processes = []
        self._setup_styles()

        # ------------------ MAIN SCROLLABLE CANVAS ------------------
        main_canvas = tk.Canvas(root, bg="#0f172a", highlightthickness=0)
        main_canvas.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        scroll_y.pack(side="right", fill="y")

        main_canvas.configure(yscrollcommand=scroll_y.set)

        self.main_frame = tk.Frame(main_canvas, bg="#0f172a")
        self.canvas_window = main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def resize_frame(event):
            main_canvas.itemconfig(self.canvas_window, width=event.width)

        main_canvas.bind("<Configure>", resize_frame)

        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        # ------------------ Title ------------------
        header_frame = tk.Frame(self.main_frame, bg="#0f172a")
        header_frame.pack(fill="x", padx=24, pady=(24, 12))

        tk.Label(
            header_frame,
            text="OS Process Scheduler Simulator",
            font=("Segoe UI", 26, "bold"),
            fg="#e2e8f0",
            bg="#0f172a",
        ).pack(anchor="w")
        tk.Label(
            header_frame,
            text="Build workloads, compare scheduling strategies, and inspect execution timelines.",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a",
        ).pack(anchor="w", pady=(6, 0))

        # ------------------ Input Frame ------------------
        input_frame = tk.Frame(self.main_frame, padx=20, pady=18, bg="#111827", bd=0)
        input_frame.pack(fill="x", padx=24, pady=(0, 14))

        tk.Label(input_frame, text="Add Process", font=("Segoe UI", 15, "bold"),
                 fg="#f8fafc", bg="#111827").grid(row=0, column=0, columnspan=9, sticky="w", pady=(0, 14))

        tk.Label(input_frame, text="PID", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#111827").grid(row=1, column=0, sticky="w", pady=(0, 6))
        tk.Label(input_frame, text="Arrival", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#111827").grid(row=1, column=2, sticky="w", pady=(0, 6))
        tk.Label(input_frame, text="Burst", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#111827").grid(row=1, column=4, sticky="w", pady=(0, 6))
        tk.Label(input_frame, text="Priority", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#111827").grid(row=1, column=6, sticky="w", pady=(0, 6))

        self.pid_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.at_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.bt_entry = tk.Entry(input_frame, width=12, **self.entry_style)
        self.pr_entry = tk.Entry(input_frame, width=12, **self.entry_style)

        self.pid_entry.grid(row=1, column=1, padx=(0, 12), pady=(0, 4), sticky="ew")
        self.at_entry.grid(row=1, column=3, padx=(0, 12), pady=(0, 4), sticky="ew")
        self.bt_entry.grid(row=1, column=5, padx=(0, 12), pady=(0, 4), sticky="ew")
        self.pr_entry.grid(row=1, column=7, padx=(0, 12), pady=(0, 4), sticky="ew")

        tk.Button(input_frame, text="Add Process",
                  command=self.add_process, **self.button_style).grid(row=1, column=8, padx=(6, 0), sticky="ew")

        for column in (1, 3, 5, 7, 8):
            input_frame.grid_columnconfigure(column, weight=1)

        # ------------------ Table ------------------
        table_outer = tk.Frame(self.main_frame, bg="#111827")
        table_outer.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        tk.Label(table_outer, text="Queued Processes", font=("Segoe UI", 15, "bold"),
                 fg="#f8fafc", bg="#111827").pack(anchor="w", padx=20, pady=(18, 10))

        table_frame = tk.Frame(table_outer, bg="#111827")
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

        # ------------------ Algorithm Frame ------------------
        algo_frame = tk.Frame(self.main_frame, padx=20, pady=18, bg="#111827", bd=0)
        algo_frame.pack(fill="x", padx=24, pady=(0, 14))

        self.algo_var = tk.StringVar()

        tk.Label(algo_frame, text="Simulation Controls", font=("Segoe UI", 15, "bold"),
                 fg="#f8fafc", bg="#111827").grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 14))

        self.algo_dropdown = ttk.Combobox(
            algo_frame,
            textvariable=self.algo_var,
            values=[
                "FCFS",
                "SJF (Non Preemptive)",
                "LJF (Non Preemptive)",
                "Round Robin",
                "Priority (Non Preemptive)",
                "SRTF (Preemptive SJF)"
            ],
            state="readonly",
            width=30,
            style="Scheduler.TCombobox"
        )
        self.algo_dropdown.grid(row=1, column=0, padx=(0, 16), sticky="ew")
        self.algo_dropdown.current(0)

        tk.Label(algo_frame, text="Time Quantum", font=("Segoe UI", 10, "bold"),
                 fg="#cbd5e1", bg="#111827").grid(row=1, column=1, sticky="w", padx=(0, 10))
        self.quantum_entry = tk.Entry(algo_frame, width=10, **self.entry_style)
        self.quantum_entry.grid(row=1, column=2, sticky="ew")

        tk.Button(algo_frame, text="Simulate",
                  command=self.simulate, **self.button_style).grid(row=1, column=3, padx=(16, 0), sticky="ew")

        algo_frame.grid_columnconfigure(0, weight=3)
        algo_frame.grid_columnconfigure(2, weight=1)
        algo_frame.grid_columnconfigure(3, weight=1)

        # ------------------ Results ------------------
        output_frame = tk.Frame(self.main_frame, bg="#111827")
        output_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        tk.Label(output_frame, text="Results", font=("Segoe UI", 15, "bold"),
                 fg="#f8fafc", bg="#111827").pack(anchor="w", padx=20, pady=(18, 10))
        self.output_text = tk.Text(output_frame, height=8, **self.text_style)
        self.output_text.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        # ------------------ Math Solution ------------------
        solution_frame = tk.Frame(self.main_frame, bg="#111827")
        solution_frame.pack(fill="both", expand=True, padx=24, pady=(0, 14))

        tk.Label(solution_frame, text="Working", font=("Segoe UI", 15, "bold"),
                 fg="#f8fafc", bg="#111827").pack(anchor="w", padx=20, pady=(18, 10))
        self.solution_text = tk.Text(solution_frame, height=8, **self.text_style)
        self.solution_text.pack(fill="both", expand=True, padx=20, pady=(0, 18))

        # ------------------ Gantt Chart ------------------
        gantt_frame = tk.Frame(self.main_frame, bg="#111827")
        gantt_frame.pack(fill="both", expand=True, padx=24, pady=(0, 24))

        tk.Label(gantt_frame, text="Gantt Chart", font=("Segoe UI", 15, "bold"),
                 fg="#f8fafc", bg="#111827").pack(anchor="w", padx=20, pady=(18, 10))

        self.gantt_canvas = tk.Canvas(
            gantt_frame,
            height=220,
            bg="#0b1220",
            highlightthickness=1,
            highlightbackground="#1e293b"
        )
        self.gantt_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 18))

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "TScrollbar",
            troughcolor="#111827",
            background="#475569",
            bordercolor="#111827",
            arrowcolor="#e2e8f0",
        )
        style.configure(
            "Scheduler.Treeview",
            background="#0b1220",
            foreground="#e2e8f0",
            fieldbackground="#0b1220",
            borderwidth=0,
            rowheight=34,
            font=("Segoe UI", 10),
        )
        style.map(
            "Scheduler.Treeview",
            background=[("selected", "#1d4ed8")],
            foreground=[("selected", "#eff6ff")],
        )
        style.configure(
            "Scheduler.Treeview.Heading",
            background="#1e293b",
            foreground="#f8fafc",
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
        )
        style.map("Scheduler.Treeview.Heading", background=[("active", "#334155")])
        style.configure(
            "Scheduler.TCombobox",
            fieldbackground="#0b1220",
            background="#0b1220",
            foreground="#e2e8f0",
            arrowcolor="#e2e8f0",
            bordercolor="#334155",
            lightcolor="#334155",
            darkcolor="#334155",
            padding=8,
        )

        self.entry_style = {
            "font": ("Segoe UI", 10),
            "bg": "#0b1220",
            "fg": "#f8fafc",
            "insertbackground": "#f8fafc",
            "relief": "flat",
            "bd": 0,
            "highlightthickness": 1,
            "highlightbackground": "#334155",
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
            "padx": 16,
            "pady": 10,
        }
        self.text_style = {
            "font": ("Consolas", 10),
            "bg": "#0b1220",
            "fg": "#dbeafe",
            "insertbackground": "#f8fafc",
            "relief": "flat",
            "bd": 0,
            "padx": 12,
            "pady": 12,
            "highlightthickness": 1,
            "highlightbackground": "#1e293b",
            "highlightcolor": "#38bdf8",
        }

    # ------------------ Add Process ------------------
    def add_process(self):
        pid = self.pid_entry.get()
        at = self.at_entry.get()
        bt = self.bt_entry.get()
        pr = self.pr_entry.get()

        if not (pid and at.isdigit() and bt.isdigit() and pr.isdigit()):
            messagebox.showerror("Error", "Enter valid inputs")
            return

        process = Process(pid, int(at), int(bt), int(pr))
        self.processes.append(process)
        self.tree.insert("", "end", values=(pid, at, bt, pr))

        self.pid_entry.delete(0, tk.END)
        self.at_entry.delete(0, tk.END)
        self.bt_entry.delete(0, tk.END)
        self.pr_entry.delete(0, tk.END)

    # ------------------ Gantt ------------------
    def show_gantt_chart(self, timeline):
        self.gantt_canvas.delete("all")

        scale = 40
        y1, y2 = 60, 120
        colors = ["#38bdf8", "#22c55e", "#f59e0b", "#f97316", "#a78bfa", "#f43f5e"]

        for index, (pid, start, end) in enumerate(timeline):
            x1 = 30 + start * scale
            x2 = 30 + end * scale

            self.gantt_canvas.create_rectangle(x1, y1, x2, y2,
                                               fill=colors[index % len(colors)], outline="#020617", width=2)
            self.gantt_canvas.create_text((x1 + x2) / 2,
                                          (y1 + y2) / 2,
                                          text=pid,
                                          fill="#020617",
                                          font=("Segoe UI", 10, "bold"))

            self.gantt_canvas.create_text(x1, y2 + 24, text=str(start), fill="#cbd5e1", font=("Segoe UI", 10))

        self.gantt_canvas.create_text(
            30 + timeline[-1][2] * scale,
            y2 + 20,
            text=str(timeline[-1][2]),
            fill="#cbd5e1",
            font=("Segoe UI", 10)
        )

    # ------------------ Simulate ------------------
    def simulate(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes added")
            return

        process_list = [
            Process(p.pid, p.arrival_time, p.burst_time, p.priority)
            for p in self.processes
        ]

        algo = self.algo_var.get()

        if algo == "FCFS":
            result, timeline = fcfs_scheduling(self.processes)
        elif algo == "SJF (Non Preemptive)":
            result, timeline = sjf_non_preemptive(self.processes)
        elif algo == "Round Robin":
            tq = self.quantum_entry.get()
            if not tq.isdigit():
                messagebox.showerror("Error", "Enter valid quantum")
                return
            result, timeline = round_robin_scheduling(self.processes, int(tq))
        elif algo == "Priority (Non Preemptive)":
            result, timeline = priority_non_preemptive(self.processes)
        elif algo == "SRTF (Preemptive SJF)":
            result, timeline = srtf_scheduling(self.processes)

        self.show_gantt_chart(timeline)

        self.output_text.delete("1.0", tk.END)
        self.solution_text.delete("1.0", tk.END)

        for p in result:
            self.output_text.insert(
                tk.END,
                f"{p.pid} | WT={p.waiting_time} | TAT={p.turnaround_time}\n"
            )

            self.solution_text.insert(
                tk.END,
                f"{p.pid}: TAT={p.completion_time}-{p.arrival_time}={p.turnaround_time}, "
                f"WT={p.turnaround_time}-{p.burst_time}={p.waiting_time}\n"
            )


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
