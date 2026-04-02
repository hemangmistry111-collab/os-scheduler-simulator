def sjf_non_preemptive(process_list):
    process_list.sort(key=lambda x: (x.arrival_time, x.burst_time, x.pid))

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
                (
                    process_list[i].burst_time < min_bt or
                    (
                        process_list[i].burst_time == min_bt and
                        idx != -1 and
                        (
                            process_list[i].arrival_time < process_list[idx].arrival_time or
                            (
                                process_list[i].arrival_time == process_list[idx].arrival_time and
                                process_list[i].pid < process_list[idx].pid
                            )
                        )
                    )
                )):
                min_bt = process_list[i].burst_time
                idx = i

        if idx == -1:
            next_arrival = min(
                process_list[i].arrival_time
                for i in range(n)
                if not visited[i]
            )
            if current_time < next_arrival:
                timeline.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
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
