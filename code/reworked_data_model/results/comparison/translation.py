import os 
import inspect
from model import ProductionEnvironment, Workstation, Task, Resource, Recipe, SetupGroup, Schedule, Order, Job, Solver, reset_entities
from get_data import get_data

class DataTranslator:
    
    def translate(self) -> ProductionEnvironment:
        pass

class FJSSPInstancesTranslator(DataTranslator):

    def reset(self):
        reset_entities()


    def translate(self, source : str = '6_Fattahi', benchmark_id = 0) -> ProductionEnvironment:
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        path = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\\'
        if source.startswith('0_'):
            target_file = f'Behnke{benchmark_id}.fjs'
        elif source.startswith('1_'):
            target_file = f'BrandimarteMk{benchmark_id}.fjs'
        elif source.startswith('2a'):
            target_file = f'HurinkSdata{benchmark_id}.fjs'
        elif source.startswith('2b'):
            target_file = f'HurinkEdata{benchmark_id}.fjs'
        elif source.startswith('2c'):
            target_file = f'HurinkRdata{benchmark_id}.fjs'
        elif source.startswith('2d'):
            target_file = f'HurinkVdata{benchmark_id}.fjs'
        elif source.startswith('3_'):
            target_file = f'DPpaulli{benchmark_id}.fjs'
        elif source.startswith('4_'):
            target_file = f'ChambersBarnes{benchmark_id}.fjs'
        elif source.startswith('5_'):
            target_file = f'Kacem{benchmark_id}.fjs'
        elif source.startswith('6_'):
            target_file = f'Fattahi{benchmark_id}.fjs'
        path += f'{source}\\{target_file}'
        file = open(path, 'r')
        file_content : list[str] = file.readlines()
        production_environment : ProductionEnvironment = ProductionEnvironment()
        self.reset()
        system_information = file_content[0].split(' ') #[number of recipes, number of workstations, average workstations / operation (can be ignored)]
        for i in range(int(system_information[1])): # add workstations to the system
            production_environment.add_workstation_type(i, f'w_type_{i}')
            production_environment.add_workstation(Workstation(name=f'workstation_{i}', basic_resources=[], tasks=[], workstation_type_id=i, event_log=[]))

        # create recipes
        for i in range(1, len(file_content)):
            row = file_content[i].split(' ')
            # first value = amount of tasks per recipe, followed by [amount of available workstations [workstation id, processing time]]
            idx = 0
            recipe_tasks = []
            for j in range(int(row[0])):
                idx += 1
                setup_group = SetupGroup()
                task : Task = Task(name=f'task_{i}_{j}', required_resources=[], products=[], independent=False, setup_groups=[setup_group])
                for k in range(int(row[idx])): # should be amount of workstations for task x
                    idx += 1
                    w_id = int(row[idx])-1
                    idx += 1
                    production_environment.get_workstation(w_id).tasks.append((task, int(row[idx]))) # NOTE: benchmark data are 1 indexed
                production_environment.add_task(task)
                production_environment.add_setup_group(setup_group)
                recipe_tasks.append((task, k, k+1))
            recipe : Recipe = Recipe(name=f'recipe_{i}', tasks=recipe_tasks)
            production_environment.add_recipe(recipe)
            production_environment.add_resource(Resource(name=f'resource_{i}', recipes=[recipe]))
        return production_environment


