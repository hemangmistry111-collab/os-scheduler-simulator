def priority_non_preemptive(process_list):
    n = len(process_list)
    completed = 0
    current_time = 0

    visited = [False] * n
    timeline = []

    # Reset values
    for p in process_list:
        p.start_time = 0
        p.completion_time = 0
        p.waiting_time = 0
        p.turnaround_time = 0

    while completed < n:
        idx = -1
        highest_priority = float("inf")

        # Select process with highest priority (smallest number) that has arrived
        for i in range(n):
            if process_list[i].arrival_time <= current_time and not visited[i]:
                if process_list[i].priority < highest_priority:
                    highest_priority = process_list[i].priority
                    idx = i
                elif process_list[i].priority == highest_priority:
                    # Tie breaker: earliest arrival time
                    if process_list[i].arrival_time < process_list[idx].arrival_time:
                        idx = i

        # If no process is ready
        if idx == -1:
            next_arrival = min([p.arrival_time for i, p in enumerate(process_list) if not visited[i]])
            timeline.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        process = process_list[idx]
        visited[idx] = True

        process.start_time = current_time
        process.completion_time = current_time + process.burst_time

        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time

        timeline.append((process.pid, process.start_time, process.completion_time))

        current_time = process.completion_time
        completed += 1

    return process_list, timeline
