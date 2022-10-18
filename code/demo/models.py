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