class BenchmarkTranslator(DataTranslator):

    def translate(self, benchmark_id : int = 0) -> ProductionEnvironment:
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        if benchmark_id == 0:
            target_file = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\SFJW\SFJW-01.txt'
        elif benchmark_id == 1:
            target_file = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\\SFJW\\SFJW-02.txt'
        elif benchmark_id == 2:
            target_file = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\SFJW\\SFJW-03.txt'
        elif benchmark_id == 3:
            target_file = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\SFJW\\SFJW-04.txt'
        elif benchmark_id == 4:
            target_file = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\SFJW\\SFJW-05.txt'
        elif benchmark_id == 5:
            target_file = r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\SFJW\\SFJW-06.txt'
        elif benchmark_id == 6:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-07.txt'
        elif benchmark_id == 7:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-08.txt'
        elif benchmark_id == 8:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-09.txt'
        elif benchmark_id == 9:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-10.txt'
        elif benchmark_id == 10:
            target_file = currentdir + '\\..\\external_test_data\\1\\MFJW\\MFJW-01.txt'
        elif benchmark_id == 11:
            target_file = currentdir + '\\..\\external_test_data\\1\\MFJW\\MFJW-02.txt'
        elif benchmark_id == 12:
            target_file = currentdir + '\\..\\external_test_data\\1\\MFJW\\MFJW-03.txt'
        elif benchmark_id == 13:
            target_file = currentdir + '\\..\\external_test_data\\1\\MFJW\\MFJW-04.txt'
        file = open(target_file, 'r')
        file_content : list[str] =  file.readlines()
        production_environment : ProductionEnvironment = ProductionEnvironment()
        system_information = file_content[0].split(' ') # [amount tasks, amount workstations, amount workers]
        for i in range(int(system_information[2])):
            production_environment.add_resource(Resource(name=f'worker_{i}', stock=1, reusable=True, recipes=[], vendors=[], events=[]))
        for i in range(int(system_information[1])):
            production_environment.add_workstation(Workstation(name=f'workstation_{i}', basic_resources=[], tasks=[], workstation_type_id=i, event_log=[]))
            production_environment.add_workstation_type(i, f'w_type_{i}')
        for i in range(int(system_information[0])):
            tasks = []
            # create tasks
            for j in range(1, len(file_content)):
                row = file_content[j].split(' ')
                # first value of the row is the amount of tasks in this recipe, second value how many workstations are available for first task, followed by workstation id, amount of workers available,  [worker id, processing time]
                idx = 0
                for k in range(int(row[0])):
                    # NOTE: alternative tasks are grouped as a list for a step in a recipe
                    alternative_tasks : list[Task] = []
                    idx += 1
                    # for each workstation available for task[k] of recipe[j]
                    for l in range(int(row[idx])):
                        idx += 1
                        workstation = production_environment.get_workstation(int(row[idx]) - 1) # NOTE: workstations in the benchmark are 1 indexed
                        idx += 1
                        for m in range(int(row[idx])):
                            idx += 1
                            worker = production_environment.get_resource(int(row[idx]) - 1) # NOTE: workers in the benchmark are 1 indexed
                            idx += 1
                            duration = int(row[idx])
                            setup_group = SetupGroup(workstation_id=workstation.id)
                            task = Task(name=f'r{j}w{l}t{m}', required_resources=(worker, 1), products=[], independent=False, setup_groups=[setup_group]) # TODO: remove id, switch to int ids only
                            alternative_tasks.append(task)
                            workstation.tasks.append((task, duration))
                            production_environment.add_task(task)
                            production_environment.add_setup_group(setup_group)
                    tasks.append((alternative_tasks, k))
            recipe = Recipe(name=f'recipe_{i}', tasks=tasks)
            production_environment.add_resource(Resource(name=f'resource_{i}', recipes=[recipe]))
            production_environment.add_recipe(recipe)
        return production_environment

"""
    Add additional dataset translator here (Data Source -> Model)
"""

class BasicBenchmarkTranslator(DataTranslator):

    def translate(self, id : int) -> ProductionEnvironment:
        n_workstations, recipes, operation_times = get_data(id)
        production_environment : ProductionEnvironment = ProductionEnvironment()
        for n in range(n_workstations):
            production_environment.add_workstation(Workstation(name=f'workstation_{n}', workstation_type_id=n))
            production_environment.add_workstation_type(n, f'w_type_{n}')
        operation_time_index = 0
        for recipe_index in range(len(recipes)):
            recipe_tasks : list[Task] = []
            for task_index in range(recipes[recipe_index]):
                setup_group = SetupGroup()
                task = Task(name=f'task_{operation_time_index}', setup_groups=[setup_group] ) # setup group is not really needed here
                for operation_index in range(len(operation_times[operation_time_index])):
                    workstation : Workstation = production_environment.get_workstation(operation_index)
                    workstation.tasks.append((task, int(operation_times[operation_time_index][operation_index])))
                recipe_tasks.append((task, task_index, task_index+1)) # task, sequence number, finish before number
                production_environment.add_task(task)
                production_environment.add_setup_group(setup_group)
                operation_time_index += 1
            recipe : Recipe = Recipe(name=f'recipe_{recipe_index}', tasks=recipe_tasks)
            production_environment.add_resource(Resource(name=f'resource_{recipe_index}', recipes=[recipe]))
            production_environment.add_recipe(recipe)
        return production_environment


