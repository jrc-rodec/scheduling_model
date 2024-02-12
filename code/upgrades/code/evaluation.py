from visualize import visualizer_for_schedule, get_colors_distinctipy

def get_jobs(sequence : list[int]):
    jobs = []
    for i in range(len(sequence)):
        if sequence[i] not in jobs:
            jobs.append(i)
    return jobs

def get_data(sequence : list[int], assignments : list[int], durations : list[list[int]], required_operations : list[int]):
    n_machines = len(durations[0])
    jobs = get_jobs(sequence)
    job_start_indices = [0]
    for i in range(1, len(required_operations)):
        if required_operations[i] != required_operations[i-1]:
            job_start_indices.append(i)
    return n_machines, jobs, job_start_indices

def get_start_end_times(jobs, n_machines, job_start_indices, sequence, assignments, durations):
    next_operations = [0] * len(jobs)
    end_on_machines = [0] * n_machines
    start_times = [0] * len(sequence)
    end_times = [-1] * len(sequence)
    for i in range(len(sequence)):
        job = sequence[i]
        operation = next_operations[job]
        operation_index = job_start_indices[job] + operation
        next_operations[job] += 1
        machine = assignments[operation_index]
        duration = durations[operation_index][machine]
        offset = 0
        min_start_job = 0
        if operation > 0:
            offset = max(0, end_times[operation_index-1] - end_on_machines[machine])
            min_start_job = end_times[operation_index-1]
        start_times[operation_index] = end_on_machines[machine] + offset
        end_times[operation_index] = start_times[operation_index] + duration
        end_on_machines[machine] = end_times[operation_index]
    return start_times, end_times

#NOTE: assume feasible solution
def makespan(sequence : list[int], assignments : list[int], durations : list[list[int]], required_operations : list[int]):
    n_machines, jobs, job_start_indices = get_data(sequence, assignments, durations, required_operations)
    start_times, end_times = get_start_end_times(jobs, n_machines, job_start_indices, sequence, assignments, durations)
    # makespan very simple
    return max(end_times)

def idle_time(sequence : list[int], assignments : list[int], durations : list[list[int]], required_operations : list[int]):
    n_machines, jobs, job_start_indices = get_data(sequence, assignments, durations, required_operations)
    start_times, end_times = get_start_end_times(jobs, n_machines, job_start_indices, sequence, assignments, durations)
    last_end_on_machine = [0] * n_machines
    idle_time = 0
    for i in range(len(start_times)):
        machine = assignments[i]
        idle_time += start_times[i] - last_end_on_machine[machine] # add gaps
        last_end_on_machine[machine] = end_times[i]
    makespan = max(end_times)
    for i in range(len(last_end_on_machine)):
        # add gaps after last finished operation to end of production plan
        idle_time += makespan - last_end_on_machine[i]
    return idle_time

def is_same_job(operationA, operationB, required_operations):
    return required_operations[operationA] == required_operations[operationB]

def queue_time(sequence : list[int], assignments : list[int], durations : list[list[int]], required_operations : list[int]):
    n_machines, jobs, job_start_indices = get_data(sequence, assignments, durations, required_operations)
    start_times, end_times = get_start_end_times(jobs, n_machines, job_start_indices, sequence, assignments, durations)
    queue_time = 0
    for i in range(1, len(start_times)):
        if is_same_job(i, i-1, required_operations):
            queue_time += start_times[i] - end_times[i-1]
    return queue_time

def predefine_colors(sequence):
    jobs = get_jobs(sequence)
    return get_colors_distinctipy(len(jobs))

def visualize(sequence, assignments, durations, required_operations, makespan, idle_time, queue_time, source, instance, pre_colors = None, title_prefix : str = ''):
    n_machines, jobs, job_start_indices = get_data(sequence, assignments, durations, required_operations)
    start_times, end_times = get_start_end_times(jobs, n_machines, job_start_indices, sequence, assignments, durations)
    visualizer_for_schedule(start_times, end_times, sequence, assignments, durations, required_operations, makespan, idle_time, queue_time, source, instance, pre_colors, title_prefix)

def show_plots():
    import pylab
    pylab.show()

if __name__ == '__main__':
    """required_operations = [0, 0, 0, 1, 1, 2, 3, 3, 4, 4, 5, 5, 6]
    job_start_indices = [0]
    for i in range(1, len(required_operations)):
        if required_operations[i] != required_operations[i-1]:
            job_start_indices.append(i)
    print(job_start_indices)"""
    #TESTING
    pool = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
    evaluations= [
        [0, 0, 0],
        [2, 1, 3],
        [1, 2, 4],
        [4, 4, 2],
        [3, 3, 1],
        [5, 5, 5],
        [0, 1, 4]
    ]
    n_options = 5
    n_best_by_makespan = [(x, y) for y, x in sorted(zip(evaluations, pool), key=lambda z: z[0][0])][:n_options]
    n_best_by_idle_time = [(x, y) for y, x in sorted(zip(evaluations, pool), key=lambda z: z[0][1])][:n_options]
    n_best_by_queue_time = [(x, y) for y, x in sorted(zip(evaluations, pool), key=lambda z: z[0][2])][:n_options]
    print(n_best_by_makespan)
    print(n_best_by_idle_time)
    print(n_best_by_queue_time)
    solutions = dict()
    for i in range(n_options):
        if n_best_by_makespan[i][0] not in solutions:
            solutions[n_best_by_makespan[i][0]] = [0, 0, 0]
        if n_best_by_idle_time[i][0] not in solutions:
            solutions[n_best_by_idle_time[i][0]] = [0, 0, 0]
        if n_best_by_queue_time[i][0] not in solutions:
            solutions[n_best_by_queue_time[i][0]] = [0, 0, 0]
    # sum ranks
    for i in range(n_options):
        solutions[n_best_by_makespan[i][0]][0] = i
        solutions[n_best_by_idle_time[i][0]][1] = i
        solutions[n_best_by_queue_time[i][0]][2] = i
    print(solutions)
    for key in solutions.keys():
        print(f'{key} Average Rank: {sum(solutions[key])/len(solutions[key])}')
    sorted_solutions = sorted(solutions.keys(), key=lambda x: sum(solutions[x])/len(solutions[x]))
    print(sorted_solutions)

    print(str([1, 2, 3, 4, 5]))