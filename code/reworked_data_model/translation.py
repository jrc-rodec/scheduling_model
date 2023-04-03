import os 
import inspect
from model import ProductionEnvironment, Workstation, Task, Resource, Recipe, SetupGroup, Schedule, Order, Job, Solver

class DataTranslator:
    
    def translate(self) -> ProductionEnvironment:
        pass

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
                    alternative_tasks :list[Task] = []
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
                            duration = row[idx]
                            setup_group = SetupGroup(id=f'r{j}w{l}t{m}', workstation_id=workstation.id)
                            task = Task(id=f'r{j}w{l}t{m}', name=f'r{j}w{l}t{m}', required_resources=(worker, 1), products=[], independent=False, setup_groups=[setup_group])
                            alternative_tasks.append(task)
                            workstation.tasks.append((task, duration))
                            production_environment.add_task(task)
                            production_environment.add_setup_group(setup_group)
                    tasks.append((alternative_tasks, k))
            recipe = Recipe(name=f'recipe_{i}', tasks=tasks)
            production_environment.add_resource(Resource(name=f'resource_{j}', recipes=[recipe]))
            production_environment.add_recipe(recipe)
        return production_environment

"""
    Add additional dataset translator here (Data Source -> Model)
"""

class Encoder:
    
    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]):
        pass
                

    def decode(self) -> Schedule:
        pass

"""
    Add additional encoders here (Model -> Solver (encode), Solver -> Schedule (decode))
"""

class TimeWindowGAEncoder(Encoder):
    
    def encode(self, production_environment : ProductionEnvironment, orders : list[Order]):
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