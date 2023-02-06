from models import Order, SimulationEnvironment, Workstation
from solver import Solver # NOTE: needs new type of solvers
import random
import copy 

class Event:
    
    def __init__(self, time_interval : int = 1):
        self.time_interval = time_interval
    #TODO: add schedule as parameter to both is_triggered and process
    def is_triggered(self, schedule : dict[int, tuple[int, int, int]], timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order]) -> bool:
        pass

    def process(self, schedule : dict[int, tuple[int, int, int]], timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order], new_orders : list[Order]) -> None:
        pass


class NewOrderEvent(Event):

    def __init__(self, time_interval : int = 1, trigger_probability : float = 0.1, earliest_possible_timeslot : int = 0, last_possible_timeslot : int = 1000) -> None:
        super().__init__(time_interval)
        self.trigger_probability = trigger_probability
        self.earliest_possible_timeslot = earliest_possible_timeslot
        self.last_possible_timeslot = last_possible_timeslot

    def is_triggered(self, schedule : dict[int, tuple[int, int, int]], timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order]) -> bool:
        return timestamp % self.time_interval == 0 and random.uniform(0.0, 1.0) < self.trigger_probability

    def process(self, schedule : dict[int, tuple[int, int, int]], timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order], new_orders : list[Order]) -> None:
        order = random.choice(available_orders)
        # TODO: maybe modify delivery date, etc., or even change available orders to available recipes and randomize other parameters
        new_order : Order = copy.deepcopy(order)
        new_order.arrival_time = timestamp
        new_order.delivery_time = random.randint(int(timestamp * 1.2), self.last_possible_timeslot)
        new_order.latest_acceptable_time = self.last_possible_timeslot
        new_orders.append(new_order)

class DeactivateWorkstationEvent(Event):

    def __init__(self, schedule : dict[int, tuple[int, int, int]], time_interval : int = 1, trigger_probability : float = 0.1, earliest_possible_timeslot : int = 0, last_possible_timeslot : int = 1000) -> None:
        super().__init__(time_interval)
        self.trigger_probability = trigger_probability
        self.earliest_possible_timeslot = earliest_possible_timeslot
        self.last_possible_timeslot = last_possible_timeslot
        self.deactivated_workstations : list[tuple[Workstation, int]] = []

    def reactivate_workstations(self, timestamp: int, simulation_environment : SimulationEnvironment) -> None:
        reactivated_workstations = []
        for deactivated_workstation in self.deactivated_workstations:
            if deactivated_workstation[1] <= timestamp:
                # reactivate workstation
                simulation_environment.workstations.append(deactivated_workstation[0])
                reactivated_workstations.append(deactivated_workstation)
        simulation_environment.workstations.sort(key = lambda x: x.id) # bring workstations back into order in case any algorithm relies on the workstations being sorted for indexing
        for reactivated_workstation in reactivated_workstations:
            self.deactivated_workstations.remove(reactivated_workstation)

    def is_triggered(self, schedule : dict[int, tuple[int, int, int]], timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order]) -> bool:
        # check if any previously deactivated workstation can be reactivated
        self.reactivate_workstations(timestamp, simulation_environment)
        return timestamp % self.time_interval == 0 and random.uniform(0,0, 1.0) < self.trigger_probability

    def process(self, schedule : dict[int, tuple[int, int, int]], timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order], new_orders : list[Order]) -> None:
        deactivate_until_timestamp : int = random.randint(int(timestamp * 1.2), self.last_possible_timeslot)
        deactivated_workstation = random.choice(simulation_environment.workstations)
        self.deactivated_workstations.append((deactivated_workstation, deactivate_until_timestamp))
        simulation_environment.workstations.remove(deactivated_workstation) # TODO: removing workstations from the environment is not ideal - add blocking dummy order to the schedule for the time instead
        # TODO: re-add all orders currently scheduled (not finished) for the workstation as new orders to be redistributed to the other workstations
        # find scheduled orders
        # check for already finished tasks
        # add missing tasks to unscheduled orders

class Simulation:

    def __init__(self, available_orders : list[Order], simulation_environment : SimulationEnvironment, solver : Solver) -> None:
        self.current_time : int = 0
        self.environment : SimulationEnvironment = simulation_environment
        self.available_orders : list[Order] = available_orders
        self.solver = solver
        self.schedule : dict[int, tuple[int, int, int]] = None # dict -> <workstation, (task_id, start_time, order_id)
        self.possible_events : list[Event] = list()

    def configure(self, end_time : int, step_size : int = 1) -> None:
        self.end_time : int = end_time
        self.step_size = step_size

    def register_event(self, event : Event) -> None:
        self.possible_events.append(event)

    def check_events(self) -> list[Event]:
        triggered_events : list[Event] = []
        for possible_event in self.possible_events:
            if possible_event.is_triggered(self.current_time, self.environment, self.available_orders):
                triggered_events.append(possible_event)
        return triggered_events

    def is_finished(self) -> bool:
        return self.current_time > self.end_time

    def step(self) -> None:
        if not self.is_finished():
            events = self.check_events()
            new_orders : list[Order] = []
            for event in events: # add new orders, deactivate some workstations, remove some resources, ...
                if event.is_triggered(self.current_time, self.environment, self.available_orders):
                    event.process(self.current_time, self.environment, self.available_orders, new_orders)
            for order in new_orders: # schedule newly created orders, if any of the events created new orders
                self.solver.schedule(order, self.schedule, self.environment, self.current_time)
            self.current_time += self.step_size

    def run(self) -> None:
        while not self.is_finished():
            self.step()
        print('Done')