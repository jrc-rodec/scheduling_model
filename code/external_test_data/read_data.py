import random

def read_operation_on_machine(data, index):
    n_machines = int(data[index])
    index += 1
    new_index = index
    jobs = []
    for i in range(n_machines):
        machine_id = int(data[index])
        index += 1
        n_workers = int(data[index])
        index += 1
        operation_durations = []
        for j in range(n_workers):
            worker_id = int(data[index])
            index += 1
            duration = int(data[index])
            index += 1
            operation_durations.append([machine_id, worker_id, duration])
        jobs.append(operation_durations)
    return jobs, index

def read_files_1():
    jobs = []
    filenames = []
    instances = []
    for i in range(1, 10):
        filenames.append(f'external_test_data\\1\\SFJW\\SFJW-0{i}.txt')
    filenames.append('external_test_data\\1\\SFJW\\SFJW-10.txt')
    for i in range(1, 8):
        if not i == 5 and not i == 6 and not i == 7:
            filenames.append(f'external_test_data\\1\\MFJW\\MFJW-0{i}.txt')
    for filename in filenames:
            lines = list()
            file = open(filename, 'r')
            print(f'Reading: {filename}')
            lines = file.readlines()
            jobs = []
            if len(lines) > 0:
                base_data = lines[0].split(' ')
                n_jobs = int(base_data[0])
                n_machines = int(base_data[1])
                n_workers = int(base_data[2])
                j_id = 1
                for line in lines[1:]:
                    data = line.split(' ')
                    n_operations_for_job = int(data[0])
                    start_index = 1
                    operations = []
                    for i in range(n_operations_for_job):
                        operation_data, start_index = read_operation_on_machine(data, start_index)
                        operations.append(operation_data)    

                    j_id += 1
                    jobs.append(operations)
            instances.append([[n_jobs, n_machines, n_workers], jobs])
    return instances

def read_files_2():
    return None

def read(source):
    instances = []
    if source == 1:
        found_instances = read_files_1()
        for instance in found_instances:
                instances.append(instance)
    elif source == 2:
        instances = read_files_2()
    else:
        pass
    return instances

def generate_orders(instance, amount, earliest_date, last_date):
    meta = instance[0]
    jobs = instance[1]
    orders = []
    for i in range(amount):
        orders.append([random.randint(0, len(jobs)-1), random.randint(earliest_date, last_date), i])
    return orders

def read_dataset_1(use_instance : int = 13, order_amount : int = 100, earliest_time : int = 500, planning_horizon : int = 10000):
    selected_source = 1

    data = read(selected_source)
    # use_instance = 13 # between 0 and 13 for example data 1
    instance = data[use_instance]
    order_amount = 10 # how many orders should be generated
    # earliest_time = 500 # can not expect delivery before 50 time units into the schedule are done
    # planning_horizon = 10000 # what is the last possible date for orders' delivery date
    orders = generate_orders(instance, order_amount, earliest_time, planning_horizon)
    #print(instance[1][0]) # print operations of job 1
    #print(instance[1][0][0]) # print possibilities for operation 1 of the operations of job 1 (which machines (first index), which workers per machine (second index), how long (3.)))
    #print(f'Generated orders(<job, delivery time>):\n{orders}')
    input = []
    meta = instance[0] # amount of jobs (not needed), amount of machines, amount of workers
    jobs = instance[1]
    for order in orders:
        for i in range(len(jobs[order[0]])): # amount of necessary operations for job n
            input.append([0,0,0])
    return input, orders, instance