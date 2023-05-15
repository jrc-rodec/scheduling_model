from solver import Solver
from model import ProductionEnvironment, Schedule
from translation import Encoder
import random

class TimeWindowSequenceGA(Solver):

    def __init__(self, production_environment : ProductionEnvironment, encoder : Encoder = None):
        super().__init__('Time Window Sequence GA', production_environment, encoder)

        self.max_generations = 0
        self.max_function_evaluations = 0

    def initialize(self):
        self.jobs = []
        pass

    def mutate(self, individual):
        p = 1 / len(individual) # maybe check whether or not genes should be kept complete
        # mutate workstation assignments
        for i in range(0, len(individual), 4):
            if random.random() < p:
                workstations = self.production_environment.get_available_workstations_for_task(self.jobs[int(i/4)])
                individual[i] = int(random.choice(workstations).id)
            
        # mutate sequence order
        for i in range(1, len(individual), 4):
            if random.random() < p:
                workstation = individual[i-1]
                indices = []
                for j in range(0, len(individual), 4):
                    if individual[j] == workstation and j != i-1:
                        indices.append(j+1)
                if len(indices) > 0:
                    swap = random.choice(indices)
                    temp = individual[i]
                    individual[i] = individual[swap]
                    individual[swap] = temp

        if self.mutate_worker:
            pass # TODO
        # if time windows enabled, mutate time window size
        if self.mutate_duration:
            for i in range(2, len(individual), 4):
                pass # TODO

    def one_point_crossover(self, parent_a, parent_b):
        crossover_point = random.randint(0, len(parent_a)-2)
        offspring = []
        offspring.extend(parent_a[:crossover_point])
        offspring.extend(parent_b[crossover_point+1:])
        self.repair(offspring)
        return offspring

    def uniform_crossover(self, parent_a, parent_b):
        selection_values = [0 if random.random() < 0.5 else 1 for _ in range(len(parent_a))]
        offspring = []
        for i in range(len(selection_values)):
            offspring.append(parent_a[i] if selection_values[i] == 1 else parent_b[i])
        # repair
        for i in range(0, len(offspring), 4):
            workstation = offspring[i]
            conflicts_found = True
            while conflicts_found:
                conflicts_found = False
                for j in range(0, len(offspring), 4):
                    if i != j and offspring[j] == workstation:
                        # check if sequence has a conflict
                        if offspring[i+1] == offspring[j+1]:
                            conflicts_found = True
                            if (selection_values[i+1] == 1 and selection_values[j+1] == 1) or (selection_values[i+1] == 0 and selection_values[j+1] == 0):
                                if random.random() < 0.5:
                                    offspring[j+1] += 1
                                else:
                                    offspring[i+1] += 1
                            elif selection_values[i+1] == 1:
                                offspring[j+1] += 1
                            else:
                                offspring[i+1] += 1
        return offspring

    def recombine(self):
        # for testing, just single point crossover
        parent_a = self.select()
        parent_b = self.select()
        while parent_a == parent_b:
            parent_b = self.select() # NOTE: maybe needs changing
        offspring = self.one_point_crossover(parent_a, parent_b)
        return offspring

    def repair(self, offspring):
        for i in range(0, len(offspring), 4):
            workstation = offspring[i]
            conflicts_found = True
            while conflicts_found:
                conflicts_found = False
                for j in range(0, len(offspring), 4):
                    if i != j and offspring[j] == workstation:
                        # check if sequence has a conflict
                        if offspring[i+1] == offspring[j+1]:
                            conflicts_found = True
                            if random.random() < 0.5:
                                offspring[j+1] += 1
                            else:
                                offspring[i+1] += 1
        return offspring

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
                offspring = self.recombine()
                #self.repair(offspring) # done at the end of recombination instead
                offsprings.append(offspring)
            #mutate offsprings
            for offspring in offsprings:
                self.mutate(offspring)
            #evaluate offsprings
            offspring_fitness : list[float] = self.evaluate_population(offsprings)
            #select new population
            pass