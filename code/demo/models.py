from solver import Solver

class Workstation:

    def __init__(self, id, name, basic_resources, tasks):
        self.id = id
        self.external_id = id
        self.external_id = self.id
        self.name = name
        self.basic_resources = basic_resources # list of resources necessary to operate the workstation independent of performed task
        self.tasks = tasks # tasks which can be done with this workstation

class Task:

    def __init__(self, id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time, alternatives):
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
        self.alternatives = alternatives

class Recipe:

    def __init__(self, id, name, tasks):
        self.id = id
        self.external_id = id
        self.name = name
        self.tasks = tasks

class Order:

    def __init__(self, id, arrival_time, delivery_time, latest_acceptable_time, resources, penalty, tardiness_fee, divisible, customer_id, optional, payment_amount = 0):
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
        self.payment_amount = payment_amount

class SimulationEnvironment:
    
    def __init__(self, workstations, tasks, resources, recipes, inventory = dict()):
        # TODO: change all lists to dictionaries
        self.workstations = workstations # set of all workstations
        self.tasks = tasks # set of all possible tasks
        self.resources = resources # set of all existing resources
        self.recipes = recipes # set of all available recipes
        self.inventory = inventory # <Resource, amount> starting state of the systems resources
        for resource in self.resources:
            if not resource in self.inventory:
                self.inventory[resource] = 0
            self.inventory[resource] += resource.stock

    def get_recipe_by_id(self, id : int):
        for recipe in self.recipes:
            if recipe.id == id:
                return recipe
        return None

    def get_all_workstations_for_task(self, id : int):
        result = []
        for workstation in self.workstations:
            for task_duration in workstation.tasks:
                if task_duration[0] == id and task_duration[1] != 0: #NOTE: for now, duration 0 just indicates the task can not be processed on the workstation
                    result.append(workstation)
                    break
        return result

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

class Schedule:
    
    def __init__(self):
        self.assignments = dict() # <workstation_id, list of jobs>
        self.created_by = None
        self.created_in = None
        self.created_for = None
        self.evaluation_results = []

        """    def __init__(self, assignments, created_by = None, created_in : SimulationEnvironment = None, created_for = None):
        self.assignments = assignments
        self.created_by = created_by
        if created_in is not None:
            self.created_in = SimulationEnvironment(**created_in)
        else:
            self.created_in = created_in
        self.created_for = created_for
        self.evaluation_results = []"""

    def assignments_for(self, workstation_id : int) -> list:
        if workstation_id in self.assignments:
            return self.assignments[workstation_id]
        return None

    def add(self, assignment : tuple, task_id : int, order_id : int):
        if assignment[0] not in self.assignments: #workstation id
            self.assignments[assignment[0]] = list()
        self.assignments[assignment[0]].append([task_id, assignment[1], order_id]) # task id, start time, order id

    def workstation_for(self, task_id):
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment[0] == task_id:
                    return workstation
        return -1 

    def start_time_for(self, job_id):
        assignemnts = self.assignments_for(self.workstation_for(job_id))
        for assignment in assignemnts:
            if assignment[0] == job_id:
                return assignment[1]
        return -1

    def is_feasible(self) -> bool:
        pass