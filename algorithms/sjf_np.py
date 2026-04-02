def sjf_non_preemptive(process_list):
    n = len(process_list)
    completed = 0
    current_time = 0
    visited = [False] * n
    timeline = []

    while completed < n:
        idx = -1
        min_bt = float("inf")

        for i in range(n):
            if (process_list[i].arrival_time <= current_time and
                not visited[i] and
                process_list[i].burst_time < min_bt):
                min_bt = process_list[i].burst_time
                idx = i

        if idx == -1:
            current_time += 1
            continue

        p = process_list[idx]
        visited[idx] = True

        p.start_time = current_time
        p.completion_time = current_time + p.burst_time

        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time

        timeline.append((p.pid, p.start_time, p.completion_time))

        current_time = p.completion_time
        completed += 1

    return process_list, timeline