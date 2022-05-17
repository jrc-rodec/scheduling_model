from models import Schedule, SimulationEnvironment, Order
import random

class Agent:

    def __init__(self, simulation_environment : SimulationEnvironment):
        self.environment = simulation_environment
        self.state = Schedule()

    def process(self, order : Order) -> bool:
        pass

    def get_state(self) -> Schedule:
        return self.state

    def is_blocked(self, workstation_id, start_time, duration):
        assignments = self.state.assignments_for(workstation_id)
        if assignments:
            for assignment in assignments:
                assignment_start_time = assignment[1]
                assignment_duration = self.environment.get_duration(assignment[0], workstation_id)
                if start_time > assignment_start_time and start_time < assignment_start_time + assignment_duration:
                    return True
                if start_time + duration > assignment_start_time and start_time + duration < assignment_start_time + assignment_duration:
                    return True
                # if new task is longer than already scheduled task, it could start before and end after -> overlap
                if assignment_start_time > start_time and assignment_start_time < start_time + duration:
                    return True
                if assignment_start_time + assignment_duration > start_time and assignment_start_time + assignment_duration < start_time + duration:
                    return True
        return False

class AgentSimulator:

    def __init__(self):
        pass

    def simulate(self, agent : Agent, orders):
        scheduled_count = 0
        for order in orders:
            success = agent.process(order)
            if success:
                scheduled_count += 1
        return agent.get_state(), scheduled_count

class GreedyAgent(Agent):

    def pick_random(self, task, tasks):
        task = self.environment.get_task(task)
        if len(task.follow_up_tasks) > 0:
            follow_up_id = random.choice(task.follow_up_tasks)
            follow_up = self.environment.get_task(follow_up_id)
            tasks.append(follow_up)
            self.pick_random(follow_up.id, tasks)
        
    def pick_random_path(self, recipe):
        tasks = []
        task = random.choice(recipe.tasks)
        tasks.append(task)
        self.pick_random(task.id, tasks)
        return tasks 

    def process(self, order : Order):
        recipes = []
        for resource in order.resources:
            recipes.append((order.id, resource.recipes))
        tasks = []
        for recipe in recipes:
            path = recipe[1][0].tasks#self.pick_random_path(recipe[1][0]) # ignore possibility of multiple recipes for now
            path.reverse()
            tasks.append(path) # add in reverse order for each recipe
        success_count = 0
        for i in range(len(tasks)):
            prev_duration = 0
            for j in range(len(tasks[i])):
                task = tasks[i][j]
                workstations = self.environment.get_valid_workstations(task.external_id)
                chosen_workstation = None
                for workstation in workstations:
                    duration = self.environment.get_duration(task.external_id, workstation.external_id)
                    start_slot = order.delivery_time - prev_duration - duration
                    if not self.is_blocked(workstation.external_id, start_slot, duration):
                        chosen_workstation = workstation
                        break            
                if chosen_workstation:    
                    prev_duration += duration
                    self.state.add((chosen_workstation, start_slot), task.external_id, order.external_id)
                    success_count += 1
                else:
                    if not order.divisible: # if order can not only be partially fullfilled too
                        return False
                    else:
                        break
        return success_count > 0

class CompactGreedyAgent(Agent):

    def has_space_before(self, workstation : int, duration : int, prev_start : int):
        assignments = self.state.assignments_for(workstation)
        blocked = []
        for assignment in assignments:
            start_time = assignment[1]
            duration = self.environment.get_duration(assignment[0], workstation)
            end_time = start_time + duration
            if end_time <= prev_start: # only use feasible time slots
                blocked.append((start_time, end_time))
        blocked_sorted = blocked.sort(key= lambda x: x[0])
        valid_spaces = []
        for i in range(len(blocked_sorted)):
            if i > 0:
                free_space = blocked_sorted[i][0] - blocked_sorted[i-1][1]
                if free_space >= duration:
                    valid_spaces.append(blocked_sorted[i][0]) # append start point of scheduled job as possible end point
        return len(valid_spaces) > 0, valid_spaces

    def find_best_fit(self, possible_workstations, job, last_slot):
        available_spaces = []
        for workstation in possible_workstations:
            duration = self.environment.get_duration(job.external_id, workstation.external_id)
            _, valid_spaces = self.has_space_before(workstation.external_id, duration, last_slot)
            for space in valid_spaces:
                available_spaces.append((workstation, space))
        best_fit = None
        best_fit_value = float('inf')
        for space in available_spaces:
            if last_slot - space[1] < best_fit_value: # get as close to the previous job as possible
                best_fit = space
                best_fit_value = last_slot - space[1]
        return best_fit

    def process(self, order : Order):
        recipes = []
        for resource in order.resources:
            recipes.append((order.id, resource.recipes[0])) # still ignore possibility of multiple recipes#
        # gather all jobs
        tasks = []
        for recipe in recipes:
            path = recipe[1].tasks
            path.reverse()
            tasks.append(path)
        success_count = 0
        delivery_date = order.delivery_time
        last_acceptable = order.latest_acceptable_time
        for i in range(len(tasks)): # for each recipe
            prev_start = delivery_date
            jobs = tasks[i]
            chosen_workstation = None
            for j in range(len(jobs)): # schedule each job for each recipe
                possible_workstations = self.environment.get_valid_workstations(jobs[j])
                for workstation in possible_workstations:
                    duration = self.environment.get_duration(jobs[j].external_id, workstation.external_id)
                    best_start_slot = prev_start - duration
                    if not self.is_blocked(workstation.external_id, best_start_slot, duration):
                        chosen_workstation = workstation
                        break
                if chosen_workstation:
                    prev_start = best_start_slot
                    self.state.add((chosen_workstation, best_start_slot), jobs[j].external_id, order.external_id)
                    success_count += 1
                else:
                    # find best fit if ideal position can not be chosen on any possible workstation
                    best_fit = self.find_best_fit(possible_workstations, jobs[j], prev_start)
                    if best_fit is not None:
                        duration = self.environment.get_duration(jobs[j].external_id, best_fit[0].external_id)
                        best_start_slot = best_fit[1] - duration
                        self.state.add((best_fit[0], best_start_slot), jobs[j].external_id, order.external_id)
                        success_count += 1
                    else:
                        # delay prev job
                        # try finding any valid space between current assignments
                        # push back prev task to allow for it
                        # if no space can be found at all, add to the end of the (valid) workstation with the smallest 
                        # makespan (earliest possible), change prev job start as soon as possible after - repeat for prev
                        # jobs of the prev job, ... until the whole recipe is rescheduled in a valid way
                        best_fit = self.find_best_fit(possible_workstations, jobs[j], last_acceptable)
                        if best_fit is not None:
                            duration = self.environment.get_duration(jobs[j].external_id, best_fit[0].external_id)
                            best_start_slot = best_fit[1] - duration
                            self.state.add((best_fit[0], best_start_slot), jobs[j].external_id, order.external_id)
                            success_count += 1
                            # TODO: go through previous tasks, do the same
                        else:
                            # job has to be appended at the end
                            earliest_possible = None
                            for workstation in possible_workstations:
                                for assignment in workstation.assignments:
                                    duration = self.environment.get_duration(assignment[0], workstation.external_id)
                                    start = assignment[1] # I think
                                    end = start + duration
                                    if earliest_possible is None or earliest_possible[1] > end: # find earliest end point
                                        earliest_possible = (workstation, end)
                            self.state.add((earliest_possible[0], earliest_possible[1]), jobs[j].external_id, order.external_id)
                            # TODO: go through previous tasks, add after this task
                        pass
        return success_count