from models import Schedule, SimulationEnvironment, Order
import random 
from optimizer_components import get_by_id, get_duration, get_all_workstations_for_task
class Agent:

    def __init__(self, simulation_environment : SimulationEnvironment):
        self.environment = simulation_environment
        self.state = Schedule()

    def process(self, order : Order) -> bool:
        pass

    def get_state(self) -> Schedule:
        return self.state

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

    def is_blocked(self, workstation_id, start_time, duration):
        assignments = self.state.assignments_for(workstation_id)
        if assignments:
            for assignment in assignments:
                assignment_start_time = assignment[1]
                assignment_duration = get_duration(assignment[0], workstation_id, self.environment.workstations)
                if start_time > assignment_start_time and start_time < assignment_start_time + assignment_duration:
                    return True
                if start_time + duration > assignment_start_time and start_time + duration < assignment_start_time + assignment_duration:
                    return True
        return False 

    def process(self, order : Order):
        recipes = []
        for resource in order.resources:
            recipes.append((order.id, resource.recipes))
        tasks = []
        for recipe in recipes:
            path = self.pick_random_path(recipe[1][0]) # ignore possibility of multiple recipes for now
            path.reverse()
            tasks.append(path) # add in reverse order for each recipe
        success_count = 0
        for i in range(len(tasks)):
            prev_duration = 0
            for j in range(len(tasks[i])):
                task = tasks[i][j]
                workstations = get_all_workstations_for_task(self.environment.workstations, task.external_id, self.environment.tasks)
                chosen_workstation = None
                for workstation in workstations:
                    duration = get_duration(task.external_id, workstation.external_id, self.environment.workstations)
                    start_slot = order.delivery_time - prev_duration - duration
                    if not self.is_blocked(workstation.external_id, start_slot, duration):
                        chosen_workstation = workstation
                        break            
                if chosen_workstation:    
                    prev_duration += duration
                    self.state.add((chosen_workstation, start_slot), task.external_id)
                    success_count += 1
                else:
                    if not order.divisible: # if order can not only be partially fullfilled too
                        return False
                    else:
                        break
        return success_count > 0
            