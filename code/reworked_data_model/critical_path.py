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
    critical_path_end_points = []#[x for x in end_points if x[3] == makespan]
    for i in range(len(end_points)):
        if end_points[3] == makespan:
            critical_path_end_points.append(i)
    # move backwards
    occurence = [0] * len(sequence) # count how often each operation appears in the critical paths
    for i in range(len(critical_path_end_points)):
        current = schedule[critical_path_end_points[i]][-1]
        machine_index = len(schedule[critical_path_end_points[i]])-1
        while current:
            occurence[job_start_indices[current[0]] + current[1]] += 1
            machine_pre = schedule[critical_path_end_points[i]][machine_index] if machine_index > 0 else None
            if current[1] > 0:
                machine = assignments[job_start_indices[current[0]]]
                for operation in schedule[machine]:
                    if operation[0] == current[0] and current[1]-1 == operation[1]:
                        sequence_pre = operation
                        break
            else:
                sequence_pre = None 
            if machine_pre != None and sequence_pre != None:
                current = machine_pre if machine_pre[3] > sequence_pre[3] else sequence_pre
            elif machine_pre != None:
                current = machine_pre
            elif sequence_pre != None:
                current = sequence_pre
            else:
                current = None
            operation_index[current[0]] = max(0, operation_index[current[0]]-1)
            machine_index = max(0, machine_index-1)
    critical_path_end_points = [x for x in end_points if x[3] == makespan]


    occurences = [0] * len(sequence)
    #... count occurences
    
    #p = create_p(occurences)
    p = norm_probabilities(occurences)

def create_p(occurences):
    shares = 0
    for i in range(max(occurences)+1):
        shares += occurences.count(i) * (i+1)
    share = 1 / shares
    p = [0] * len(occurences)
    for i in range(len(occurences)):
        p[i] = (occurences[i]+1) * share

def norm_probabilities(occurences):
    shares = [o + 1 for o in occurences]
    s = sum(shares)
    return [(x+1) / s for x in occurences]
    

sequence = [0, 1, 0, 1, 2, 1, 0]
assignments = [1, 1, 0, 2, 3, 3, 4]
#find_critical_path(sequence, assignments)
occurences = [0, 0, 0, 1, 1, 2, 1, 1, 2, 0] # 4 + 8 + 6 = 18
create_p(occurences)

print(sum(norm_probabilities(occurences)))