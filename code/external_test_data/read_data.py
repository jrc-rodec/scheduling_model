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
            instances.append(jobs)
    return [n_jobs, n_machines, n_workers], instances

def read_files_2():
    return None

def read(source):
    instances = []
    if source == 1:
        meta, found_instances = read_files_1()
        for instance in found_instances:
                instances.append([meta, instance])
    elif source == 2:
        instances = read_files_2()
    else:
        pass
    return instances
    
selected_source = 1

data = read(selected_source)
#print(len(data))
j = 1
for instance in data:
    i = 1
    print(f'Instance {j}: Details: {instance[0]}')
    j+=1
    for job in instance[1]:
        print(f'Operations for Job {i} are (Machine ID, Worker ID, Duration):')
        i+=1
        for operation in job:
            print(operation)
        print('\n')