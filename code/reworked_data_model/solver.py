from model import ProductionEnvironment, Job, Order
from copy import deepcopy

class Solver:
    pass

class TimeWindowGASolver(Solver):

    def __init__(self, production_environment : ProductionEnvironment, orders : list[Order]) -> None:
        self.production_environment = production_environment
        self.orders = orders
        self.name = 'Time Window GA'

    def configure(self, encoding : list[int], population_size : int = 25, offspring_amount : int = 50, elitism : bool = False, mutation_probability : float = None, max_generations : int = 100, first_time_slot : int = 0, last_time_slot : int = 1000) -> None:
        self.max_generations = max_generations
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        self.elitism = elitism
        self.first_time_slot = first_time_slot
        self.last_time_slot = last_time_slot
        if not mutation_probability:
            mutation_probability = 1 / len(encoding)
        self.mutation_probability = mutation_probability

    def initialize_population(self) -> list[list[int]]:
        pass

    def _is_feasible(self, individual : list[int]) -> bool:
        pass

    def _evaluate(self, individual : list[int]) -> list[float]:
        pass

    def _select_parents(self, population : list[list[int]]) -> tuple[list[int], list[int]]:
        pass

    def _mutate(self, individual : list[int]) -> list[int]:
        pass

    def _recombine(self, parent_a : list[int], parent_b : list[int]) -> tuple[list[int], list[int]]:
        pass

    def solve(self, jobs : list[Job]):
        self.jobs = jobs
        population : list[list[int]] = self.initialize_population()
        offsprings : list[list[int]] = []
        for generation in range(self.max_generations):
            pass
        pass
