def fcfs_scheduling(process_list):
    process_list.sort(key=lambda x: x.arrival_time)

    current_time = 0
    timeline = []   # For Gantt chart

    for process in process_list:
        # CPU idle case
        if current_time < process.arrival_time:
            timeline.append(("IDLE", current_time, process.arrival_time))
            current_time = process.arrival_time

        process.start_time = current_time
        process.completion_time = current_time + process.burst_time

        process.turnaround_time = process.completion_time - process.arrival_time
        process.waiting_time = process.turnaround_time - process.burst_time

        # Store execution in timeline
        timeline.append((process.pid, process.start_time, process.completion_time))

        current_time = process.completion_time

    return process_list, timeline
