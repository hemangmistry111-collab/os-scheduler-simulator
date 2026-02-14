import tkinter as tk
from tkinter import ttk, messagebox

from core.process import Process
from algorithms.fcfs import fcfs_scheduling
from algorithms.round_robin import round_robin_scheduling
from algorithms.sjf_np import sjf_non_preemptive
from algorithms.priority_np import priority_non_preemptive


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Scheduler Simulator")
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

        # ------------------ Heading ------------------
        title = tk.Label(self.main_frame, text="OS Process Scheduler Simulator",
                         font=("Arial", 22, "bold"))
        title.pack(pady=10)

        # ------------------ Input Frame ------------------
        input_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        input_frame.pack(fill="x", padx=15)

        tk.Label(input_frame, text="Process ID:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(input_frame, text="Arrival Time:").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(input_frame, text="Burst Time:").grid(row=0, column=4, padx=5, pady=5)
        tk.Label(input_frame, text="Priority:").grid(row=0, column=6, padx=5, pady=5)

        self.pid_entry = tk.Entry(input_frame, width=15)
        self.pid_entry.grid(row=0, column=1, padx=5, pady=5)

        self.at_entry = tk.Entry(input_frame, width=15)
        self.at_entry.grid(row=0, column=3, padx=5, pady=5)

        self.bt_entry = tk.Entry(input_frame, width=15)
        self.bt_entry.grid(row=0, column=5, padx=5, pady=5)

        self.pr_entry = tk.Entry(input_frame, width=15)
        self.pr_entry.grid(row=0, column=7, padx=5, pady=5)

        add_btn = tk.Button(input_frame, text="Add Process", width=15, command=self.add_process)
        add_btn.grid(row=0, column=8, padx=15)

        # ------------------ Process Table ------------------
        table_frame = tk.Frame(self.main_frame, padx=10, pady=10)
        table_frame.pack(fill="both", expand=True, padx=15)

        self.tree = ttk.Treeview(table_frame, columns=("PID", "AT", "BT", "PR"), show="headings", height=7)
        self.tree.heading("PID", text="Process ID")
        self.tree.heading("AT", text="Arrival Time")
        self.tree.heading("BT", text="Burst Time")
        self.tree.heading("PR", text="Priority")

        self.tree.column("PID", width=250, anchor="center")
        self.tree.column("AT", width=250, anchor="center")
        self.tree.column("BT", width=250, anchor="center")
        self.tree.column("PR", width=250, anchor="center")

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ------------------ Algorithm Frame ------------------
        algo_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        algo_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(algo_frame, text="Select Algorithm:", font=("Arial", 12, "bold")).grid(row=0, column=0, padx=5)

        self.algo_var = tk.StringVar()

        self.algo_dropdown = ttk.Combobox(
            algo_frame,
            textvariable=self.algo_var,
            values=[
                "FCFS",
                "SJF (Non Preemptive)",
                "Round Robin",
                "Priority (Non Preemptive)"
            ],
            state="readonly",
            width=30
        )
        self.algo_dropdown.grid(row=0, column=1, padx=10)
        self.algo_dropdown.current(0)

        tk.Label(algo_frame, text="Time Quantum (RR):", font=("Arial", 11)).grid(row=0, column=2, padx=5)

        self.quantum_entry = tk.Entry(algo_frame, width=12)
        self.quantum_entry.grid(row=0, column=3, padx=5)

        simulate_btn = tk.Button(algo_frame, text="Simulate", width=12, command=self.simulate)
        simulate_btn.grid(row=0, column=4, padx=10)

        clear_btn = tk.Button(algo_frame, text="Clear All", width=12, command=self.clear_all)
        clear_btn.grid(row=0, column=5, padx=10)

        # ------------------ Results Frame ------------------
        output_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        output_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Label(output_frame, text="Results:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.output_text = tk.Text(output_frame, height=8, font=("Consolas", 12))
        self.output_text.pack(fill="both", expand=True)

        # ------------------ Mathematical Solution Frame ------------------
        solution_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        solution_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Label(solution_frame, text="Mathematical Solution (Working):", font=("Arial", 12, "bold")).pack(anchor="w")

        self.solution_text = tk.Text(solution_frame, height=10, font=("Consolas", 12))
        self.solution_text.pack(fill="both", expand=True)

        # ------------------ Gantt Chart Frame ------------------
        gantt_frame = tk.Frame(self.main_frame, padx=10, pady=10, relief="ridge", bd=2)
        gantt_frame.pack(fill="both", expand=True, padx=15, pady=10)

        tk.Label(gantt_frame, text="Gantt Chart:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.gantt_canvas = tk.Canvas(gantt_frame, bg="white", height=200)
        self.gantt_canvas.pack(side="top", fill="both", expand=True)

        gantt_scrollbar = ttk.Scrollbar(gantt_frame, orient="horizontal", command=self.gantt_canvas.xview)
        gantt_scrollbar.pack(side="bottom", fill="x")

        self.gantt_canvas.configure(xscrollcommand=gantt_scrollbar.set)

    # ------------------ Add Process ------------------
    def add_process(self):
        pid = self.pid_entry.get().strip()
        at = self.at_entry.get().strip()
        bt = self.bt_entry.get().strip()
        pr = self.pr_entry.get().strip()

        if pid == "" or at == "" or bt == "" or pr == "":
            messagebox.showerror("Error", "Please fill all fields including Priority.")
            return

        if not at.isdigit() or not bt.isdigit() or not pr.isdigit():
            messagebox.showerror("Error", "Arrival Time, Burst Time, Priority must be integers.")
            return

        process = Process(pid, int(at), int(bt), int(pr))
        self.processes.append(process)

        self.tree.insert("", "end", values=(pid, at, bt, pr))

        self.pid_entry.delete(0, tk.END)
        self.at_entry.delete(0, tk.END)
        self.bt_entry.delete(0, tk.END)
        self.pr_entry.delete(0, tk.END)

    # ------------------ Gantt Chart Drawing ------------------
    def show_gantt_chart(self, timeline):
        self.gantt_canvas.delete("all")

        start_x = 30
        y1, y2 = 50, 120
        scale = 60

        max_time = timeline[-1][2]

        for pid, start, end in timeline:
            x1 = start_x + start * scale
            x2 = start_x + end * scale

            color = "lightgray" if pid == "IDLE" else "skyblue"

            self.gantt_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black")
            self.gantt_canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2, text=pid, font=("Arial", 10, "bold"))
            self.gantt_canvas.create_text(x1, y2 + 20, text=str(start), font=("Arial", 9))

        self.gantt_canvas.create_text(start_x + max_time * scale, y2 + 20, text=str(max_time), font=("Arial", 9))

        self.gantt_canvas.configure(scrollregion=self.gantt_canvas.bbox("all"))

    # ------------------ Mathematical Solution ------------------
    def show_math_solution(self, result):
        self.solution_text.delete("1.0", tk.END)

        for p in result:
            self.solution_text.insert(tk.END, f"{p.pid}:\n")
            self.solution_text.insert(tk.END, f"ST = {p.start_time}\n")
            self.solution_text.insert(tk.END, f"CT = ST + BT = {p.start_time} + {p.burst_time} = {p.completion_time}\n")
            self.solution_text.insert(tk.END, f"TAT = CT - AT = {p.completion_time} - {p.arrival_time} = {p.turnaround_time}\n")
            self.solution_text.insert(tk.END, f"WT = TAT - BT = {p.turnaround_time} - {p.burst_time} = {p.waiting_time}\n")
            self.solution_text.insert(tk.END, "-" * 70 + "\n")

    # ------------------ Simulate ------------------
    def simulate(self):
        if len(self.processes) == 0:
            messagebox.showerror("Error", "No processes added!")
            return

        algo = self.algo_var.get()

        if algo == "FCFS":
            result, timeline = fcfs_scheduling(self.processes)

        elif algo == "SJF (Non Preemptive)":
            result, timeline = sjf_non_preemptive(self.processes)

        elif algo == "Round Robin":
            tq = self.quantum_entry.get().strip()

            if tq == "" or not tq.isdigit() or int(tq) <= 0:
                messagebox.showerror("Error", "Please enter valid Time Quantum for Round Robin.")
                return

            result, timeline = round_robin_scheduling(self.processes, int(tq))

        elif algo == "Priority (Non Preemptive)":
            result, timeline = priority_non_preemptive(self.processes)

        else:
            messagebox.showerror("Error", f"{algo} is not implemented yet.")
            return

        self.show_gantt_chart(timeline)
        self.show_math_solution(result)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "PID\tAT\tBT\tPR\tWT\tTAT\n")
        self.output_text.insert(tk.END, "-" * 80 + "\n")

        total_wt = 0
        total_tat = 0

        for p in result:
            total_wt += p.waiting_time
            total_tat += p.turnaround_time

            self.output_text.insert(
                tk.END,
                f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.priority}\t{p.waiting_time}\t{p.turnaround_time}\n"
            )

        avg_wt = total_wt / len(result)
        avg_tat = total_tat / len(result)

        self.output_text.insert(tk.END, "-" * 80 + "\n")
        self.output_text.insert(tk.END, f"Average Waiting Time: {avg_wt:.2f}\n")
        self.output_text.insert(tk.END, f"Average Turnaround Time: {avg_tat:.2f}\n")

    # ------------------ Clear All ------------------
    def clear_all(self):
        self.processes.clear()

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.output_text.delete("1.0", tk.END)
        self.solution_text.delete("1.0", tk.END)
        self.gantt_canvas.delete("all")


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
