from models import SimulationEnvironment, Workstation, Task, Recipe, Schedule
import random
import copy

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
        processing_index = 0
        for recipe in recipies:
            tasks_for_recipe = []
            
            for i in range(recipe):
                w_id = 0
                task = Task(t_id, f't{t_id}', [], [], [], [], True, 0, 0, []) # id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time, alternatives
                for duration in processing_times[processing_index]:
                    # create task + add to workstation
                    workstations[w_id].tasks.append((t_id, duration))
                    w_id = w_id + 1
                
                processing_index += 1
                tasks.append(task) # add to list of all tasks
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
        durations = dict() # durations on each workstation for each indexed task
        all_jobs = [] # gather all jobs
        for order in orders:
            recipe_id = order.resources[0] # saved recipe in there for now, change later
            recipe : Recipe = env.get_recipe_by_id(recipe_id)
            for task in recipe.tasks:
                values.append(0) # slot for workstation
                values.append(0) # slot for start time
                all_jobs.append(task.id) # just add the starting task id for now
                d = [] # TODO: test after adjusting for new duration table
                for _ in range(len(env.workstations)):
                    d.append(0)
                possible_workstations = env.get_all_workstations_for_task(task.id)
                for possible_workstation in possible_workstations:
                    for task_duration in possible_workstation.tasks:
                        if task_duration[0] == task.id:
                            d[possible_workstation.id] = task_duration[1]
                durations[task.id] = d
        return values, durations, all_jobs # encoding, duration lookup table, list of all jobs (probably not needed), list of all possible alternatives for each slot

class EncodeForPSO(DataTranslator):

    def translate(self, env : SimulationEnvironment, orders):
        values = []
        pass

class EncodeForGreedyAgent(DataTranslator):

    def translate(self, env: SimulationEnvironment, orders):
        values = []
        pass

class EncodeForCMA(DataTranslator):

    def translate(self, env : SimulationEnvironment, orders):
        values : list[float] = []
        durations = dict()
        jobs = []
        for order in orders:
            recipe_id = order.resources[0]
            recipe : Recipe = env.get_recipe_by_id(recipe_id)
            due_dates = []
            for task in recipe.tasks:
                values.append(0.0)
                jobs.append(task.id)
                due_dates.append((orders.delivery_time, orders.latest_acceptable_time)) #NOTE: for optimization, aim for delivery time, accept latest acceptable time as feasible
            d =  []
            for _ in range(len(env.workstations)):
                d.append(0)
            possible_workstations = env.get_all_workstations_for_task(task.id)
            for possible_workstation in possible_workstations:
                for task_duration in possible_workstation.tasks:
                    if task_duration[0] == task.id:
                        d[possible_workstation.id] = task_duration[1]
            durations[task.id] = d
        return values, durations, jobs, due_dates

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
            recipe = env.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            if job_index < sum + len(recipe.tasks):
                return order
            sum += len(recipe.tasks)
        return orders[len(orders)-1]
    
class CMAToScheduleTranslator(DataTranslator):

    def cost_function(self, weight, p_all, due_date, start_times, env : SimulationEnvironment): # calculate priority of each job to be scheduled next, big weight = low priority score (min priority score is next)
        d = due_date[0] # just consider deliver time, not latest acceptable
        costs = []
        for i in range(len(p_all)):
            costs.append((p_all[i] * (d / start_times[i])) / weight) # if cost = 0, not possible on workstation
        return costs # returns cost for each workstation

    def get_next(self, costs):
        current_min = float('max')
        index = 0
        for i in range(len(costs)):
            if any(value < current_min for value in costs[i]):
                index = i
                current_min = min(costs[i])
        return index # returns index of next job to be scheduled, not including which workstation should be used
    
    def get_order(self, index, env, orders):
        sum = 0
        for order in orders:
            recipe = env.get_recipe_by_id(order.resources[0])
            if index < sum + len(recipe.tasks):
                return order
            sum += len(recipe.tasks)
        return orders[len(orders)-1]

    def is_first(self, index, env, orders):
        sum = 0
        for i in range(len(orders)):
            if sum + len(env.get_recipe_by_id(orders[i].resources[0])) >= index:
                return index - sum + len(env.get_recipe_by_id(orders[i].resources[0])) == 0
        return False

    def find_suitable_slots(self, sorted_assignments, job, durations, workstation):
        duration = durations[job][workstation]
        prev_end_time = 0
        slots = []
        for assignment in sorted_assignments:
            if assignment[1] - prev_end_time > duration:
                slots.append(prev_end_time)
            prev_end_time = assignment[1] + durations[assignment[0]][workstation]
        last_assignment = sorted_assignments[len(sorted_assignments-1)]
        if last_assignment[1] + durations[last_assignment[0]][workstation] not in slots:
            slots.append(last_assignment[1] + durations[last_assignment[0]][workstation]) # add last used time slot on workstation to the list
        return slots

    def find_earliest_start_times(self, schedule : Schedule, jobs : list[int], durations, env : SimulationEnvironment, orders, scheduled : list[bool]) -> list[list[int]]:
        # this is probably very slow
        start_times = []
        workstation_assignments = []
        for workstation in env.workstations:
            assignments = schedule.assignments_for(workstation.id)
            if not assignments is None:
                workstation_assignments.append(assignments)
            else:
                workstation_assignments.append([])
        for i in range(len(jobs)):
            times = [float('max') for _ in env.workstations]
            min_times = [0 for _ in env.workstations]
            if not scheduled[i]:
                order = self.get_order(i, env, orders)
                first = self.is_first(i, env, orders)
                if not first:
                    # find previous scheduled tasks of same order to gather min start times
                    for workstation in env.workstations:
                        for assignment in workstation_assignments[workstation.id]: # assignment -> <task id, start time, order id>
                            if assignment[2].id == order.id:
                                duration = durations[assignment[0]][workstation.id]
                                end_time = assignment[1] + duration
                                min_times[workstation.id] = end_time #NOTE: this does not mean the timeslot is available, the task is just not allowed to start before this time
                
                for workstation in env.workstations:
                    sorted_assignments = schedule.assignments_for(workstation.id).sort(key = lambda x : x[1])
                    possible_start_times = self.find_suitable_slots(sorted_assignments, jobs[i], durations, workstation.id)
                    for start_time in possible_start_times:
                        if start_time >= max(min_times) and start_time < times[workstation.id]:
                            times[workstation.id] = start_time
            else:
                times = [0]
            start_times.append(times)
        return start_times # returns earliest possible start time on each workstation for each job

    def translate(self, result, jobs, durations, due_dates, env : SimulationEnvironment, orders):
        schedule = Schedule()
        values = copy.deepcopy(result)
        start_times : list[list[int]] = []
        scheduled = [False for _ in jobs]
        for _ in range(len(values)):
            costs = []
            # TODO: start_times - earliest possible start times on each workstation for each job according to their duration on the workstation
            start_times = self.find_earliest_start_times(schedule, jobs, durations, env, orders, scheduled)
            for i in range(len(values)):
                costs.append(self.cost_function(values[i], durations[jobs[i]], due_dates[i], start_times[i]))
            next_job = self.get_next(costs)
            # for now, just choose min value
            workstation = costs[next_job].index(min(costs[next_job])) # workstation id
            values[next_job] = [float('max')] # remove them as possibility without changing the length of the list, should probably be done differently
            start_time = start_times[next_job][workstation]
            schedule.add((workstation, start_time), jobs[next_job], self.get_order(next_job, env, orders))
            scheduled[next_job] = True
        return schedule