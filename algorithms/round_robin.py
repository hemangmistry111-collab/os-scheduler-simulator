from collections import deque


def round_robin_scheduling(process_list, time_quantum):
    process_list.sort(key=lambda x: x.arrival_time)

    n = len(process_list)
    current_time = 0
    completed = 0
    timeline = []

    queue = deque()
    index = 0

    # Reset remaining time for safety
    for p in process_list:
        p.remaining_time = p.burst_time

    while completed < n:

        # Add arrived processes into queue
        while index < n and process_list[index].arrival_time <= current_time:
            queue.append(process_list[index])
            index += 1

        # If queue is empty, CPU is idle
        if not queue:
            if index < n:
                timeline.append(("IDLE", current_time, process_list[index].arrival_time))
                current_time = process_list[index].arrival_time
            continue

        process = queue.popleft()

        start = current_time

        if process.remaining_time > time_quantum:
            current_time += time_quantum
            process.remaining_time -= time_quantum
        else:
            current_time += process.remaining_time
            process.remaining_time = 0
            process.completion_time = current_time
            completed += 1

        end = current_time
        timeline.append((process.pid, start, end))

        # Add new processes that arrived during execution
        while index < n and process_list[index].arrival_time <= current_time:
            queue.append(process_list[index])
            index += 1

        # If process not finished, push back to queue
        if process.remaining_time > 0:
            queue.append(process)

    # Calculate WT and TAT
    for p in process_list:
        p.turnaround_time = p.completion_time - p.arrival_time
        p.waiting_time = p.turnaround_time - p.burst_time

    return process_list, timeline
