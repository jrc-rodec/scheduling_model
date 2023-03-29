from enum import Enum

class Entitiy:

    def __init__(self, id : int) -> None:
        self.id = id


class Event(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, event_type_id : int = 0, parameters : dict = dict()) -> None:
        self.__init__(Event.next_id, event_type_id, parameters)
        Event.next_id += 1
        
    def __init__(self, id : str, event_type_id : int = 0, parameters : dict = dict()) -> None:
        super().__init__(id)
        self.event_type_id = event_type_id
        self.parameters = parameters

    def get_parameter(self, key):
        return self.parameters.get(key)


class Task(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, name : str = None, required_resources : list[tuple] = [], products : list[tuple] = [], independent : bool = False, setup_groups : list = []) -> None:
        self.__init__(Task.next_id, name, required_resources, products, independent, setup_groups)
        Task.next_id += 1

    def __init__(self, id : str, name : str = None, required_resources : list[tuple] = [], products : list[tuple] = [], independent : bool = False, setup_groups : list = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f't{self.id}'
        self.required_resources = required_resources
        self.products = products
        self.independent = independent
        self.setup_groups = setup_groups


class Recipe(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, name : str = None, tasks : list[tuple[Task, int, int]] = []) -> None:
        self.__init__(Recipe.next_id, name, tasks)
        Recipe.next_id += 1

    def __init__(self, id : str, name : str = None, tasks : list[tuple[list[Task], int, int]] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'r{self.id}'
        self.tasks = tasks

    def get_sequence_value_for_task(self, id : str) -> int:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative.id == id:
                    return task[1]
        return None
    
    def get_finish_before_value_for_task(self, id : str) -> int:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative.id == id:
                    return task[2]
        return None
    
    def get_task(self, id : str) -> Task:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative.id == id:
                    return alternative
        return None
    
    def get_alternatives(self, id : str) -> list[Task]:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative.id == id:
                    return task[0]


class Vendor(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, name : str = None, resources : list = [], event_log : list[Event] = []) -> None:
        self.__init__(Vendor.next_id, name, resources, event_log)
        Vendor.next_id += 1

    def __init__(self, id : str, name : str = None, resources : list[tuple] = [], event_log : list[Event] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'v{self.id}'
        self.resources = resources # resource, price (per unit), min, max, expected delivery time
        self.event_log = event_log

    def get_expected_delivery_time_for_resource(self, id : str) -> int:
        for resource in self.resources:
            if resource[0].id == id:
                return resource[4]
        return None
            
    def get_min_amount_for_resource(self, id : str) -> int:
        for resource in self.resources:
            if resource[0].id == id:
                return resource[2]
        return None
            
    def get_max_amount_for_resource(self, id : str) -> int:
        for resource in self.resources:
            if resource[0].id == id:
                return resource[3]
        return None
    
    def get_price_per_unit_for_resource(self, id : str) -> float:
        for resource in self.resources:
            if resource[0].id == id:
                return resource[1]
        return None
    
    def get_available_resources(self) -> list:
        resources = []
        for resource in self.resources:
            resources.append(resource[0])
        return resources


class Resource(Entitiy):

    next_id : int = 0
    def __init__(self, name : str = None, stock : int = 0, reusable : bool = False, recipes : list[Recipe] = [], vendors : list[Vendor] = [], events : list[Event] = []) -> None:
        self.__init__(Resource.next_id, name, stock, reusable, recipes, vendors, events)
        Resource.next_id += 1

    def __init__(self, id : str, name : str = None, stock : int = 0, reusable : bool = False, recipes : list[Recipe] = [], vendors : list[Vendor] = [], events : list[Event] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'r{self.id}'
        self.stock = stock
        self.reusable = reusable
        self.recipes = recipes
        self.vendors = vendors
        self.events = events


class Workstation(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, name : str = None, basic_resources : list[tuple[Resource, int]] = [], tasks : list = [], workstation_type_id : int = 0, event_log : list[Event] = []) -> None:
        self.__init__(Workstation.next_id, name, basic_resources, tasks, workstation_type_id, event_log)
        Workstation.next_id += 1

    def __init__(self, id : str, name : str = None, basic_resources : list[tuple[Resource, int]] = [], tasks : list = [], workstation_type_id : int = 0, event_log : list[Event] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'w{self.id}'
        self.basic_resources = basic_resources
        self.tasks = tasks
        self.workstation_type_id = workstation_type_id
        self.event_log = event_log


class SetupGroup(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, setup_time : int = 0, disassemble_time : int = 0, workstation_id : str = 0) -> None:
        self.__init__(SetupGroup.next_id, setup_time, disassemble_time, workstation_id)
        SetupGroup.next_id += 1

    def __init__(self, id : str, setup_time : int = 0, disassemble_time : int = 0, workstation_id : str = 0) -> None:
        super().__init__(id)
        self.setup_time = setup_time
        self.disassemble_time = disassemble_time
        self.workstation_id = workstation_id


class Order(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, arrival_time : int = 0, delivery_time : int = 0, latest_acceptable_time : int = 0, resources : list[tuple] = [], penalty : float = 0.0, tardiness_fee : float = 0.0, divisible : bool = False, customer_id : str = 0, priority_level : int = 0) -> None:
        self.__init__(Order.next_id, arrival_time, delivery_time, latest_acceptable_time, resources, penalty, tardiness_fee, divisible, customer_id, priority_level)
        Order.next_id += 1

    def __init__(self, id : str, arrival_time : int = 0, delivery_time : int = 0, latest_acceptable_time : int = 0, resources : list[tuple] = [], penalty : float = 0.0, tardiness_fee : float = 0.0, divisible : bool = False, customer_id : str = 0, priority_level : int = 0) -> None:
        super().__init__(id)
        self.arrival_time = arrival_time
        self.delivery_time = delivery_time
        self.latest_acceptable_time = latest_acceptable_time
        self.resources = resources
        self.penalty = penalty
        self.tardiness_fee = tardiness_fee
        self.divisible = divisible
        self.customer_id = customer_id
        self.priority_level = priority_level


class Job(Entitiy):
    
    next_id : int = 0

    def __init__(self, order_id : str = 0, recipe_id : str = 0, task_id : str = 0, ro_id : str = 0) -> None:
        self.__init__(Job.next_id, order_id, recipe_id, task_id, ro_id)
        Job.next_id += 1

    def __init__(self, id : str, order_id : str = 0, recipe_id : str = 0, task_id : str = 0, ro_id : str = 0) -> None:
        super().__init__(id)
        self.order_id = order_id
        self.recipe_id = recipe_id
        self.task_id = task_id
        self.ro_id = ro_id


class Assignment(Entitiy):
    
    next_id : int = 0

    def __init__(self, job_id : str = 0, start_time : int = 0, end_time : int = 0, resources : list[tuple] = []) -> None:
        self.__init__(Assignment.next_id, job_id, start_time, end_time, resources)
        Assignment.next_id += 1

    def __init__(self, id : str, job_id : str = 0, start_time : int = 0, end_time : int = 0, resources : list[tuple] = []) -> None:
        super().__init__(id)
        self.job_id = job_id
        self.start_time = start_time
        self.end_time = end_time
        self.resources = resources


class Schedule(Entitiy):
    
    next_id : int = 0

    def __init__(self, start_time : int = 0, assignments : dict[Workstation, list[Assignment]] = dict(), objective_values : list = [], solver_id : str = 0) -> None:
        self.__init__(Schedule.next_id, start_time, assignments, objective_values, solver_id)
        Schedule.next_id += 1

    def __init__(self, id : str, start_time : int = 0, assignments : dict[Workstation, list[Assignment]] = dict(), objective_values : list = [], solver_id : str = 0) -> None:
        super().__init__(id)
        self.start_time = start_time
        self.assignments = assignments
        self.objective_values = objective_values
        self.solver_id = solver_id

    def _get_workstation(self, id : str) -> Workstation:
        for workstation in self.assignments.keys():
            if workstation.id == id:
                return workstation
        return None
    
    def get_assignments_before(self, time : int) -> list[tuple[Workstation, Assignment]]:
        assignments : list[tuple[Workstation, Assignment]] = []
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.start_time < time:
                    assignments.append((workstation, assignment))
        return assignments
    
    def get_assignments_after(self, time : int) -> list[tuple[Workstation, Assignment]]:
        assignments : list[tuple[Workstation, Assignment]] = []
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.start_time > time:
                    assignments.append((workstation, assignment))
        return assignments
    
    def get_completed_assignments(self, time : int) -> list[tuple[Workstation, Assignment]]:
        assignments : list[tuple[Workstation, Assignment]] = []
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.end_time < time:
                    assignments.append((workstation, assignment))
        return assignments
    
    def get_uncompleted_assignments(self, time : int) -> list[tuple[Workstation, Assignment]]:
        assignments : list[tuple[Workstation, Assignment]] = []
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.end_time > time:
                    assignments.append((workstation, assignment))
        return assignments
    
    def get_active_assignments(self, time : int) -> list[tuple[Workstation, Assignment]]:
        assignments : list[tuple[Workstation, Assignment]] = []
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.start_time <= time and assignment.end_time > time:
                    assignments.append((workstation, assignment))
        return assignments
    
    def get_active_assignemnts_on_workstation(self, id : str, time : int) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        assignments : list[Assignment] = []
        if workstation:
            for assignment in self.assignemnts[workstation]:
                if assignment.start_time <= time and assignment.end_time > time:
                    assignments.append(assignment)
        return assignments

    def get_assignments_on_workstation_before(self, id : str, time : int) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        assignments : list[Assignment] = []
        if workstation:
            for assignment in self.assignments[workstation]:
                if assignment.start_time < time:
                    assignments.append(assignment)
        return assignments
    
    def get_assignemnts_on_workstation_after(self, id : str, time : int) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        assignments : list[Assignment] = []
        if workstation:
            for assignment in self.assignments[workstation]:
                if assignment.start_time > time:
                    assignments.append(assignment)
        return assignments
    
    def get_completed_assignments_on_workstation(self, id : str, time : int) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        assignments : list[Assignment] = []
        if workstation:
            for assignment in self.assignments[workstation]:
                if assignment.end_time < time:
                    assignments.append(assignment)
        return assignments
    
    def get_uncompleted_assignments_on_workstation(self, id : str, time : int) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        assignments : list[Assignment] = []
        if workstation:
            for assignment in self.assignments[workstation]:
                if assignment.end_time > time:
                    assignments.append(assignment)
        return assignments
    
    def get_assignments_on_workstation(self, id : str) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        return self.assignments.get(workstation)


class SolverMode(Enum):

    TIME_WINDOW = 1
    EXACT = 2

class Solver(Entitiy):
    
    next_id : int = 0

    def __init__(self, name : str = None, parameters : dict = dict()) -> None:
        self.__init__(Solver.next_id, name, parameters)
        Solver.next_id += 1

    def __init__(self, id : str, name : str = None, parameters : dict = dict(), solver_mode : SolverMode = SolverMode.TIME_WINDOW) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f's{self.id}'
        self.parameters = parameters
        self.solver_mode = solver_mode # use either TIME_WINDOW or EXACT

    def get_parameter(self, key):
        return self.parameters.get(key)


class Customer(Entitiy):
    
    next_id : int = 0

    def __init__(self, name : str = 0, priority_level : int = 0, event_log : list[Event] = []) -> None:
        self.__init__(Customer.next_id, name, priority_level, event_log)
        Customer.next_id += 1

    def __init__(self, id : str, name : str = 0, priority_level : int = 0, event_log : list[Event] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'c{self.id}'
        self.priority_level = priority_level
        self.event_log = event_log

class ProductionEnvironment:

    def __init__(self) -> None:
        self.event_table : dict[int, str] = dict()
        self.workstation_table : dict[int, str] = dict()

        self.event_log : dict[str, Event] = dict() # list of all events
        self.workstations : dict[str, Workstation] = dict()
        self.recipes : dict[str, Recipe] = dict()
        self.tasks : dict[str, Task] = dict()
        self.customers : dict[str, Customer] = dict()
        self.schedules : dict[str, Schedule] = dict() # past schedules
        self.orders : dict[str, Order] = dict()
        self.setup_groups : dict[str, SetupGroup] = dict()
        self.vendors : dict[str, Vendor] = dict()
        self.resources : dict[str, tuple[Resource, int]] = dict()

    def add_workstation_type(self, id : str, name : str) -> None:
        if str(id) not in self.workstation_table:
            self.workstation_table[str(id)] = name

    def add_workstation(self, workstation : Workstation) -> None:
        if str(workstation.id) not in self.workstations:
            self.workstations[str(workstation.id)] = workstation

    def add_event(self, event : Event) -> None:
        if str(event.id) not in self.event_log:
            self.event_log[str(event.id)] = event

    def add_recipe(self, recipe : Recipe) -> None:
        if str(recipe.id) not in self.recipes:
            self.recipes[str(recipe.id)] = recipe
    
    def add_task(self, task : Task) -> None:
        if str(task.id) not in self.tasks:
            self.tasks[str(task.id)] = task
    
    def add_customer(self, customer : Customer) -> None:
        if str(customer.id) not in self.customers:
            self.customers[str(customer.id)] = customer
    
    def add_schedule(self, schedule : Schedule) -> None:
        if str(schedule.id) not in self.schedules:
            self.schedules[str(schedule.id)] = schedule
    
    def add_order(self, order : Order) -> None:
        if str(order.id) not in self.orders:
            self.orders[str(order.id)] = order
    
    def add_setup_group(self, setup_group : SetupGroup) -> None:
        if str(setup_group.id) not in self.setup_groups:
            self.setup_groups[str(setup_group.id)] = setup_group
    
    def add_vendor(self, vendor : Vendor) -> None:
        if str(vendor.id) not in self.vendors:
            self.vendors[str(vendor.id)] = vendor
    
    def add_resource(self, resource : Resource) -> None:
        if str(resource.id) not in self.resources:
            self.resources[str(resource.id)] = (resource, resource.stock)

    def get_resource(self, id : str) -> Resource:
        return self.resources.get(str(id))[0]
    
    def get_stock(self, id : str) -> int:
        return self.resources.get(str(id))[1]
    
    def get_customer(self, id : str) -> Customer:
        return self.customers.get(str(id))
    
    def get_recipe(self, id : str) -> Recipe:
        return self.recipes.get(str(id))
    
    def get_workstation(self, id : str) -> Workstation:
        return self.workstations.get(str(id))
    
    def get_task(self, id : str) -> Task:
        return self.tasks.get(str(id))
    
    def get_event(self, id : str) -> Event:
        return self.event_log.get(str(id))
    
    def get_schedule(self, id : str) -> Schedule:
        return self.schedules.get(str(id))
    
    def get_order(self, id : str) -> Order:
        return self.orders.get(str(id))
    
    def get_setup_group(self, id : str) -> SetupGroup:
        return self.setup_groups.get(str(id))
    
    def get_vendor(self, id : str) -> Vendor:
        return self.vendors.get(str(id))
    
    def get_workstation_list(self) -> list[Workstation]:
        return self.workstations.values()
    
    def get_event_list(self) -> list[Event]:
        return self.event_log.values()
    
    def get_recipe_list(self) -> list[Recipe]:
        return self.recipes.values()
    
    def get_task_list(self) -> list[Task]:
        return self.tasks.values()
    
    def get_customer_list(self) -> list[Customer]:
        return self.customers.values()
    
    def get_schedule_list(self) -> list[Schedule]:
        return self.schedules.values()
    
    def get_setup_group_list(self) -> list[SetupGroup]:
        return self.setup_groups.values()
    
    def get_vendor_list(self) -> list[Vendor]:
        return self.vendors.values()
    
    def get_resource_list(self) -> list[Resource]:
        resources : list[Resource] = []
        for resource in self.resources.values():
            resources.append(resource[0])
        return resources
    
    def get_inventory_list(self) -> list[tuple[Resource, int]]:
        return self.resources.values()
