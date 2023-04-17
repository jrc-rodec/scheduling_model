from model import Schedule, ProductionEnvironment, Job, Order
from uncertainty import ScenarioGenerator

class Objective:

    NEXT_ID = 0

    def __init__(self, name : str) -> None:
        self.id : int = Objective.NEXT_ID
        Objective.NEXT_ID += 1
        self.name : str = name
        self.parameters : dict[str,] = dict()

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = []) -> float:
        pass

    def add_parameter(self, name : str, value) -> None:
        if name not in self.parameters:
            self.parameters[name] = value
    
    def update_parameter(self, name : str, value) -> None:
        if name in self.parameters:
            self.parameters[name] = value

    def remove_parameter(self, name : str) -> None:
        self.parameters.pop(name)

class FeasibilityConstraint:

    pass

class FeasibilityTester:

    def __init__(self, production_environment : ProductionEnvironment) -> None:
        self.constraints : list[FeasibilityConstraint] = []
        self.production_environment = production_environment

    def test(self, schedule : Schedule, jobs : list[Job]) -> bool:
        i = 0
        feasible = True
        while i < len(self.constraints) and feasible:
            feasible = self.constraints[i].test(schedule, jobs)
            i += 1
        return feasible
    
    def test_all(self, schedule : Schedule, jobs : list[Job]) -> list[bool]:
        results : list[bool] = []
        for constraint in self.constraints:
            results.append(constraint.test(schedule, jobs))
        return results
    
    def add_constraint(self, constraint : FeasibilityConstraint) -> None:
        self.constraints.append(constraint)
    
    def remove_constraint(self, constraint : FeasibilityConstraint) -> None:
        self.constraints.remove(constraint)
    
    def clear_constraints(self) -> None:
        self.constraints.clear()

class Evaluator:

    def __init__(self, production_environment : ProductionEnvironment) -> None:
        self.objectives : list[Objective] = []
        self.scenario_generator : ScenarioGenerator = ScenarioGenerator()
        self.production_environment : ProductionEnvironment = production_environment

    def evaluate(self, schedule : Schedule, jobs : list[Job]) -> list[float]:
        objective_values : list[float] = []
        # TODO: scenario generation
        for objective in self.objectives:
            objective_values.append(objective.evaluate(schedule, self.production_environment, jobs))
        return objective_values

    def add_objective(self, objective : Objective) -> None:
        self.objectives.append(objective)

    def remove_objective(self, objective : Objective) -> None:
        self.objectives.remove(objective)
    
    def clear_objectives(self) -> None:
        self.objectives :list[Objective] = []

"""
    Add additional objectives below
"""

class Makespan(Objective):

    def __init__(self):
        super().__init__('Makespan')
    
    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment = None, jobs : list[Job] = []) -> float:
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
    
    def __init__(self):
        super().__init__('Idle Time')

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment = None, jobs : list[Job] = []) -> float:
        idle_time = 0
        for workstation in schedule.assignments.keys():
            sorted_assignments = sorted(schedule.assignments[workstation], key=lambda x: x.start_time)
            if len(sorted_assignments) > 0:
                idle_time += sorted_assignments[0].start_time
                for i in range(1, len(sorted_assignments)):
                    idle_time += sorted_assignments[i].start_time - sorted_assignments[i-1].end_time
        return idle_time
                

class Tardiness(Objective):

    def __init__(self):
        super().__init__('Tardiness')

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = []) -> float:
        tardiness = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            #TODO: change after job is changed to objects
            if job.order != prev_job.order or job.recipe != prev_job.recipe or job == jobs[-1]:
                # check prev job end_time
                order = prev_job.order
                prev_assignment = schedule._get_assignment_for_job(prev_job)
                if prev_assignment.end_time > order.delivery_time:
                    tardiness += prev_assignment.end_time - order.delivery_time
            prev_job = job
        return tardiness

class TimeDeviation(Objective):

    def __init__(self):
        super().__init__('Time Deviation')

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = []) -> float:
        deviation = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            if job.order != prev_job.order or job.recipe != prev_job.recipe or job == jobs[-1]:
                order = prev_job.order
                deviation += abs(schedule._get_assignment_for_job(prev_job).end_time - order.delivery_time)
            prev_job = job
        return deviation

class Profit(Objective):
    
    def __init__(self):
        super().__init__('Profit')

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = []) -> float:
        profit = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            if job.order != prev_job.order or job.recipe != prev_job.recipe or job == jobs[-1]:
                order : Order = prev_job.order
                prev_assignment = schedule._get_assignment_for_job(prev_job)
                if prev_assignment.end_time > order.delivery_time:
                    if prev_assignment.end_time > order.latest_acceptable_time:
                        profit -= order.penalty
                    else:
                        profit += order.profit - order.tardiness_fee
                else:
                    profit += order.profit
            prev_job = job
        return profit

class UnfulfilledOrders(Objective):

    def __init__(self):
        super().__init__('Unfulfilled Order Count')

    def evaluate(self, schedule : Schedule, production_environment : ProductionEnvironment, jobs : list[Job] = []) -> float:
        unfulfilled_order_count = 0
        prev_job = jobs[0]
        for job in jobs[1:]:
            if job.order != prev_job.order or job.recipe != prev_job.recipe or job == jobs[-1]:
                # check prev job end_time
                order : Order = prev_job.order
                if schedule._get_assignment_for_job(prev_job).end_time > order.latest_acceptable_time:
                    unfulfilled_order_count += 1
        return unfulfilled_order_count
    
"""
    Add additional feasibility constraints below
"""