class Encoder:
    
    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]):
        pass
                

    def decode(self) -> Schedule:
        pass

"""
    Add additional encoders here (Model -> Solver (encode), Solver -> Schedule (decode))
"""

class TimeWindowGAEncoder(Encoder):
    # NOTE: for the GA that includes workers
    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]) -> tuple[list[int], list[Job]]:
        # format: <workstation, worker, start_time, end_time>
        values : list[int] = []
        jobs : list[Job] = []
        for order in orders:
            ro_id = 0
            for resource in order.resources:
                if len(resource[0].recipes) > 0:
                    use_recipe : Recipe = resource[0].recipes[0] # assume only 1 recipe for each resource for now
                    for task in use_recipe.tasks:
                        jobs.append(Job(order=order, recipe=use_recipe, task=task, ro_id=ro_id))
                        ro_id += 1
                        values.extend([0, 0, 0, 0]) # NOTE: should maybe be initialised here already
        return values, jobs
    
    def decode(self, values : list[int], jobs : list[Job], production_environment : ProductionEnvironment, objective_values : list[float] = [], solver : Solver = None) -> Schedule:
        schedule : Schedule = Schedule(start_time=0, assignments=dict(), objective_values=objective_values, solver=solver)
        job_idx : int = 0
        for i in range(0, len(values), 4):
            workstation_id : int = values[i]
            worker_id : int = values[i+1]
            start_time : int = values[i+2]
            end_time : int = values[i+3]
            workstation : Workstation = production_environment.get_workstation(workstation_id)
            worker : Resource = production_environment.get_resource(worker_id)
            job : Job = jobs[job_idx]
            schedule.add_assignment(workstation, job, start_time, end_time, [(worker, 1)])
            job_idx += 1
        return schedule
    
class SimpleGAEncoder(Encoder):

    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]) -> tuple[list[int], dict[int, list[int]], list[Job]]:
        # format: <workstation, start_time>
        values : list[int] = []
        durations : dict[int, list[int]] = dict() # durations on each workstation for each indexed task
        jobs : list[Job] = []
        for order in orders:
            ro_id = 0
            for resource in order.resources:
                if len(resource[0].recipes) > 0:
                    use_recipe : Recipe = resource[0].recipes[0] # assume only 1 recipe for each resource for now
                    for task in use_recipe.tasks:
                        jobs.append(Job(order=order, recipe=use_recipe, task=task[0], ro_id=ro_id))
                        ro_id += 1
                        values.extend([0, 0])
                        d : list[int] = len(production_environment.workstations) * [0] # TODO: something wrong with the parsing of this
                        possible_workstations = production_environment.get_available_workstations_for_task(task[0])
                        for possible_workstation in possible_workstations:
                            d[possible_workstation.id] = possible_workstation.get_duration(task[0])
                        durations[task[0].id] = d
        return values, durations, jobs

    def decode(self, values : list[int], jobs : list[Job], production_environment : ProductionEnvironment, objective_values : list[float] = [], solver : Solver = None) -> Schedule:
        schedule : Schedule = Schedule(start_time=0, assignments=dict(), objective_values=objective_values, solver=solver)
        job_idx : int = 0
        for i in range(0, len(values), 2):
            workstation_id : int = values[i]
            workstation : Workstation = production_environment.get_workstation(workstation_id)
            start_time : int = values[i+1]
            end_time : int = start_time + workstation.get_duration(jobs[job_idx].task)
            schedule.add_assignment(workstation=workstation, job=jobs[job_idx], start_time=start_time, end_time=end_time, resources=[])
            job_idx += 1
        return schedule

