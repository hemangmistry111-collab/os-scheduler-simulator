def srtf_scheduling(process_list):
    n = len(process_list)
    completed = 0
    current_time = 0
    timeline = []

    for p in process_list:
        p.remaining_time = p.burst_time
        p.start_time = -1

    last_pid = None

    while completed < n:
        idx = -1
        min_remaining = float("inf")

        for i in range(n):
            if (process_list[i].arrival_time <= current_time and
                process_list[i].remaining_time > 0 and
                process_list[i].remaining_time < min_remaining):
                min_remaining = process_list[i].remaining_time
                idx = i

        if idx == -1:
            current_time += 1
            continue

        p = process_list[idx]

        if p.start_time == -1:
            p.start_time = current_time

        if last_pid != p.pid:
            timeline.append((p.pid, current_time, current_time + 1))
        else:
            last = timeline[-1]
            timeline[-1] = (last[0], last[1], current_time + 1)

        p.remaining_time -= 1
        current_time += 1
        last_pid = p.pid

        if p.remaining_time == 0:
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed += 1

    return process_list, timeline