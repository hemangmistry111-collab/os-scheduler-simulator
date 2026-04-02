def ljf_non_preemptive(process_list):
    n = len(process_list)
    completed = 0
    current_time = 0
    visited = [False] * n
    timeline = []

    while completed < n:
        idx = -1
        max_bt = -1

        for i in range(n):
            process = process_list[i]
            if (
                process.arrival_time <= current_time
                and not visited[i]
                and process.burst_time > max_bt
            ):
                max_bt = process.burst_time
                idx = i

        if idx == -1:
            current_time += 1
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
