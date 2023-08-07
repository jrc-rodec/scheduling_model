from oo_sequence_ga import Individual
from multiprocessing import Queue, freeze_support

def evaluate_only_parallel(individual, queue, operation_amount):
        next_operations = [0] * operation_amount
        end_on_workstations = [0] * len(Individual.base_durations[0])
        end_times = [-1] * len(Individual.required_operations)
        gaps_on_workstations :list[list[tuple[int, int]]]= []
        for i in range(len(Individual.base_durations[0])):
            gaps_on_workstations.append([])
        for i in range(len(individual.sequence)):
            job = individual.sequence[i]
            operation = next_operations[job]
            start_index = 0
            for j in range(len(Individual.required_operations)):
                if Individual.required_operations[j] == job:
                    start_index = j
                    break
                start_index = j
            start_index += operation
            next_operations[job] += 1
            workstation = individual.workstations[start_index]
            duration = individual.durations[start_index]
            offset = 0
            #min_start_job = 0
            if operation > 0:
                # check end on prev workstation NOTE: if there is a previous operation of this job, start_index-1 should never be out of range
                offset = max(0, end_times[start_index-1] - end_on_workstations[workstation])
                #min_start_job = end_times[start_index-1]
            end_times[start_index] = end_on_workstations[workstation]+duration+offset
            end_on_workstations[workstation] = end_times[start_index]
        queue.put(max(end_times))

"""def adjust_individual_parallel(individual : Individual, operation_amount):
    class Gap:
        def __init__(self, start, end, before_operation):
            self.start = start
            self.end = end
            self.preceeds_operation = before_operation
    gaps : list[list[Gap]] = []
    available_workstations = []
    n_workstations = len(Individual.base_durations[0])
    for w in range(n_workstations):
        if w not in available_workstations:
            available_workstations.append(w)
    for _ in range(n_workstations):
        gaps.append([])
    end_times_on_workstations : list[int] = [0] * n_workstations
    end_times_of_operations : list[int] = [0] * len(Individual.required_operations)
    next_operation = [0] * len(operation_amount)
    # build schedule
    for i in range(len(individual.sequence)):
        job = individual.sequence[i]
        operation = next_operation[job]
        operation_index = 0
        for j in range(len(Individual.required_operations)):
            if Individual.required_operations[j] == job:
                operation_index = j
                break
            operation_index = j
        operation_index += operation
        workstation = individual.workstations[operation_index]
        next_operation[job] += 1
        duration = individual.durations[operation_index]
        inserted : bool = False
        for gap in gaps[workstation]:
            if gap.end - gap.start >= duration:
                # found a gap, check job seqeunce
                if operation_index == 0 or (Individual.required_operations[operation_index-1] == Individual.required_operations[operation_index] and end_times_of_operations[operation_index-1] <= gap.end - duration): # AND pre_operation finishes before gap.end - duration
                    # gap can be used
                    inserted = True
                    start = 0 if operation_index == 0 else min(gap.start, end_times_of_operations[operation_index-1])
                    end = start + duration
                    if gap.end - end > 0:
                        # new gap
                        new_gap = Gap(end, gap.end, operation_index)
                        gaps[workstation].append(new_gap)
                    end_times_of_operations[operation_index] = end
                    # swap operations in sequence vector
                    job_swap = Individual.required_operations[gap.preceeds_operation]
                    swap_operation_index = 0
                    swap_start_index = 0
                    for j in range(len(Individual.required_operations)):
                        if Individual.required_operations[j] == job_swap:
                            swap_start_index = j
                            break
                        swap_start_index = j
                    swap_operation_index = gap.preceeds_operation - swap_start_index
                    count = 0
                    swap_individual_index = 0
                    for j in range(len(individual.sequence)):
                        if individual.sequence[j] == job_swap:
                            if count == swap_operation_index:
                                swap_individual_index = j
                                break
                            count += 1
                            swap_individual_index = j
                    tmp = individual.sequence[swap_individual_index]
                    individual.sequence[swap_individual_index] = individual.sequence[i]
                    individual.sequence[i] = tmp
                    # remove old gap
                    gaps[workstation].remove(gap)
                    # done
                    break
        if not inserted:
            job_min_start = 0
            if operation_index != 0 and Individual.required_operations[operation_index-1] == Individual.required_operations[operation_index]:
                job_min_start = end_times_of_operations[operation_index-1]
            if job_min_start > end_times_on_workstations[workstation]:
                # new gap
                gaps[workstation].append(Gap(job_min_start, job_min_start + duration, operation_index))
                end_times_on_workstations[workstation] = job_min_start + duration
            else:
                end_times_on_workstations[workstation] += duration
            end_times_of_operations[operation_index] = end_times_on_workstations[workstation]"""