class TimeWindowSequenceEncoder(Encoder):

    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]):
        values : list[int] = []
        jobs : list[Job] = []
        for order in orders:
            ro_id = 0
            for resource in order.resources:
                if len(resource[0].recipes) > 0:
                    use_recipe : Recipe = resource[0].recipes[0]
                    for task in use_recipe.tasks:
                        jobs.append(Job(order=order, recipe=use_recipe, task=task[0], ro_id=ro_id))
                        ro_id += 1
                        values.extend([0, 0, 0]) # workstation, sequence value on workstation, time window size
        return values, jobs
    
    def get_indices_for_workstation(self, values, workstation):
        on_workstation = []
        for i in range(0, len(values), 4):
            if values[i] == workstation:
                on_workstation.append(i)
        return on_workstation

    def right_shift(self, values : list[int], sequence_values : list[int], job_orders : list[int], workstation):
        on_workstation = self.get_indices_for_workstation(values, workstation)
        on_workstation.sort(key=lambda x: sequence_values[x+1])
        for i in range(len(on_workstation)):
            if i > 0:
                idx = on_workstation[i]
                prev_idx = on_workstation[i-1]
                values[idx+1] = max(values[idx+1], values[prev_idx+1]+values[prev_idx+3])
                # find and resolve sequence dependencies
            else:
                # NOTE: shouldn't do anything
                values[on_workstation[i]+1] = max(values[on_workstation[i]+1], 0)

    def determine_start_time_repaired(self, values : list[int], production_environment : ProductionEnvironment, jobs : list[Job]):
        workstations = len(production_environment.get_workstation_list())
        job_orders = [j.order.id for j in jobs]
        #repair 
        changes = True
        while changes:
            changes = False
            for i in range(4, len(values), 4):
                j = i
                while j >= 0 and job_orders[int(j/4)] == job_orders[int(i/4)]:
                    if values[j] == values[i] and values[j+1] > values[i+1]:
                        tmp = values[i+1]
                        values[i+1] = values[j+1]
                        values[j+1] = tmp
                        changes = True
                        #print('repaired')
                    j -= 4
        result = values.copy()

        changes = True
        count = 0
        while changes:
            changes = False
            # workstation dependencies
            for w in range(workstations):
                on_workstation = self.get_indices_for_workstation(result, w)
                on_workstation.sort(key=lambda x: result[x+1])
                for i in range(len(on_workstation)):
                    if i == 0:
                        result[on_workstation[i]+1] = max(result[on_workstation[i]+1], 0) if count > 0 else 0
                    else:
                        result[on_workstation[i]+1] = max(result[on_workstation[i]+1], result[on_workstation[i-1]+1] + result[on_workstation[i-1]+3])
            # job sequence dependencies
            for i in range(len(job_orders)):
                if i > 0:
                    if job_orders[i] == job_orders[i-1]:
                        idx = i * 4
                        before = result[idx+1]
                        prev_idx = (i-1) * 4
                        result[idx+1] = max(result[idx+1], result[prev_idx+1] + result[prev_idx+3])
                        if before != result[idx+1]:
                            # right shift all on workstation
                            self.right_shift(result, values, job_orders, result[idx]) # NOTE: only shifting after sequence number would be more efficient, ignore for now
                            #changes = True
                            count += 1
                        changes = changes or before != result[idx+1]
            if count > 100:
                #print('circular dependency')
                changes = False
        return result

    def get_start_times(self, values : list[int], production_environment : ProductionEnvironment, jobs : list[Job]) -> list[int]:
        result = values.copy()
        on_workstations = []
        for workstation in range(len(production_environment.workstations.keys())):
            on_workstations.append([])
            for i in range(0,len(result), 4):
                if result[i] == workstation:
                    on_workstations[workstation].append(i)
        for workstation in on_workstations:
            workstation.sort(key=lambda x: values[x+1])
            for i in range(len(workstation)):
                if i == 0:
                    result[workstation[i]+1] = 0
                else:
                    result[workstation[i]+1] = result[workstation[i-1]+1] + result[workstation[i-1]+3]# + 1
        changes = True
        counter = 0
        while changes:
            changes = False
            for i in range(0, len(result), 4): # for all jobs
                if i > 0 and jobs[int(i/4)].order == jobs[int(i/4) - 1].order: # first job in order sequence is not affected
                    if result[i-3] + result[i-1] > result[i+1]:
                        #changes = True
                        # adjust
                        #shift = result[i-3] + result[i-1] - result[i+1]
                        #result[i+1] += shift# + 1
                        result[i+1] = result[i-3] + result[i-1]
                        # shift all on workstation until no longer necessary
                        w = None
                        for workstation in on_workstations:
                            if i in workstation:
                                w = workstation
                                break
                        for j in range(w.index(i) + 1, len(w)):
                            #shift = result[w[j-1]+1] + result[w[j-1]+3] - result[w[j]+1]
                            #if result[w[j-1]+1] + result[w[j-1]+3] <= result[w[j]+1]:
                            #    break # stop shifting
                            #result[w[j]+1] = max(result[w[j-1]+1] + result[w[j-1]+3] + 1, result[w[j]-3 + result[w[j]]-1]) # move start time to previous end time, unless already later
                            prev = 0
                            if jobs[int((w[j]-4) / 4)].order == jobs[int(w[j] / 4)].order:
                                prev = result[w[j]-3] + result[w[j]-1]
                            result[w[j]+1] = max(result[w[j-1]+1] + result[w[j-1]+3], prev) # move start time to previous end time, unless already later
            counter += 1
            if counter > 1000:
                print(counter)
        return result

    def determine_start_times(self, values : list[int], production_environment : ProductionEnvironment, jobs : list[Job]) -> list[int]:
        #values = [0, 0, 0, 10, 0, 1, 0, 5, 1, 1, 0, 5, 1, 0, 0, 10]
        # TODO: rewrite to include workers
        result = values.copy()
        on_workstations = []
        for workstation in range(len(production_environment.workstations.keys())):
            on_workstations.append([])
            for i in range(0,len(result), 4):
                if result[i] == workstation:
                    on_workstations[workstation].append(i)
        for workstation in on_workstations:
            workstation.sort(key=lambda x: values[x+1])
            for i in range(len(workstation)):
                if i == 0:
                    result[workstation[i]+1] = 0
                else:
                    result[workstation[i]+1] = result[workstation[i-1]+1] + result[workstation[i-1]+3]
        for i in range(0,len(result),4):
            if i > 0 and jobs[int(i/4)].order == jobs[int(i/4)-1].order:
                for w in on_workstations:
                    if i in w:
                        on_workstation = w
                        break
                prev_end = result[i-3] + result[i-1]
                shift = prev_end - result[i+1]
                for j in range(on_workstation.index(i), len(on_workstation)):
                    #prev_end = result[i-3] + result[i-1]
                    #result[on_workstation[j]+1] = max(result[on_workstation[j]+1], shift)
                    # NOTE: check if shift is necessary at all
                    if j == 0:
                        #result[on_workstation[j]+1] = max(result[on_workstation[j]+1], result[on_workstation[j]+1] + shift)
                        result[on_workstation[j]+1] += shift
                    #elif result[on_workstation[j-1]+1] + shift > result[on_workstation[j]+1]:
                    else:
                        result[on_workstation[j]+1] = result[on_workstation[j-1]+1] + result[on_workstation[j-1]+3] + shift #max(result[on_workstation[j]+1], result[on_workstation[j]+1] + shift)
                    #else:
                    #    break # in case the previous job didn't have to shift, all others can stop shifting
        return result


    def decode(self, values : list[int], jobs : list[Job], production_environment : ProductionEnvironment, objective_values : list[float] = [], solver : Solver = None) -> Schedule:
        schedule : Schedule = Schedule(start_time=0, assignments=dict(), objective_values=objective_values, solver=solver)
        job_idx : int = 0
        #solution = self.determine_start_times(values, production_environment, jobs)
        #solution = self.get_start_times(values, production_environment, jobs)
        solution = self.determine_start_time_repaired(values, production_environment, jobs)
        for i in range(0, len(solution), 4):
            workstation_id : int = solution[i]
            workstation : Workstation = production_environment.get_workstation(workstation_id)
            start_time = solution[i+1]
            end_time : int = start_time + solution[i+3]
            schedule.add_assignment(workstation=workstation, job=jobs[job_idx], start_time=start_time, end_time=end_time, resources=[])
            job_idx += 1
        return schedule


