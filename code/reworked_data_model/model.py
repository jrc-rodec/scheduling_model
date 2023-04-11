from enum import Enum

class Entitiy:

    def __init__(self, id : int) -> None:
        self.id = id

    def __eq__(self, other) -> bool:
        return self.__class__ == other.__class__ and str(self.id) == str(other.id)
    
    def __ne__(self, other) -> bool:
        return not self == other


class Event(Entitiy):
    
    next_id : int = 0
    
    def __init__(self, id : str = None, event_type_id : int = 0, parameters : dict = dict()) -> None:
        if not id:
            id = Event.next_id
            Event.next_id += 1
        super().__init__(id)
        self.event_type_id = event_type_id
        self.parameters = parameters

    def get_parameter(self, key):
        return self.parameters.get(key)


class Task(Entitiy):
    
    next_id : int = 0

    def __init__(self, id : str = None, name : str = None, required_resources : list[tuple] = [], products : list[tuple] = [], independent : bool = False, setup_groups : list = []) -> None:
        if not id:
            id = Task.next_id
            Task.next_id += 1
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

    def __init__(self, id : str = None, name : str = None, tasks : list[tuple[list[Task], int, int]] = []) -> None:
        if not id:
            id = Recipe.next_id
            Recipe.next_id += 1
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'r{self.id}'
        self.tasks = tasks

    def get_sequence_value_for_task(self, task : Task) -> int:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative == task:
                    return task[1]
        return None
    
    def get_finish_before_value_for_task(self, task : Task) -> int:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative == task:
                    return task[2]
        return None
    
    def get_task(self, id : str) -> Task:
        for task in self.tasks:
            for alternative in task[0]:
                if str(alternative.id) == str(id):
                    return alternative
        return None
    
    def get_alternatives(self, task : Task) -> list[Task]:
        for task in self.tasks:
            for alternative in task[0]:
                if alternative == task:
                    return task[0]
        return None


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

    def get_expected_delivery_time_for_resource(self, resource) -> int:
        for r in self.resources:
            if r[0] == resource:
                return r[4]
        return None
            
    def get_min_amount_for_resource(self, resource) -> int:
        for r in self.resources:
            if r[0] == resource:
                return r[2]
        return None
            
    def get_max_amount_for_resource(self, resource) -> int:
        for r in self.resources:
            if r[0] == resource:
                return r[3]
        return None
    
    def get_price_per_unit_for_resource(self, resource) -> float:
        for r in self.resources:
            if r[0] == resource:
                return r[1]
        return None
    
    def get_available_resources(self) -> list:
        resources = []
        for resource in self.resources:
            resources.append(resource[0])
        return resources


class Resource(Entitiy):

    next_id : int = 0

    def __init__(self, id : str = None, name : str = None, stock : int = 0, reusable : bool = False, recipes : list[Recipe] = [], vendors : list[Vendor] = [], events : list[Event] = []) -> None:
        if not id:
            id = Resource.next_id
            Resource.next_id += 1
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

import copy
class Workstation(Entitiy):
    
    next_id : int = 0

    #NOTE: apparently, when objects (lists in this case) are used as default, there's only one list, and every object has a reference to the same list
    def __init__(self, id : str = None, name : str = None, basic_resources : list[tuple[Resource, int]] = [], tasks : list = [], workstation_type_id : int = 0, event_log : list[Event] = []) -> None:
        if not id:
            id = Workstation.next_id
            Workstation.next_id += 1
        super().__init__(id)
        if name:
            self.name = name
        else:
            self.name = f'w{self.id}'
        self.basic_resources = basic_resources
        self.tasks = copy.deepcopy(tasks)
        self.workstation_type_id = workstation_type_id
        self.event_log = event_log

    def get_duration(self, task : Task) -> int:
        for t in self.tasks:
            if task == t[0]:# str(task[0].id) == str(task_id):
                return t[1]
        return 0


class SetupGroup(Entitiy):
    
    next_id : int = 0

    def __init__(self, id : str = None, setup_time : int = 0, disassemble_time : int = 0, workstation_id : str = 0) -> None:
        if not id:
            id = SetupGroup.next_id
            SetupGroup.next_id += 1
        super().__init__(id)
        self.setup_time = setup_time
        self.disassemble_time = disassemble_time
        self.workstation_id = workstation_id


class Order(Entitiy):
    
    next_id : int = 0

    def __init__(self, id : str = None, arrival_time : int = 0, delivery_time : int = 0, latest_acceptable_time : int = 0, resources : list[tuple] = [], penalty : float = 0.0, tardiness_fee : float = 0.0, divisible : bool = False, customer_id : str = 0, priority_level : int = 0, profit : float = 0) -> None:
        if not id:
            id = Order.next_id
            Order.next_id += 1
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
        self.profit = profit


class Job(Entitiy):
    
    next_id : int = 0

    def __init__(self, id : str = None, order : Order = None, recipe : Recipe = None, task : Task = None, ro_id : str = 0) -> None:
        if not id:
            id = Job.next_id
            Job.next_id += 1
        super().__init__(id)
        self.order = order
        self.recipe = recipe
        self.task = task
        self.ro_id = ro_id


class Assignment(Entitiy):
    
    next_id : int = 0

    def __init__(self, id : str = None, job : Job = None, start_time : int = 0, end_time : int = 0, resources : list[tuple] = []) -> None:
        if not id:
            id = Assignment.next_id
            Assignment.next_id += 1
        super().__init__(id)
        self.job = job
        self.start_time = start_time
        self.end_time = end_time
        self.resources = resources


