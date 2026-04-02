def priority_preemptive(process_list):
    n = len(process_list)
    completed = 0
    current_time = 0
    timeline = []
    last_pid = None

    for process in process_list:
        process.remaining_time = process.burst_time
        process.start_time = -1

    while completed < n:
        idx = -1
        highest_priority = float("inf")

        for i in range(n):
            process = process_list[i]
            if (
                process.arrival_time <= current_time
                and process.remaining_time > 0
                and process.priority < highest_priority
            ):
                highest_priority = process.priority
                idx = i

        if idx == -1:
            current_time += 1
            last_pid = None
            continue

        process = process_list[idx]

        if process.start_time == -1:
            process.start_time = current_time

        if last_pid != process.pid:
            timeline.append((process.pid, current_time, current_time + 1))
        else:
            last = timeline[-1]
            timeline[-1] = (last[0], last[1], current_time + 1)

        process.remaining_time -= 1
        current_time += 1
        last_pid = process.pid

        if process.remaining_time == 0:
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
            completed += 1

    return process_list, timeline
