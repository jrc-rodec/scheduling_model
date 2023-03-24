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

    def __init__(self, id : str, name : str = None, tasks : list[tuple[Task, int, int]] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'r{self.id}'
        self.tasks = tasks


class Vendor(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, name : str = None, resources : list = [], event_log : list[Event] = []) -> None:
        self.__init__(Vendor.next_id, name, resources, event_log)
        Vendor.next_id += 1

    def __init__(self, id : str, name : str = None, resources : list = [], event_log : list[Event] = []) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'v{self.id}'
        self.resources = resources
        self.event_log = event_log


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


class Solver(Entitiy):
    
    next_id : int = 0

    def __init__(self, name : str = None, parameters : dict = dict()) -> None:
        self.__init__(Solver.next_id, name, parameters)
        Solver.next_id += 1

    def __init__(self, id : str, name : str = None, parameters : dict = dict()) -> None:
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f's{self.id}'
        self.parameters = parameters


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

        self.event_log : dict[str, Event] = [] # list of all events
        self.workstations : dict[str, Workstation] = []
        self.recipes : dict[str, Recipe] = []
        self.tasks : dict[str, Task] = []
        self.customers : dict[str, Customer] = []
        self.schedules : dict[str, Schedule] = [] # past schedules
        self.orders : dict[str, Order] = []
        self.setup_groups : dict[str, SetupGroup] = []
        self.vendors : dict[str, Vendor] = []
        self.resources : dict[str, tuple[Resource, int]] = []

    def get_resource(self, id : str) -> Resource:
        return self.resources.get(id)[0]
    
    def get_stock(self, id : str) -> int:
        return self.resources.get(id)[1]
    
    def get_customer(self, id : str) -> Customer:
        return self.customers.get(id)
    
    def get_recipe(self, id : str) -> Recipe:
        return self.recipes.get(id)
    
    def get_workstation(self, id : str) -> Workstation:
        return self.workstations.get(id)
    
    def get_task(self, id : str) -> Task:
        return self.tasks.get(id)
    
    def get_event(self, id : str) -> Event:
        return self.event_log.get(id)
    
    def get_schedule(self, id : str) -> Schedule:
        return self.schedules.get(id)
    
    def get_order(self, id : str) -> Order:
        return self.orders.get(id)
    
    def get_setup_group(self, id : str) -> SetupGroup:
        return self.setup_groups.get(id)
    
    def get_vendor(self, id : str) -> Vendor:
        return self.vendors.get(id)
    
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