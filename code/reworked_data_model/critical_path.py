def find_critical_path(sequence, assignments, durations):
    schedule = []
    n_machines = max(assignments)
    for _ in range(n_machines):
        schedule.append([])
    """used_machines = []
    for assignment in assignments:
        if assignment not in used_machines:
            used_machines.append(assignment)"""
    n_jobs = max(sequence)
    operation_index = [0] * n_jobs
    ends_on_workstation = [0] * n_machines
    ends_operations = [0] * n_jobs
    operations = sequence.copy()
    operations.sort()
    job_start_indices = [0] * n_jobs
    index = 1
    for i in range(1, len(operations)):
        if operations[i-1] != operations[i]:
            job_start_indices[index] = i
            index += 1
    for i in range(len(sequence)):
        job = sequence[i]
        workstation = assignments[job_start_indices[job + operation_index[job]]] # TODO: double check index
        duration = durations[job][workstation]
        start_time = max(ends_on_workstation[workstation], ends_operations[job])
        end_time = start_time + duration
        ends_on_workstation[workstation] = end_time
        ends_operations[job] = end_time
        schedule[workstation].append([job, operation_index[job], start_time, end_time])
        operation_index[job] += 1
    end_points = []
    makespan = 0
    for machine in schedule:
        machine.sort(key=lambda x: x[3])
        last = machine[-1][3]
        end_points.append(machine[-1])
        if last > makespan:
            makespan = last
    critical_path_end_points = [x for x in end_points if x[3] == makespan]


    occurences = [0] * len(sequence)
    #... count occurences
    
    p = create_p(occurences)

def create_p(occurences):
    shares = 0
    for i in range(max(occurences)+1):
        shares += occurences.count(i) * (i+1)
    share = 1 / shares
    p = [0] * len(occurences)
    for i in range(len(occurences)):
        p[i] = (occurences[i]+1) * share
    

sequence = [0, 1, 0, 1, 2, 1, 0]
assignments = [1, 1, 0, 2, 3, 3, 4]
#find_critical_path(sequence, assignments)
occurences = [0, 0, 0, 1, 1, 2, 1, 1, 2, 0] # 4 + 8 + 6 = 18
create_p(occurences)