from models import SimulationEnvironment, Workstation, Task, Recipe, Schedule
import random

class DataTranslator:
    pass

"""
    TRANSLATORS FOR DATASOURCES
"""
class TestTranslator(DataTranslator): # no resources used for this dataset

    def translate(self, n_workstations, recipies, processing_times):
        workstations =  []
        recipies_list = []
        r_id = 0
        tasks =  []
        for w_id in range(n_workstations):
            workstations.append(Workstation(w_id, f'w{w_id}', [], [])) # id, name, basic resources, tasks
        t_id = 0
        for recipe in recipies:
            tasks_for_recipe = []
            for i in range(recipe):
                #alternatives = [] # needed for this dataset, also easier for other datasets, could be replaced by searching for tasks with same result resources (if given)
                w_id = 0
                task = Task(t_id, f't{t_id}', [], [], [], [], True, 0, 0, []) # id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time, alternatives
                for duration in processing_times[i]:
                    # create task + add to workstation
                    #alternatives.append(task)
                    workstations[w_id].tasks.append((t_id, duration))
                    w_id = w_id + 1
                tasks.append(task) # add to list of all tasks
                #for task in alternatives:
                #    task.alternatives = alternatives.copy()
                #    task.alternatives.remove(task) # remove self from alternative list
                #tasks_for_recipe.append(random.choice(alternatives)) # choose random task as placeholder in recipe
                tasks_for_recipe.append(task)
                t_id = t_id + 1
            recipies_list.append(Recipe(r_id, f'r{r_id}', tasks_for_recipe))
            r_id = r_id + 1
        return recipies_list, workstations, [], tasks, [] # recipies, workstations, resources, tasks, orders

"""
    TRANSLATORS FOR SOLVERS
"""
class EncodeForGA(DataTranslator):

    def translate(self, env : SimulationEnvironment, orders):
        values = []
        alternative_tasks_per_job = [] # for each index (job), add all possible alternatives eligible for this slot (starting task + all alternatives)
        durations = dict() # durations on each workstation for each indexed task
        all_jobs = [] # gather all jobs
        for order in orders:
            recipe_id = order.resources[0] # saved recipe in there for now, change later
            recipe : Recipe = env.get_recipe_by_id(recipe_id)
            for task in recipe.tasks:
                values.append(0) # slot for workstation
                values.append(0) # slot for start time
                all_jobs.append(task.id) # just add the starting task id for now
                """alternatives = task.alternatives
                all_possibilities = []
                all_possibilities.append(task.id) 
                for alternative in alternatives:
                    all_possibilities.append(alternative.id)
                alternative_tasks_per_job.append(all_possibilities) # add all possible tasks for encoding index x
                for possibility in all_possibilities:
                    if possibility not in durations:
                        d = []
                        for _ in range(len(env.workstations)):
                            d.append(0)
                        possible_workstations = env.get_all_workstations_for_task(possibility)
                        for possible_workstation in possible_workstations:
                            for task_duration in possible_workstation.tasks:
                                if task_duration[0] == possibility:
                                    d[possible_workstation.id] = task_duration[1]
                        durations[possibility] = d"""
                d = [] # TODO: test after adjusting for new duration table
                for _ in range(len(env.workstations)):
                    d.append(0)
                possible_workstations = env.get_all_workstations_for_task(task.id)
                for possible_workstation in possible_workstations:
                    for task_duration in possible_workstation.tasks:
                        if task_duration[0] == task.id:
                            d[possible_workstation.id] = task_duration[1]
                durations[task.id] = d
        return values, durations, all_jobs, alternative_tasks_per_job # encoding, duration lookup table, list of all jobs (probably not needed), list of all possible alternatives for each slot

class EncodeForPSO(DataTranslator):

    def translate(self, env : SimulationEnvironment, orders):
        values = []
        pass

class EncodeForGreedyAgent(DataTranslator):

    def translate(self, env: SimulationEnvironment, orders):
        values = []
        pass

"""
    TRANSLATORS BACK TO SCHEDULE MODEL
"""

class GAToScheduleTranslator(DataTranslator):

    def translate(self, result, jobs, env : SimulationEnvironment, orders):
        schedule = Schedule()
        for i in range(0, len(result), 2): # go through workstation assignments
            schedule.add((result[i], result[i+1]), jobs[int(i/2)], self.get_order(i, env, orders))
        return schedule

    def get_order(self, index, env, orders):
        job_index = int(index/2)
        sum = 0
        for order in orders:
            if sum >= job_index:
                return order
            recipe = env.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            sum += len(recipe.tasks)
        return orders[len(orders)-1]