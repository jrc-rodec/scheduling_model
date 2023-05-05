from solver import Solver
from model import ProductionEnvironment, Schedule
from translation import Encoder

class TimeWindowSequenceGA(Solver):

    def __init__(self, production_environment : ProductionEnvironment, encoder : Encoder = None):
        super().__init__('Time Window Sequence GA', production_environment, encoder)

        self.max_generations = 0
        self.max_function_evaluations = 0

    def initialize(self):
        self.jobs = []
        pass

    def mutate(self, individual):
        p = 1 / len(individual)
        # mutate workstation assignments
        for i in range(0, len(individual), 3):
            pass
        # mutate sequence order
        for i in range(1, len(individual), 3):
            pass
        # if time windows enabled, mutate time window size
        if self.mutate_duration:
            for i in range(2, len(individual), 3):
                pass
        pass

    def recombine(self):
        pass

    def repair(self):
        pass

    def select(self):
        pass

    def evaluate(self, solution : list[int]):
        if solution in self.memory:
            self.memory_access += 1
            return self.memory[solution][0] # NOTE: just use the first values for now
        feasible = False # TODO
        if not feasible:
            return float('inf')
        schedule : Schedule = self.encoder.decode(solution, self.jobs, self.production_environment, [], self)
        result = self.evaluator.evaluate(schedule, self.jobs)
        self.memory[solution] = result
        self.function_evaluations += 1
        return result[0] # NOTE: just using the first value for now

    def evaluate_population(self, population) -> list[float]:
        population_fitness = []
        for i in range(len(population)):
            population_fitness.append(self.evaluate(population[i]))
        return population_fitness

    def create_population(self) -> list[list[int]]:
        pass

    def should_stop(self) -> bool:
        if self.max_generations > 0 and self.generation >= self.max_generations:
            return True
        if self.max_function_evaluations > 0 and self.function_evaluations >= self.max_function_evaluations:
            return True
        return False

    def run(self, population_size : int = 25, offspring_amount : int = 50):
        self.memory : dict(list[int], list[int]) = []
        self.history = {"best": [], "average": []}
        self.function_evaluations = 0
        self.memory_access = 0
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        self.population : list[list[int]] = self.create_population()
        self.population_fitness = self.evaluate_population(self.population)
        self.generation = 0
        if self.max_generations == 0 and self.max_function_evaluations == 0:
            print('No stopping criteria set, abort')
            return False
        while not self.should_stop():
            #create offsprings
            offsprings : list[list[int]] = []
            for _ in range(len(self.offspring_amount)):
                offsprings.append(self.recombine())
            #mutate offsprings
            for offspring in offsprings:
                self.mutate(offspring)
            #evaluate offsprings
            offspring_fitness : list[float] = self.evaluate_population(offsprings)
            #select new population
            pass