import random

def to_index(job, operation, job_sequence):
    counter = -1
    index = 0
    for i in job_sequence:
        if i == job:
            counter += 1
        if counter == operation:
            return index
        index += 1
    return None

class GreedyFJSSPSolver:

    def determine_next(next_operation, durations, job_sequence, counts):
        next_durations = [0] * len(next_operation)
        min_index = float('inf')
        min_duration = float('inf')
        machine = [float('inf')] * len(next_operation)
        min_machine = float('inf')
        for i in range(len(next_operation)):
            if next_operation[i] >= counts[i]:
                continue
            index = to_index(i, next_operation[i], job_sequence)
            operation_durations = durations[index]
            # for FJSSP, use this, for FJSSP-W, extract workers
            next_durations[i] = float('inf')
            for j in range(len(operation_durations)):
                if operation_durations[j] > 0 and operation_durations[j] < next_durations[i]:
                    next_durations[i] = operation_durations[j]
                    machine[i] = j
                elif operation_durations[j] > 0 and operation_durations[j] == next_durations[i] and random.random() < 0.5:
                    next_durations[i] = operation_durations[j]
                    machine[i] = j
        for i in range(len(next_durations)):
            if next_durations[i] > 0:
                if next_durations[i] < min_duration:
                    min_duration = next_durations[i]
                    min_machine = machine[i]
                    min_index = i
                elif next_durations[i] == min_duration and random.random() < 0.5:
                    min_duration = next_durations[i]
                    min_machine = machine[i]
                    min_index = i
        return min_index, min_duration, min_machine


class GreedyFJSSPWSolver:

    pass