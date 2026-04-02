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

        self.processes = []

        # ------------------ MAIN SCROLLABLE CANVAS ------------------
        main_canvas = tk.Canvas(root)
        main_canvas.pack(side="left", fill="both", expand=True)

        scroll_y = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
        scroll_y.pack(side="right", fill="y")

        main_canvas.configure(yscrollcommand=scroll_y.set)

        self.main_frame = tk.Frame(main_canvas)
        self.canvas_window = main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")

        def resize_frame(event):
            main_canvas.itemconfig(self.canvas_window, width=event.width)

        main_canvas.bind("<Configure>", resize_frame)

        self.main_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        # ------------------ Title ------------------
        tk.Label(self.main_frame,
                 text="OS Process Scheduler Simulator",
                 font=("Arial", 22, "bold")).pack(pady=10)

        # ------------------ Input Frame ------------------
        input_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        input_frame.pack(fill="x", padx=15)

        tk.Label(input_frame, text="PID").grid(row=0, column=0)
        tk.Label(input_frame, text="Arrival").grid(row=0, column=2)
        tk.Label(input_frame, text="Burst").grid(row=0, column=4)
        tk.Label(input_frame, text="Priority").grid(row=0, column=6)

        self.pid_entry = tk.Entry(input_frame, width=12)
        self.at_entry = tk.Entry(input_frame, width=12)
        self.bt_entry = tk.Entry(input_frame, width=12)
        self.pr_entry = tk.Entry(input_frame, width=12)

        self.pid_entry.grid(row=0, column=1, padx=5)
        self.at_entry.grid(row=0, column=3, padx=5)
        self.bt_entry.grid(row=0, column=5, padx=5)
        self.pr_entry.grid(row=0, column=7, padx=5)

        tk.Button(input_frame, text="Add Process",
                  command=self.add_process).grid(row=0, column=8, padx=10)

        # ------------------ Table ------------------
        table_frame = tk.Frame(self.main_frame)
        table_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.tree = ttk.Treeview(
            table_frame,
            columns=("PID", "AT", "BT", "PR"),
            show="headings"
        )

        for col in ("PID", "AT", "BT", "PR"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # ------------------ Algorithm Frame ------------------
        algo_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        algo_frame.pack(fill="x", padx=15)

        self.algo_var = tk.StringVar()

        self.algo_dropdown = ttk.Combobox(
            algo_frame,
            textvariable=self.algo_var,
            values=[
                "FCFS",
                "SJF (Non Preemptive)",
                "Round Robin",
                "Priority (Non Preemptive)",
                "SRTF (Preemptive SJF)"
            ],
            state="readonly",
            width=30
        )
        self.algo_dropdown.grid(row=0, column=0, padx=10)
        self.algo_dropdown.current(0)

        tk.Label(algo_frame, text="Time Quantum").grid(row=0, column=1)
        self.quantum_entry = tk.Entry(algo_frame, width=10)
        self.quantum_entry.grid(row=0, column=2)

        tk.Button(algo_frame, text="Simulate",
                  command=self.simulate).grid(row=0, column=3, padx=10)

        # ------------------ Results ------------------
        self.output_text = tk.Text(self.main_frame, height=8)
        self.output_text.pack(fill="both", expand=True, padx=15, pady=5)

        # ------------------ Math Solution ------------------
        self.solution_text = tk.Text(self.main_frame, height=8)
        self.solution_text.pack(fill="both", expand=True, padx=15, pady=5)

        # ------------------ Gantt Chart ------------------
        gantt_frame = tk.Frame(self.main_frame)
        gantt_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.gantt_canvas = tk.Canvas(gantt_frame, height=200, bg="white")
        self.gantt_canvas.pack(fill="both", expand=True)

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

        for pid, start, end in timeline:
            x1 = 30 + start * scale
            x2 = 30 + end * scale

            self.gantt_canvas.create_rectangle(x1, y1, x2, y2,
                                               fill="skyblue", outline="black")
            self.gantt_canvas.create_text((x1 + x2) / 2,
                                          (y1 + y2) / 2,
                                          text=pid)

            self.gantt_canvas.create_text(x1, y2 + 20, text=str(start))

        self.gantt_canvas.create_text(
            30 + timeline[-1][2] * scale,
            y2 + 20,
            text=str(timeline[-1][2])
        )

    # ------------------ Simulate ------------------
    def simulate(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes added")
            return

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