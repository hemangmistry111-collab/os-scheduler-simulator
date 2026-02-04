from core.process import Process
from algorithms.fcfs import fcfs_scheduling

def main():
    processes = [
        Process("P1", 0, 5),
        Process("P2", 1, 3),
        Process("P3", 2, 8),
        Process("P4", 3, 6),
    ]

    scheduled_processes = fcfs_scheduling(processes)

    print("PID | AT | BT | WT | TAT")
    for p in scheduled_processes:
        print(f"{p.pid}  | {p.arrival_time}  | {p.burst_time}  | {p.waiting_time}  | {p.turnaround_time}")

if __name__ == "__main__":
    main()
