from datetime import datetime
import random 
# id and external id is the same for all models for now
class Task:

    def __init__(self, id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time):
        self.id = id
        self.external_id = id
        self.name = name
        self.resources = resources
        self.result_resources = result_resources
        self.preceding_tasks = preceding_tasks
        self.follow_up_tasks = follow_up_tasks
        self.independent = independent
        self.prepare_time = prepare_time
        self.unprepare_time = unprepare_time

class Recipe:

    def __init__(self, id, name, tasks):
        self.id = id
        self.external_id = id
        self.name = name
        self.tasks = tasks

class Resource:
    
    def __init__(self, id, name, stock, price, renewable, recipes, delivery_delay):
        self.id = id
        self.external_id = id
        self.name = name
        self.stock = stock
        self.price = price
        self.renewable = renewable
        self.recipes = recipes # possible recipes to create this resource
        self.delivery_delay = delivery_delay

class Workstation:

    def __init__(self, id, name, basic_resources, tasks):
        self.id = id
        self.external_id = id
        self.external_id = self.id
        self.name = name
        self.basic_resources = basic_resources # list of resources necessary to operate the workstation independent of performed task
        self.tasks = tasks # tasks which can be done with this workstation

class Order:

    def __init__(self, id, arrival_time, delivery_time, latest_acceptable_time, resources, penalty, tardiness_fee, divisible, customer_id, optional):
        self.id = id
        self.external_id = id
        self.arrival_time = arrival_time
        self.delivery_time = delivery_time
        self.latest_acceptable_time = latest_acceptable_time
        self.resources = resources # <Resource, (Amount + Price)> currently [resource_id, amount, price]
        self.penalty = penalty
        self.tardiness_fee = tardiness_fee
        self.divisible = divisible
        self.customer_id = customer_id
        self.optional = optional

class Job:
    
    next_id = 0

    def __init__(self, order : Order, task : int, index : int):
        self.id = Job.next_id
        Job.next_id += 1
        self.order_id = order.id # could just add order instead
        self.task_id = task # could just add task instead
        self.to_id = index # tasks index in orders tasks list (in case the same task happens more than once for an order) (basically operation id)

class Schedule:
    
    def __init__(self):
        self.assignments = dict() # <workstation_id, list of jobs>

    def assignments_for(self, workstation_id : int) -> list:
        if workstation_id in self.assignments:
            return self.assignments[workstation_id]
        return None

    def add(self, assignment : tuple, task_id : int, order_id : int):
        if assignment[0] not in self.assignments:
            self.assignments[assignment[0]] = list()
        self.assignments[assignment[0]].append([task_id, assignment[1], order_id])

    def is_feasible(self) -> bool:
        pass


class SimulationEnvironment:
    
    def __init__(self, workstations, tasks, resources, recipes):
        # TODO: change all lists to dictionaries
        self.workstations = workstations # set of all workstations
        self.tasks = tasks # set of all possible tasks
        self.resources = resources # set of all existing resources
        self.recipes = recipes # set of all available recipes
        self.inventory = dict() # <Resource, amount> starting state of the systems resources
        for resource in self.resources:
            if not resource in self.inventory:
                self.inventory[resource] = 0
            self.inventory[resource] += resource.stock
    
    def create_input(self, orders) -> tuple[list, list]:
        jobs = list()
        assignments = list()
        for order in orders:
            for resource in order.resources:
                r = self.get_resource_by_external_id(resource[0])
                # <resource, (amount, price)>
                if len(r.recipes) > 0: # if resource can be produced
                    # choose random available recipe for now
                    recipe = self.get_recipe_by_external_id(random.choice(r.recipes))
                    index = 0
                    for task in recipe.tasks:
                        t = self.get_task_by_external_id(task)
                        for preceding_task in t.preceding_tasks:
                            # assigning all tasks to workstation 0 by default for now
                            jobs.append(Job(order, preceding_task, index))
                            assignments.append([0, 0])
                            index += 1
                        jobs.append(Job(order, task, index))
                        index += 1
                        assignments.append([0, 0])
                        for follow_up_task in t.follow_up_tasks:
                            jobs.append(Job(order, follow_up_task, index))
                            assignments.append([0, 0])
                            index += 1
                else:
                    # resource has to be bought
                    pass
        return jobs, assignments # making sure all assignments are at the same index as their respective job
        
    def print(self):
        print(f'Printing Simulation Environment:')
        print(f'Workstations:')
        for workstation in self.workstations:
            print(f'Id:{workstation.external_id}:{workstation.name} can do {len(workstation.tasks)} different tasks')
        print(f'Resources:')
        for resource in self.resources:
            print(f'Id:{resource.external_id}:{resource.name}')
        print(f'Recipes:')
        for recipe in self.recipes:
            print(f'Id:{recipe.external_id}:{recipe.name}')
        print(f'Tasks:')
        for task in self.tasks:
            print(f'Id:{task.external_id}:{task.name} has {len(task.preceding_tasks)} preceding and {len(task.follow_up_tasks)} follow up tasks')

    def read_output(self, jobs, output) -> Schedule:
        schedule = Schedule()
        for i in range(len(output)):
            schedule.add(output[i][0], (jobs[i], output[i][1]))
        return schedule

    def get_duration(self, task_id : int, workstation_id : int) -> int:
        workstation : Workstation = self.get_workstation(workstation_id)
        for task in workstation.tasks:
            if task[0] == task_id:
                return task[1]
        return 0

    def get_workstation(self, workstation_id : int) -> Workstation:
        for workstation in self.workstations:
            if workstation.id == workstation_id:
                return workstation
        return None
    
    def get_workstation_by_external_id(self, workstation_id : int) -> Workstation:
        for workstation in self.workstations:
            if workstation.external_id == workstation_id:
                return workstation
        return None

    def get_valid_workstations(self, task_id : int):
        result = []
        for workstation in self.workstations:
            for task in workstation.tasks:
                if task[0] == task_id:
                    result.append(workstation)
                    break
        return result

    def get_task(self, task_id : int) -> Task:
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_task_by_external_id(self, task_id : int) -> Task:
        for task in self.tasks:
            if task.external_id == task_id:
                return task
        return None

    def get_resource(self, resource_id : int) -> Resource:
        for resource in self.resources:
            if resource.id == resource_id:
                return resource
        return None
    
    def get_resource_by_external_id(self, resource_id : int) -> Resource:
        for resource in self.resources:
            if resource.external_id == resource_id:
                return resource
        return None
    
    def get_recipe(self, recipe_id : int) -> Recipe:
        for recipe in self.recipes:
            if recipe.id == recipe_id:
                return recipe
        return None
    
    def get_recipe_by_external_id(self, recipe_id : int) -> Recipe:
        for recipe in self.recipes:
            if recipe.external_id == recipe_id:
                return recipe
        return None

    def get_all_tasks(self, task):
        all = []
        if isinstance(task, int):
            task = self.get_task(task)
        for pre in task.preceding_tasks:
            all += self.get_all_tasks(pre)
        all.append(task)
        for follow_up in task.follow_up_tasks:
            all += self.get_all_tasks(follow_up)
        return all

    # TODO: fix if needed after all
    def get_all_tasks_for_recipe(self, recipe_id : int):
        recipe = self.get_recipe(recipe_id)
        all = []
        for task in recipe.tasks:
            all += self.get_all_tasks(task)
        return all