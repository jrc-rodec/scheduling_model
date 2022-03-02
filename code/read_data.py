import random

from models import Workstation, Resource, Task, Recipe, SimulationEnvironment
import pymzn

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

def read_file(filename):
    file = open(filename, 'r')
    print(f'Reading: {filename}')
    return file.readlines()
    
def read_files_1():
    jobs = []
    filenames = []
    instances = []
    import os
    import inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    targetdir = currentdir + '\\external_test_data\\1\\SFJW\\'
    mfjwdir = currentdir + '\\external_test_data\\1\\MFJW\\'
    for i in range(1, 10):
        filenames.append(f'{targetdir}SFJW-0{i}.txt')
    filenames.append(f'{targetdir}SFJW-10.txt')
    for i in range(1, 8):
        if not i == 5 and not i == 6 and not i == 7:
            filenames.append(f'{mfjwdir}MFJW-0{i}.txt')
    for filename in filenames:
            lines = read_file(filename)
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

def read_files_3():
    jobs = []
    filenames = []
    instances = []
    for i in range(10): # just read 00 - 09 for now
        filenames.append(f'external_test_data\\3\\rcpsp\\0{i}.dzn')
    for filename in filenames:
        # lines = read_file(filename)
        data = pymzn.dzn2dict(filename)
        n_resources = data['n_res']
        resources_state = data['rc'] # amount of available resources per resource (ID 0 - n)
        n_tasks = data['n_tasks']
        durations = data['d'] # duration per task (ID 0 - n)
        rr = data['rr'] # resource consumption for each task, for each resource ( 2D array -> row = resource, col = task consumption)
        succession_tasks = data['suc'] # determines if a task has follow up tasks or not
        instances.append([n_resources, resources_state, n_tasks, durations, rr, succession_tasks])
    return instances

def read(source):
    instances = []
    if source == 1:
        found_instances = read_files_1()
        for instance in found_instances:
                instances.append(instance)
    elif source == 2:
        instances = read_files_2()
    elif source == 3:
        instances = read_files_3()
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
    instance = data[use_instance]
    orders = generate_orders(instance, order_amount, earliest_time, planning_horizon)
    input = []
    meta = instance[0] # amount of jobs (not needed), amount of machines, amount of workers
    jobs = instance[1]
    for order in orders:
        for i in range(len(jobs[order[0]])): # amount of necessary operations for job n
            input.append([0,0,0])
    return input, orders, instance

def read_dataset_3(order_amount : int = 10, earliest_time : int = 500, last_time : int = 2000):
    data = read(3)
    # only reading one of the files for now
    instance = data[0]
    orders = []
    input = []
    for i in range(order_amount):
        orders.append([random.randint(0, instance[2] - 1), random.randint(earliest_time, last_time)])
    i = 0
    for i in range(len(orders)):
        input.append([0,0,0])
        for j in range(instance[4][orders[i][0]]):
            input.append([0,0,0])
    return input, orders, instance

def contains(entities, id):
    for entity in entities:
        if entity.external_id == id:
            return True
    return False

def translate_1(instance):
    # gather resources (in case of dataset 1 = workers)
    # gather workstations (in case of dataset 1 = machines)
    # gather recipes (in case of dataset 1 = lines 1:end)
    # gather tasks (in case of dataset 1 = combinations of machines and workers for each job)
    meta = instance[0]
    recipes_data = instance[1]
    resources = []
    workstations = []
    recipes = []
    tasks = []
    recipe_id = 0
    operation_id = 0
    resource_id = instance[0][2] + 1 # n workers + 1
    for recipe in recipes_data:
        task_id = 0
        tasks_of_recipe = []
        for recipe_task in recipe:
            resource_id += 1 # add pseudo resource to identify exchangable tasks
            for possible_machine_combination in recipe_task:
                for possible_workers_for_machine in possible_machine_combination:
                    machine = possible_workers_for_machine[0]
                    worker = possible_workers_for_machine[1]
                    duration = possible_workers_for_machine[2]
                    if not contains(workstations, machine):
                        workstations.append(Workstation(machine, f'machine#{machine}', [], []))
                    if not contains(resources, worker):
                        resources.append(Resource(worker, f'Worker#{worker}', 1, 0, True, [], 0))
                    task = Task(operation_id, f'R{recipe_id}o{task_id}w{machine}r{worker}', [(worker, 1)], [(resource_id, 1)], [], [], True, 0, 0) # Recipe/operation/workstation/resource for the name
                    if task_id > 0:
                        tasks[operation_id - 1].follow_up_tasks.append(operation_id)
                    tasks.append(task)
                    tasks_of_recipe.append(task)
                    workstations[len(workstations) - 1].tasks.append((operation_id, duration))
                    operation_id += 1
            task_id += 1
            
        recipes.append(Recipe(recipe_id, f'Recipe#{recipe_id}', tasks_of_recipe))
        recipe_id += 1
    return recipes, workstations, resources, tasks

def translate_3(instance, n_workstations):
    # instances.append([n_resources, resources_state, n_tasks, durations, rr, succession_tasks])    
    recipes = []
    workstations = []
    resources = []
    tasks = []
    tasks_for_workstation = []
    for i in range(instance[0]):
        resources.append(Resource(i, f'Resource#{i}', instance[1][i], 0, False, [], 0))
    for i in range(instance[2]):
        resources_for_task = []
        for j in range(instance[0]):
            if instance[4][j*instance[2]+i] != 0:
                resources_for_task.append(instance[4][j*instance[2]+i])
        tasks.append(Task(i, f'Task#{i}', resources_for_task, [], [], instance[5][i], True, 0, 0))
        tasks_for_workstation.append((tasks[len(tasks)-1], instance[3][i]))
        recipes.append(Recipe(i, f'Recipe#{i}', tasks[len(tasks)-1]))
    for i in range(n_workstations):
        workstations.append(Workstation(i, f'Workstation#{i}', [], tasks_for_workstation))
    return recipes, workstations, resources, tasks

def task_to_input(task : Task):
    input = []
    for pre in task.preceding_tasks:
        input += task_to_input(pre)
    input.append([0,0,0]) # switch to workstation_id, task_id, start_time for future input
    for follow_up in task.follow_up_tasks:
        input += task_to_input(follow_up)
    return input

def generate_optimizer_input(recipes, order_amount, earliest, latest):
    input = []
    orders = []
    for i in range(order_amount):
        orders.append([random.randint(0, len(recipes)), random.randint(earliest, latest)])
    for order in orders:
        for task in recipes[order[0]].tasks:
            input += task_to_input(task)
    return input, orders

# input, orders, instance = read_dataset_1(13, 10, 500, 2000)
# recipes, workstations, resources, tasks = translate_1(instance)
# input, orders, instance = read_dataset_3()
# recipes, workstations, resources, tasks = translate_3(instance)
# env = SimulationEnvironment(workstations, tasks, resources, recipes)