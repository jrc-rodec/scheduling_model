from external_test_data.read_data import read_dataset_1

def get_amount_operations_for_job(index : int, jobs) -> int:
    return len(jobs[index])

def get_available_combinations_for_operation(operation_index : int, job_index : int, jobs):
    return jobs[job_index][operation_index]

def get_available_machines_for_operation(operation_index : int, job_index : int, jobs):
    machines = []
    for operation in jobs[job_index][operation_index]:
        if operation[0] not in machines:
            machines.append[operation[0]]
    return machines

def get_available_workers_for_operation(operation_index : int, job_index : int, jobs):
    workers = []
    for operation in jobs[job_index][operation_index]:
        if operation[1] not in workers:
            workers.append(operation[1])
    return workers

def get_available_worker_for_machine_for_operation(machine_id : int, operation_index : int, job_index : int, jobs):
    workers = []
    for operation in jobs[job_index][operation_index]:
        if operation[0] == machine_id:
            if operation[1] not in workers:
                workers.append(operation[1])
    return workers

def get_duration(machine_id : int, worker_id : int, operation_index : int, job_index : int, jobs):
    for operation in jobs[job_index][operation_index]:
        if operation[0] == machine_id and operation[1] == worker_id:
            return operation[2]
    return 0

input, orders, instance = read_dataset_1(use_instance=13)
print(orders)
system_info = instance[0]
jobs = instance[1]
n_jobs = system_info[0]
n_machines = system_info[1]
n_workers = system_info[2]
# ready to start optimization
