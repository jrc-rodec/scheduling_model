import os 
import inspect
from model import ProductionEnvironment, Workstation, Task, Resource, Recipe, SetupGroup, Schedule, Order, Job, Solver, reset_entities


class DataTranslator:
    
    def translate(self) -> ProductionEnvironment:
        pass

class FJSSPInstancesTranslator(DataTranslator):

    def reset(self):
        reset_entities()


    def translate(self, source : str = '6_Fattahi', benchmark_id = 0) -> ProductionEnvironment:
        currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
        path = currentdir + '\\..\\benchmarks\\'
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