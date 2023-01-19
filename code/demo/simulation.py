from models import Order, SimulationEnvironment
from solver import Solver # NOTE: needs new type of solvers

class Event:

    def is_triggered(self, timestamp : int, simulation_environment : SimulationEnvironment, available_orders : list[Order]) -> bool:
        pass

    def process(self, timestamp : int, simualtion_environment : SimulationEnvironment, available_orders : list[Order], new_orders : list[Order]) -> None:
        pass

class Simulation:

    def __init__(self, available_orders : list[Order], simulation_environment : SimulationEnvironment, solver : Solver) -> None:
        self.current_time : int = 0
        self.environment : SimulationEnvironment = simulation_environment
        self.available_orders : list[Order] = available_orders
        self.solver = solver
        self.schedule = None
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
                event.process(self.current_time, self.environment, self.available_orders, new_orders)
            for order in new_orders: # schedule newly created orders, if any of the events created new orders
                self.solver.schedule(order, self.schedule, self.environment, self.current_time)
            self.current_time += self.step_size

    def run(self) -> None:
        while not self.is_finished():
            self.step()
        print('Done')