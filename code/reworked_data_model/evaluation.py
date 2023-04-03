from model import Schedule, ProductionEnvironment, Job, Order
from uncertainty import ScenarioGenerator

class Objective:

    NEXT_ID = 0

    def __init__(self, name : str) -> None:
        self.id : int = Objective.NEXT_ID
        Objective.NEXT_ID += 1
        self.name : str = name
        self.parameters : dict[str,] = dict()

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job], oders : list[Order]) -> float:
        # TODO: after job changes to objects instead of ids, job and order list can be removed as parameters
        pass

    def add_parameter(self, name : str, value) -> None:
        if name not in self.parameters:
            self.parameters[name] = value
    
    def update_parameter(self, name : str, value) -> None:
        if name in self.parameters:
            self.parameters[name] = value

    def remove_parameter(self, name : str) -> None:
        self.parameters.pop(name)

class Evaluator:

    def __init__(self, production_environment : ProductionEnvironment, orders : list[Order]) -> None:
        self.objectives : list[Objective] = []
        self.scenario_generator : ScenarioGenerator = ScenarioGenerator()
        self.production_environment : ProductionEnvironment = production_environment
        self.orders = orders

    def evaluate(self, schedule : Schedule, jobs : list[Job]) -> list[float]:
        objective_values : list[float] = []
        # TODO: scenario generation
        for objective in self.objectives:
            objective_values.append(objective.evaluate(schedule, self.production_environment, jobs, self.orders))

    def add_objective(self, objective : Objective) -> None:
        self.objectives.append(objective)

    def remove_objective(self, objective : Objective) -> None:
        self.objectives.remove(objective)

"""
    Add additional objectives below
"""

class Makespan(Objective):

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment = None, jobs : list[Job] = [], orders : list[Order] = []) -> float:
        min = float('inf')
        max = 0
        for workstation in schedule.assignments.keys():
            for assignment in schedule.assignments[workstation]:
                if assignment.start_time < min:
                    min = assignment.start_time
                if assignment.end_time > max:
                    max = assignment.end_time
        return max - min

class IdleTime(Objective):
    
    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment = None, jobs : list[Job] = [], orders : list[Order] = []) -> float:
        idle_time = 0
        for workstation in schedule.assignemnts.keys():
            sorted_assignments = sorted(schedule.assignments[workstation], key=lambda x: x.start_time)
            if len(sorted_assignments) > 0:
                idle_time += sorted_assignments[0].start_time
                for i in range(1, len(sorted_assignments)):
                    idle_time += sorted_assignments[i].start_time - sorted_assignments[i-1].end_time
        return idle_time
                

class Tardiness(Objective):
    
    def _get_order(self, orders : list[Order], id : str) -> Order:
        for order in orders:
            if str(order.id) == str(id):
                return order
        return None

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = [], orders : list[Order] = []) -> float:
        tardiness = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            #TODO: change after job is changed to objects
            if job.order_id != prev_job.order_id or job.recipe_id != prev_job.recipe_id or jobs.index(job) == len(jobs)-1:
                # check prev job end_time
                order = self._get_order(prev_job.order_id)
                if prev_job.end_time > order.delivery_time:
                    tardiness += prev_job.end_time - order.delivery_time
            prev_job = job
        return tardiness

class TimeDeviation(Objective):
    
    def _get_order(self, orders : list[Order], id : str) -> Order:
        for order in orders:
            if str(order.id) == str(id):
                return order
        return None

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = [], orders : list[Order] = []) -> float:
        deviation = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            if job.order_id != prev_job.order_id or job.recipe_id != prev_job.recipe_id or jobs.index(job) == len(jobs)-1:
                order = self._get_order(prev_job.order_id)
                deviation += abs(prev_job.end_time - order.delivery_time)
            prev_job = job
        return deviation

class Profit(Objective):
    
    def _get_order(self, orders : list[Order], id : str) -> Order:
        for order in orders:
            if str(order.id) == str(id):
                return order
        return None

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = [], orders : list[Order] = []) -> float:
        profit = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            if job.order_id != prev_job.order_id or job.recipe_id != prev_job.recipe_id or jobs.index(job) == len(jobs)-1:
                order : Order = self._get_order(prev_job.order_id)
                if prev_job.end_time > order.delivery_time:
                    if prev_job.end_time > order.latest_acceptable_time:
                        profit -= order.penalty
                    else:
                        profit += order.profit - order.tardiness_fee
            prev_job = job
        return profit

class UnfulfilledOrders(Objective):

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = [], orders : list[Order] = []) -> float:
        unfulfilled_order_count = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            if job.order_id != prev_job.order_id or job.recipe_id != prev_job.recipe_id or jobs.index(job) == len(jobs)-1:
                # check prev job end_time
                order : Order = self._get_order(prev_job.order_id)
                if prev_job.end_time > order.latest_acceptable_time:
                    unfulfilled_order_count += 1
        return unfulfilled_order_count