class Schedule(Entitiy):
    
    next_id : int = 0

    def __init__(self, id : str = None, start_time : int = 0, assignments : dict[Workstation, list[Assignment]] = dict(), objective_values : list = [], solver = None) -> None:
        if not id:
            id = Schedule.next_id
            Schedule.next_id += 1
        super().__init__(id)
        self.start_time = start_time
        self.assignments = assignments
        self.objective_values = objective_values
        self.solver = solver

    def _get_assignment_for_job(self, job : Job) -> Assignment:
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.job == job:
                    return assignment
        return None
    
    def _get_workstation_for_job(self, job : Job) -> Workstation:
        for workstation in self.assignments.keys():
            for assignment in self.assignments[workstation]:
                if assignment.job == job:
                    return workstation
        return None

    def is_feasible(self, jobs : list[Job]) -> bool:
        recipe = jobs[0].recipe
        order = jobs[0].order
        task = jobs[0].task

        for job in jobs:
            # check sequence for each order
            if job.order == order and job.recipe == recipe:
                sequence_value = recipe.get_sequence_value_for_task()
                finish_before_value = recipe.get_finish_before_value_for_task()

                assignment = self._get_assignment_for_job(job)
                finished = self.get_completed_assignments(assignment.start_time) # check for assignments that are finished when this assignment starts
                for workstation, finished_assignment in finished:
                    if finished_assignment.job.order == job.order and finished_assignment.job.recipe == job.recipe:
                        if finished_assignment.job.recipe.get_finish_before_value_for_task(finished_assignment.job.task) >= sequence_value: # NOTE: maybe just >, not necessarily >=, but probably >=
                            return False # sequence violation, current assignment should be finished already
                        if finished_assignment.job.recipe.get_sequence_value_for_task(finished_assignment.job.task) >= sequence_value:
                            return False # sequence violation, finished assignment should not have started before the current assignment
                
                # check if previous tasks belonging to the recipe are completed
                active = self.get_active_assignments(assignment.end_time) # check for assignments that are still active when the current one finishes
                for workstation, active_assignment in active:
                    if active_assignment.job.order == job.order and active_assignment.job.recipe == job.recipe:
                        if finish_before_value >= active_assignment.job.recipe.get_sequence_value_for_task(active_assignment.job.task):
                            return False # sequence violation, current assignment should have finished before the active assignment started
                        if sequence_value >= active_assignment.job.recipe.get_finish_before_value_for_task(active_assignment.job.task):
                            return False # sequence violation, active assignment should have been finished before the current assignment started
                        
                planned = self.get_assignments_after(assignment.start_time) # check for assignments that start after the current one
                for workstation, planned_assignment in planned:
                    if planned_assignment.job.order == job.order and planned_assignment.job.recipe == job.recipe:
                        if planned_assignment.job.recipe.get_sequence_value_for_task(planned_assignment.job.task) < sequence_value:
                            return False # sequence violation, should have already started
                        if planned_assignment.job.recipe.get_finish_before_value_for_task(planned_assignment.job.task) < sequence_value:
                            return False # sequence violation, should have already been finished
                # NOTE: there are probably more sequence violations

            recipe = job.recipe
            order = job.order
            task = job.task # probably unnecessary
            
        for workstation in self.assignments.keys():
            # check order on workstations and resource availability
            for i in range(1, len(self.assignments[workstation])):
                latest_start_time = self.assignments[workstation][i].end_time - workstation.get_duration(self.assignments[workstation][i].job.task)
                if self.solver.solver_mode == SolverMode.TIME_WINDOW and self.assignments[workstation][i-1].end_time > latest_start_time:
                    return False # too much time window overlap, should cover everything, NOTE: order sequence check may need to be changed for the same reasons
                elif self.assignments[workstation][i].start_time < self.assignments[workstation][i-1].end_time:
                    return False # overlap, NOTE: different rules are necessary for time window optimization, restrict overlap size instead
                # TODO: check resources
        return True

    def _get_workstation(self, id : str) -> Workstation:
        for workstation in self.assignments.keys():
            if str(workstation) == str(id):
                return workstation
        return None
    
    def add_assignment(self, workstation : Workstation, job : Job, start_time : int, end_time : int, resources : list[tuple]) -> None:
        if str(workstation.id) not in self.assignments:
            self.assignments[str(workstation.id)] = []
        self.assignments[str(workstation.id)].append(Assignment(job=job, start_time=start_time, end_time=end_time, resources=resources))
        pass

    def get_assignments_for_order_recipe(self, job : Job) -> list[Assignment]:
        assignments = []
        # TODO: Switch to this method in feasibility check
        for workstation in self.assignments:
            for assignment in self.assignments[workstation]:
                if assignment.job != job and assignment.job.order == job.order and assignment.job.recipe == job.recipe:
                    assignments.append(assignment)
        return assignments

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
    
    def get_active_assignments_on_workstation(self, id : str, time : int) -> list[Assignment]:
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
    
    def get_assignments_on_workstation_after(self, id : str, time : int) -> list[Assignment]:
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
    
    def get_assignments_on_workstation_between(self, id : str, start_time : int, end_time : int) -> list[Assignment]:
        workstation : Workstation = self._get_workstation(id)
        assignments : list[Assignment] = []
        if workstation:
            for assignment in self.assignments[workstation]:
                if (assignment.start_time >= start_time and assignment.start_time <= end_time) or (assignment.end_time >= start_time and assignment.end_time <= end_time):
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

    def get_available_workstations_for_task(self, task : Task) -> list[Workstation]:
        workstations : list[Workstation] = []
        for workstation in self.workstations.values():
            for t in workstation.tasks:
                if task == t[0]:# str(task[0].id) == str(task_id):
                    workstations.append(workstation)
                    break
        return workstations
    
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
