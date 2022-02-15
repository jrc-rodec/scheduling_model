from datetime import datetime

class Task:
    next_id = 0
    def __init__(self, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time):
        self.id = Task.next_id
        self.external_id = self.id
        Task.next_id += 1
        self.name = name
        self.resources = resources
        self.result_resources = result_resources
        self.preceding_tasks = preceding_tasks
        self.follow_up_tasks = follow_up_tasks
        self.independent = independent
        self.prepare_time = prepare_time
        self.unprepare_time = unprepare_time

    def __init__(self, id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time):
        self.id = Task.next_id
        Task.next_id += 1
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

    next_id = 0
    def __init__(self, name, tasks):
        self.id = Recipe.next_id
        Recipe.next_id += 1
        self.external_id = self.id
        self.name = name
        self.tasks = tasks
    
    def __init__(self, id, name, tasks):
        self.id = Recipe.next_id
        Recipe.next_id += 1
        self.external_id = id
        self.name = name
        self.tasks = tasks

class Resource:
    
    next_id = 0
    def __init__(self, name, stock, price, renewable, recipes):
        self.id = Resource.next_id
        Resource.next_id += 1
        self.external_id = self.id
        self.name = name
        self.stock = stock
        self.price = price
        self.renewable = renewable
        self.recipes = recipes # possible recipes to create this resource

    def __init__(self, id, name, stock, price, renewable, recipes):
        self.id = Resource.next_id
        Resource.next_id += 1
        self.external_id = id
        self.name = name
        self.stock = stock
        self.price = price
        self.renewable = renewable
        self.recipes = recipes # possible recipes to create this resource

class Workstation:
    
    next_id = 0
    def __init__(self, name, basic_resources, tasks):
        self.id = Workstation.next_id
        Workstation.next_id += 1
        self.external_id = self.id
        self.name = name
        self.basic_resources = basic_resources # list of resources necessary to operate the workstation independent of performed task
        self.tasks = tasks # tasks which can be done with this workstation

    def __init__(self, id, name, basic_resources, tasks):
        self.id = Workstation.next_id
        Workstation.next_id += 1
        self.external_id = id
        self.external_id = self.id
        self.name = name
        self.basic_resources = basic_resources # list of resources necessary to operate the workstation independent of performed task
        self.tasks = tasks # tasks which can be done with this workstation

class Order:

    next_id = 0
    def __init__(self, arrival_time, delivery_time, latest_acceptable_time, resources, penalty, tardiness_fee, divisible, customer_id):
        self.id = Order.next_id
        Order.next_id += 1
        self.external_id = self.id
        self.arrival_time = arrival_time
        self.delivery_time = delivery_time
        self.latest_acceptable_time = latest_acceptable_time
        self.resources = resources # <Resource, (Amount + Price)>
        self.penalty = penalty
        self.tardiness_fee = tardiness_fee
        self.divisible = divisible
        self.customer_id = customer_id

    def __init__(self, id, arrival_time, delivery_time, latest_acceptable_time, resources, penalty, tardiness_fee, divisible, customer_id):
        self.id = Order.next_id
        Order.next_id += 1
        self.external_id = id
        self.arrival_time = arrival_time
        self.delivery_time = delivery_time
        self.latest_acceptable_time = latest_acceptable_time
        self.resources = resources # <Resource, (Amount + Price)>
        self.penalty = penalty
        self.tardiness_fee = tardiness_fee
        self.divisible = divisible
        self.customer_id = customer_id

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
    
    def __init__(self, workstations, tasks, resources, inventory):
        self.workstations = workstations # set of all workstations
        self.tasks = tasks # set of all possible tasks
        self.resources = resources # set of all existing resources
        self.inventory = inventory # <Resource, amount> starting state of the systems resources
        
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
                            index += 1
                        jobs.append(Job(order, task, index))
                        index += 1
                        assignments.append([0, 0])
                        for follow_up_task in task.follow_up_tasks:
                            jobs.append(Job(order, follow_up_task, index))
                            assignments.append([0, 0])
                            index += 1
                else:
                    # resource has to be bought
                    pass
        return jobs, assignments # making sure all assignments are at the same index as their respective job

    def read_output(self, jobs, output) -> Schedule:
        schedule = Schedule()
        for i in range(len(output)):
            schedule.add(output[i][0], (jobs[i], output[i][1]))
        return schedule

    def simulate(self):
        pass

    def generate_orders(self) -> list:
        pass