def evaluate_and_adjust_parallel(individual : Individual, q : Queue, operation_amount : int):
    class Gap:
        def __init__(self, start, end, before_operation):
            self.start = start
            self.end = end
            self.preceeds_operation = before_operation
    gaps : list[list[Gap]] = []
    available_workstations = []
    n_workstations = len(Individual.base_durations[0])
    for w in range(n_workstations):
        if w not in available_workstations:
            available_workstations.append(w)
    for _ in range(n_workstations):
        gaps.append([])
    end_times_on_workstations : list[int] = [0] * n_workstations
    end_times_of_operations : list[int] = [0] * len(Individual.required_operations)
    next_operation = [0] * len(operation_amount)
    # build schedule
    for i in range(len(individual.sequence)):
        job = individual.sequence[i]
        operation = next_operation[job]
        operation_index = 0
        for j in range(len(Individual.required_operations)):
            if Individual.required_operations[j] == job:
                operation_index = j
                break
            operation_index = j
        operation_index += operation
        workstation = individual.workstations[operation_index]
        next_operation[job] += 1
        duration = individual.durations[operation_index]
        inserted : bool = False
        for gap in gaps[workstation]:
            if gap.end - gap.start >= duration:
                # found a gap, check job seqeunce
                if operation_index == 0 or (Individual.required_operations[operation_index-1] == Individual.required_operations[operation_index] and end_times_of_operations[operation_index-1] <= gap.end - duration): # AND pre_operation finishes before gap.end - duration
                    # gap can be used
                    inserted = True
                    start = 0 if operation_index == 0 else min(gap.start, end_times_of_operations[operation_index-1])
                    end = start + duration
                    if gap.end - end > 0:
                        # new gap
                        new_gap = Gap(end, gap.end, operation_index)
                        gaps[workstation].append(new_gap)
                    end_times_of_operations[operation_index] = end
                    # swap operations in sequence vector
                    job_swap = Individual.required_operations[gap.preceeds_operation]
                    swap_operation_index = 0
                    swap_start_index = 0
                    for j in range(len(Individual.required_operations)):
                        if Individual.required_operations[j] == job_swap:
                            swap_start_index = j
                            break
                        swap_start_index = j
                    swap_operation_index = gap.preceeds_operation - swap_start_index
                    count = 0
                    swap_individual_index = 0
                    for j in range(len(individual.sequence)):
                        if individual.sequence[j] == job_swap:
                            if count == swap_operation_index:
                                swap_individual_index = j
                                break
                            count += 1
                            swap_individual_index = j
                    tmp = individual.sequence[swap_individual_index]
                    individual.sequence[swap_individual_index] = individual.sequence[i]
                    individual.sequence[i] = tmp
                    # remove old gap
                    gaps[workstation].remove(gap)
                    # done
                    break
        if not inserted:
            job_min_start = 0
            if operation_index != 0 and Individual.required_operations[operation_index-1] == Individual.required_operations[operation_index]:
                job_min_start = end_times_of_operations[operation_index-1]
            if job_min_start > end_times_on_workstations[workstation]:
                # new gap
                gaps[workstation].append(Gap(job_min_start, job_min_start + duration, operation_index))
                end_times_on_workstations[workstation] = job_min_start + duration
            else:
                end_times_on_workstations[workstation] += duration
            end_times_of_operations[operation_index] = end_times_on_workstations[workstation]

    next_operations = [0] * operation_amount
    end_on_workstations = [0] * len(Individual.base_durations[0])
    end_times = [-1] * len(Individual.required_operations)
    gaps_on_workstations :list[list[tuple[int, int]]]= []
    for i in range(len(Individual.base_durations[0])):
        gaps_on_workstations.append([])
    for i in range(len(individual.sequence)):
        job = individual.sequence[i]
        operation = next_operations[job]
        start_index = 0
        for j in range(len(Individual.required_operations)):
            if Individual.required_operations[j] == job:
                start_index = j
                break
            start_index = j
        start_index += operation
        next_operations[job] += 1
        workstation = individual.workstations[start_index]
        duration = individual.durations[start_index]
        offset = 0
        #min_start_job = 0
        if operation > 0:
            # check end on prev workstation NOTE: if there is a previous operation of this job, start_index-1 should never be out of range
            offset = max(0, end_times[start_index-1] - end_on_workstations[workstation])
            #min_start_job = end_times[start_index-1]
        end_times[start_index] = end_on_workstations[workstation]+duration+offset
        end_on_workstations[workstation] = end_times[start_index]
    individual.fitness = max(end_times)
    q.put(individual)

if __name__ == '__main__':
    freeze_support()