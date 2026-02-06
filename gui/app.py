import tkinter as tk
from tkinter import ttk, messagebox

from core.process import Process
from algorithms.fcfs import fcfs_scheduling


class SchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OS Scheduler Simulator")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.processes = []

        # ------------------ Heading ------------------
        title = tk.Label(root, text="OS Process Scheduler Simulator",
                         font=("Arial", 18, "bold"))
        title.pack(pady=10)

        # ------------------ Input Frame ------------------
        input_frame = tk.Frame(root, padx=10, pady=10, relief="ridge", bd=2)
        input_frame.pack(fill="x", padx=15)

        tk.Label(input_frame, text="Process ID:").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(input_frame, text="Arrival Time:").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(input_frame, text="Burst Time:").grid(row=0, column=4, padx=5, pady=5)

        self.pid_entry = tk.Entry(input_frame, width=10)
        self.pid_entry.grid(row=0, column=1, padx=5, pady=5)

        self.at_entry = tk.Entry(input_frame, width=10)
        self.at_entry.grid(row=0, column=3, padx=5, pady=5)

        self.bt_entry = tk.Entry(input_frame, width=10)
        self.bt_entry.grid(row=0, column=5, padx=5, pady=5)

        add_btn = tk.Button(input_frame, text="Add Process", command=self.add_process)
        add_btn.grid(row=0, column=6, padx=10)

        # ------------------ Process Table ------------------
        table_frame = tk.Frame(root, padx=10, pady=10)
        table_frame.pack(fill="x", padx=15)

        self.tree = ttk.Treeview(table_frame, columns=("PID", "AT", "BT"), show="headings", height=8)
        self.tree.heading("PID", text="Process ID")
        self.tree.heading("AT", text="Arrival Time")
        self.tree.heading("BT", text="Burst Time")

        self.tree.column("PID", width=150, anchor="center")
        self.tree.column("AT", width=150, anchor="center")
        self.tree.column("BT", width=150, anchor="center")

        self.tree.pack(side="left", fill="x")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # ------------------ Algorithm Frame ------------------
        algo_frame = tk.Frame(root, padx=10, pady=10, relief="ridge", bd=2)
        algo_frame.pack(fill="x", padx=15, pady=10)

        tk.Label(algo_frame, text="Select Algorithm:", font=("Arial", 11, "bold")).grid(row=0, column=0, padx=5)

        self.algo_var = tk.StringVar()
        self.algo_dropdown = ttk.Combobox(algo_frame, textvariable=self.algo_var,
                                          values=["FCFS"], state="readonly", width=20)
        self.algo_dropdown.grid(row=0, column=1, padx=5)
        self.algo_dropdown.current(0)

        tk.Label(algo_frame, text="Time Quantum (RR):").grid(row=0, column=2, padx=5)
        self.quantum_entry = tk.Entry(algo_frame, width=10)
        self.quantum_entry.grid(row=0, column=3, padx=5)

        simulate_btn = tk.Button(algo_frame, text="Simulate", command=self.simulate)
        simulate_btn.grid(row=0, column=4, padx=10)

        clear_btn = tk.Button(algo_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=5, padx=10)

        # ------------------ Output Frame ------------------
        output_frame = tk.Frame(root, padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, padx=15)

        tk.Label(output_frame, text="Results:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.output_text = tk.Text(output_frame, height=12, font=("Consolas", 11))
        self.output_text.pack(fill="both", expand=True)

    # ------------------ Add Process ------------------
    def add_process(self):
        pid = self.pid_entry.get().strip()
        at = self.at_entry.get().strip()
        bt = self.bt_entry.get().strip()

        if pid == "" or at == "" or bt == "":
            messagebox.showerror("Error", "Please fill all fields.")
            return

        if not at.isdigit() or not bt.isdigit():
            messagebox.showerror("Error", "Arrival Time and Burst Time must be integers.")
            return

        process = Process(pid, int(at), int(bt))
        self.processes.append(process)

        self.tree.insert("", "end", values=(pid, at, bt))

        self.pid_entry.delete(0, tk.END)
        self.at_entry.delete(0, tk.END)
        self.bt_entry.delete(0, tk.END)

    # ------------------ Simulate ------------------
    def simulate(self):
        if len(self.processes) == 0:
            messagebox.showerror("Error", "No processes added!")
            return

        algo = self.algo_var.get()

        if algo == "FCFS":
            result = fcfs_scheduling(self.processes)

        else:
            messagebox.showerror("Error", "Algorithm not implemented yet.")
            return

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, "PID\tAT\tBT\tWT\tTAT\n")
        self.output_text.insert(tk.END, "-" * 40 + "\n")

        total_wt = 0
        total_tat = 0

        for p in result:
            total_wt += p.waiting_time
            total_tat += p.turnaround_time
            self.output_text.insert(tk.END,
                                    f"{p.pid}\t{p.arrival_time}\t{p.burst_time}\t{p.waiting_time}\t{p.turnaround_time}\n")

        avg_wt = total_wt / len(result)
        avg_tat = total_tat / len(result)

        self.output_text.insert(tk.END, "-" * 40 + "\n")
        self.output_text.insert(tk.END, f"Average Waiting Time: {avg_wt:.2f}\n")
        self.output_text.insert(tk.END, f"Average Turnaround Time: {avg_tat:.2f}\n")

    # ------------------ Clear All ------------------
    def clear_all(self):
        self.processes.clear()

        for row in self.tree.get_children():
            self.tree.delete(row)

        self.output_text.delete("1.0", tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = SchedulerApp(root)
    root.mainloop()
