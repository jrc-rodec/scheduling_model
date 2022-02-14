from datetime import datetime

class Task:
    next_id = 0
    def __init__(self):
        self.id = Task.next_id
        Task.next_id += 1
        self.name = ''
        self.resources = []
        self.result_resources = []
        self.preceding_tasks = []
        self.follow_up_tasks = []
        self.independent = True
        self.prepare_time = 0
        self.unprepare_time = 0

class Recipe:

    next_id = 0
    def __init__(self):
        self.id = Recipe.next_id
        Recipe.next_id += 1
        self.name = ''
        self.tasks = []

class Resource:
    
    next_id = 0
    def __init__(self):
        self.id = Resource.id
        Resource.next_id += 1
        self.name = ''
        self.stock = 0
        self.price = 0
        self.renewable = False
        self.recipes = [] # possible recipes to create this resource

class Workstation:
    
    next_id = 0
    def __init__(self):
        self.id = Workstation.next_id
        Workstation.next_id += 1
        self.name = ''
        self.basic_resources = [] # list of resources necessary to operate the workstation independent of performed task
        self.tasks = [] # tasks which can be done with this workstation

class Order:

    next_id = 0
    def __init__(self):
        self.id = Order.next_id
        Order.next_id += 1
        self.arrival_time = datetime.now()
        self.delivery_time = datetime.now()
        self.latest_acceptable_time = datetime.now()
        self.resources = dict() # <Resource, (Amount + Price)>
        self.penalty = 0
        self.tardiness_fee = 0
        self.divisible = False
        self.customer_id = 0

class Job:
    
    next_id = 0
    def __init__(self, order : Order, task : Task, index : int):
        self.id = Job.next_id
        Job.next_id += 1
        self.order_id = order.id # could just add order instead
        self.task_id = task.id # could just add task instead
        self.to_id = index # tasks index in orders tasks list (in case the same task happens more than once for an order)

class Schedule:
    
    def __init__(self):
        self.assignments = dict() # <workstation_id, list of jobs>

    def assignments_for(self, workstation : Workstation) -> list:
        return self.assignments[workstation.id]

    def assignment_for(self, workstation_id : int) -> list:
        return self.assignments[workstation_id]

    def add(self, workstation, assignment):
        self.add(workstation.id, assignment)

    def add(self, workstation_id : int, assignment : tuple):
        if workstation_id not in self.assignments:
            self.assignments[workstation_id] = list()
        self.assignments[workstation_id].append(assignment)

    def is_feasible(self) -> bool:
        pass

class SimulationEnvironment:
    
    def __init__(self):
        self.workstations = [] # set of all workstations
        self.tasks = [] # set of all possible tasks
        self.resources = [] # set of all existing resources
        self.inventory = dict() # <Resource, amount> starting state of the systems resources
        
    def generate_orders(self) -> list:
        pass

    def create_input(self, orders) -> tuple[list, list]:
        jobs = list()
        assignments = list()
        for order in orders:
            for resource in order.resources.keys():
                # <resource, (amount, price)
                #amount = order.resources[resource][0]
                #price = order.resources[resource][1]
                if len(resource.recipes) > 0: # if resource can be produced
                    # choose first available recipe for now
                    recipe = resource.recipes[0]
                    index = 0
                    for task in recipe.tasks:
                        for preceding_task in task.preceding_tasks:
                            # assigning all tasks to workstation 0 by default for now
                            jobs.append(Job(order, preceding_task, index))
                            assignments.append([0, 0])
                        jobs.append(Job(order, task, index))
                        assignments.append([0, 0])
                        for follow_up_task in task.follow_up_tasks:
                            jobs.append(Job(order, follow_up_task, index))
                            assignments.append([0, 0])
                        index += 1
                else:
                    # resource has to be bought
                    pass
        return jobs, assignments # making sure all assignments are at the same index as their respective job

    def simulate(self):
        pass

    def read_output(self, jobs, output) -> Schedule:
        schedule = Schedule()
        for i in range(len(output)):
            schedule.add(output[i][0], (jobs[i], output[i][1]))
        return schedule
