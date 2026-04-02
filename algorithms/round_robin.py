from collections import deque

def round_robin_scheduling(process_list, quantum):
    queue = deque()
    timeline = []
    current_time = 0
    completed = 0
    n = len(process_list)

    process_list.sort(key=lambda x: x.arrival_time)

    for p in process_list:
        p.remaining_time = p.burst_time

    i = 0

    while completed < n:
        while i < n and process_list[i].arrival_time <= current_time:
            queue.append(process_list[i])
            i += 1

        if not queue:
            current_time += 1
            continue

        p = queue.popleft()

        start = current_time
        execute_time = min(quantum, p.remaining_time)
        current_time += execute_time
        p.remaining_time -= execute_time

        timeline.append((p.pid, start, current_time))

        while i < n and process_list[i].arrival_time <= current_time:
            queue.append(process_list[i])
            i += 1

        if p.remaining_time > 0:
            queue.append(p)
        else:
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed += 1

    return process_list, timeline