class GurobiEncoder(Encoder):

    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]):
        #NOTE: all IDs used by the gurobi solver a 1 indexed
        recipes = [] # jobs
        job_ops_machs : tuple[int,int,int] = []
        durations : dict[tuple[int,int,int],int] = dict() # recipe/order id, ro_id, workstation_id -> duration
        job_op_suitable : dict[tuple[int, int]] = dict()
        nb_machines : int = len(production_environment.workstations.keys())
        for order in orders:
            recipes.append(order.resources[0][0].recipes[0]) # default recipe for now
        nb_jobs = len(recipes)
        nb_operations = [len(recipe.tasks) for recipe in recipes]
        INFINITE = 1000000
        task_processing_times : list[list[list[int]]] = [[[INFINITE for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]
        jobs : list[Job] = []
        for order in orders:
            recipe = order.resources[0][0].recipes[0]
            for i in range(len(recipe.tasks)):
                task = recipe.tasks[i][0]
                workstations = production_environment.get_available_workstations_for_task(task)
                for workstation in workstations:
                    job_ops_machs.append((order.id + 1, i + 1, workstation.id + 1))
                    duration = workstation.get_duration(task)
                    durations[order.id + 1, i + 1, workstation.id + 1] = duration
                    task_processing_times[order.id][i][workstation.id] = duration
                job_op_suitable[order.id + 1, i + 1] = [w.id + 1 for w in workstations]
                jobs.append(Job(order=order, recipe=recipe, task=task, ro_id=i))
        upper_bound = 0
        for j in range(nb_jobs):
            for o in range(nb_operations[j]):
                upper_bound += max(x for x in task_processing_times[j][o] if x != INFINITE)
        return nb_machines, nb_jobs, nb_operations, job_ops_machs, durations, job_op_suitable, upper_bound, jobs

    def decode(self, xsol, ysol, csol, job_ops_machs, durations, production_environment : ProductionEnvironment, jobs : list[Job], solver : Solver = None):
        schedule : Schedule = Schedule()
        schedule.solver = solver
        job_idx = 0
        for j, k, i in job_ops_machs:
            if ysol[j,k,i] > 0:
                job = jobs[job_idx]
                job_idx+=1
                workstation = production_environment.get_workstation(i-1)
                start_time = csol[j,k]-durations[j,k,i]
                end_time = csol[j,k]
                schedule.add_assignment(workstation, job, start_time, end_time, resources=[])
        return schedule
    
import gurobipy as gp

class GurobiWithWorkersEncoder(Encoder):

    def encode(self, production_environment : ProductionEnvironment, orders : list[Order], lines): # TODO: replace and remove lines parameter
        INFINITE = 1000000
        recipes = []
        nb_operations = [len(recipe.tasks) for recipe in recipes]
        nb_jobs = len(recipes)
        nb_machines = len(production_environment.workstations.keys())
        nb_workers = len(production_environment.resources.keys())
        for order in orders:
            recipes.append(order.resources[0][0].recipes[0]) # default recipe for now
        task_processing_time = [[[[INFINITE for s in range(nb_workers)] 
                                        for m in range(nb_machines)] 
                                        for o in range(nb_operations[j])] 
                                        for j in range(nb_jobs)]
    
        job_op_dur_helper = {}
        job_op_machsuitable = {}
        job_op_mach_workersuitable = {}
        for j in range(nb_jobs):
            line = lines[j + 1].split()
            tmp_idx = 1
            for o in range(nb_operations[j]):
                nb_machines_operation = int(line[tmp_idx])
                tmp_idx += 1
                suitable_machine_helper = []
                for i in range(nb_machines_operation):
                    machine = int(line[tmp_idx])
                    suitable_machine_helper += [machine]
                    nb_m_workers = int(line[tmp_idx + 1])
                    tmp_idx += 2
                    suitable_worker_helper = []
                    for s in range(nb_m_workers):
                        worker = int(line[tmp_idx])
                        time = int(line[tmp_idx + 1])
                        tmp_idx += 2
                        task_processing_time[j][o][machine-1][worker-1] = time
                        suitable_worker_helper += [worker]
                        job_op_dur_helper[j+1,o+1,machine,worker] = time
                    
                    job_op_mach_workersuitable[j+1,o+1,machine] = suitable_worker_helper
                job_op_machsuitable[j+1,o+1] = suitable_machine_helper

        job_op_mach_worker, duration = gp.multidict(job_op_dur_helper)
        
        # Trivial upper bound for the completion times of the tasks
        L=0
        for j in range(nb_jobs):
            for o in range(nb_operations[j]):
                L += max(task_processing_time[j][o][m][s] for m in range(nb_machines) for s in range(nb_workers) if task_processing_time[j][o][m][s] != INFINITE )
        return nb_jobs, nb_operations, nb_machines, nb_workers, job_op_machsuitable, job_op_mach_worker, duration, job_op_mach_worker, L
        

    def decode(self, xsol, usol, ysol, csol, job_ops_machs, durations, production_environment : ProductionEnvironment, jobs : list[Job], solver : Solver = None):
        schedule : Schedule = Schedule()
        schedule.solver = solver
        job_idx = 0
        for j, k, i in job_ops_machs:
            if ysol[j,k,i] > 0:
                job = jobs[job_idx]
                job_idx+=1
                workstation = production_environment.get_workstation(i-1)
                start_time = csol[j,k]-durations[j,k,i]
                end_time = csol[j,k]
                schedule.add_assignment(workstation, job, start_time, end_time, resources=[])
        return schedule
    
class SequenceGAEncoder(Encoder):

    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]) -> tuple[list[list[int]], list[list[int]], list[int]]:
        workstations_per_operation : list[list[int]] = []
        base_durations : list[list[int]] = []
        jobs : list[int] = []
        tasks = production_environment.get_task_list()
        workstations_available = list(production_environment.get_workstation_list())
        for task in tasks:
            workstations_per_operation.append([])
            workstations = production_environment.get_available_workstations_for_task(task)
            workstations_per_operation[task.id] = [w.id for w in workstations]
            base_durations.append([0] * len(workstations_available))
            for workstation in workstations:
                base_durations[-1][workstation.id] = workstation.get_duration(task)
        for order in orders:
            jobs.extend([order.id for _ in order.resources[0][0].recipes[0].tasks])
        return workstations_per_operation, base_durations, jobs
        

    def decode(self, job_sequence : list[int], workstation_assignments : list[int], worker_assignments : list[int], durations : list[int], job_operations, production_environment : ProductionEnvironment, fill_gaps : bool = False, solver = None) -> Schedule:
        schedule = Schedule()
        schedule.solver = solver
        jobs = []
        for x in job_operations:
            if x not in jobs:
                jobs.append(x)
        next_operations = [0] * len(jobs)
        end_on_workstations = [0] * len(list(production_environment.get_workstation_list()))
        end_times = [-1] * len(job_operations)
        gaps_on_workstations :list[list[tuple[int, int]]]= []
        for i in range(len(list(production_environment.get_workstation_list()))):
            gaps_on_workstations.append([])
        for i in range(len(job_sequence)):
            job = job_sequence[i]
            operation = next_operations[job]
            start_index = 0
            for j in range(len(job_operations)):
                if job_operations[j] == job:
                    start_index = j
                    break
                start_index = j
            start_index += operation
            next_operations[job] += 1
            workstation = workstation_assignments[start_index]
            duration = durations[start_index]
            offset = 0
            if operation > 0:
                # check end on prev workstation NOTE: if there is a previous operation of this job, start_index-1 should never be out of range
                offset = max(0, end_times[start_index-1] - end_on_workstations[workstation])
                min_start_job = end_times[start_index-1]
            start_time = end_on_workstations[workstation] + offset
            if fill_gaps:
                use_gap = None
                for gap in gaps_on_workstations[workstation]:
                    if gap[0] >= min_start_job and gap[0] >= end_on_workstations[workstation] and gap[1] - gap[0] >= duration:
                        # found a gap
                        use_gap = gap
                        break
                if use_gap:
                    # find start time
                    # find end time
                    # check for new, smaller gap
                    index = gaps_on_workstations[workstation].index(use_gap)
                    if len(gaps_on_workstations[workstation]) > index+1:
                        # should be sorted
                        if use_gap[1] + duration < gaps_on_workstations[workstation][index+1][0]:
                            gaps_on_workstations[workstation][index] = (use_gap[1], gaps_on_workstations[workstation][index+1][0])
                        else:
                            gaps_on_workstations[workstation].remove(use_gap) # no new gap, just remove the gap from the list
                    else:
                            # last end on workstation = start
                            gaps_on_workstations[workstation].remove(use_gap)
                    start_time = use_gap[0]

            end_time = start_time + duration
            end_times[start_index] = max(end_times[start_index], end_time)
            end_on_workstations[workstation] = end_times[start_index]
            
            w = production_environment.get_workstation(workstation)
            j = Job(f'J{job}O{operation}', production_environment.get_order(job))

            schedule.add_assignment(w, j, start_time, end_time, resources=[])
            end_on_workstations[workstation] = end_time
        return schedule