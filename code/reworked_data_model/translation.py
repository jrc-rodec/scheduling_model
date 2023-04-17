import os 
import inspect
from model import ProductionEnvironment, Workstation, Task, Resource, Recipe, SetupGroup, Schedule, Order, Job, Solver
from get_data import get_data

class DataTranslator:
    
    def translate(self) -> ProductionEnvironment:
        pass

class FJSSPInstancesTranslator(DataTranslator):

    def translate(self, source : str = '6_Fattahi', benchmark_id = 0) -> ProductionEnvironment:
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        path = currentdir + '\\..\\external_test_data\\FJSSPinstances\\'
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
            target_file = f'DPaulli{benchmark_id}a.fjs'
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
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-01.txt'
        elif benchmark_id == 1:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-02.txt'
        elif benchmark_id == 2:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-03.txt'
        elif benchmark_id == 3:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-04.txt'
        elif benchmark_id == 4:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-05.txt'
        elif benchmark_id == 5:
            target_file = currentdir + '\\..\\external_test_data\\1\\SFJW\\SFJW-06.txt'
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
