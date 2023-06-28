# outer solver: combinatorial optimization - Workstation Assignment, (Worker Assignment), (Resource Constraints)
# FF: makespan (determined by inner solver), robust makespan (uncertainty simulation), load balancing (proportional to breakdown probability)
# ex.: GA, Tabu Search, Harmony Search
# NOTE: since every solution triggers an additional optimization, small population size + few iterations are necessary

# inner solver: integer optimization - Starting Sequence, (Time Window Size)
# FF: makespan, robust makespan (uncertainty simulation)
# either: starting sequence ordering
# ex.: GA, Gurobi
# or: combinatorial change of order
# ex.: GA
# or: dispatching policy
# NOTE: not integer optimization
# ex.: PSO, CMA-ES
# or: use starting time directly
# ex.: PSO, GA, Gurobi

import random

class OuterHarmonySearch:

    pass

class OuterTabuSearch:

    pass

class OuterGA:

    def __init__(self, workstation_options : list[list[int]], orders : list[int]):
        #[0] -> [0, 1, 2]
        #[1] -> [2, 3]
        #...
        self.workstation_options = workstation_options
        self.orders = orders
        self.results : dict[list[int], tuple[list[int|float], list[float]]] = dict()

    def recombine(self, parent_a : list[int], parent_b : list[int]):
        # uniform crossover
        child : list[int] = [0] * len(parent_a)
        for i in range(len(parent_a)):
            if random.random() < 0.5:
                child[i] = parent_a[i]
            else:
                child[i] = parent_b[i]
        return child

    def mutate(self, individual : list[int]) -> None:
        p = 1 / len(individual)
        for i in range(len(individual)):
            if random.random() < p and len(self.workstation_options[i]) > 1:
                current = individual[i]
                while current == individual[i]:
                    individual[i] = random.choice(self.workstation_options[i])

    def select(self, population : list[list[int]], population_fitness : list[list[float]]) -> list[int]:
        fitness_sum = 0
        for fitness in population_fitness:
            fitness_sum += fitness[0] # NOTE: only use first
        probabilities = [0.0] * len(population_fitness)
        previous_probability = 0.0
        for i in range(len(probabilities)):
            probabilities[i] = previous_probability + (population_fitness[i][0] / fitness_sum)
            previous_probability = probabilities[i]
        n = random.random()
        for i in range(len(probabilities)):
            if n < probabilities[i]:
                return population[i]
        return population[-1]

    def evaluate(self, individual : list[int]) -> list[float]:
        if self.results.get(individual):
            return self.results[individual][1] # fitness
        inner_ga = InnerGA(individual, self.orders)
        result, fitness = inner_ga.run()
        self.results[individual] = (result, fitness)
        return fitness

    def create_individual(self, n_genes : int) -> list[int]:
        individual : list[int] = [0] * n_genes
        for j in range(len(individual)):
            individual[j] = random.choice(self.workstation_options[j])
        return individual

    def create_population(self, population_size : int, n_genes : int) -> list[list[int]]:
        # random for now
        population : list[list[int]] = []
        for i in range(population_size):
            individual = self.create_individual(n_genes)
            population.append(individual)
        return population

    def run(self, n_genes : int, population_size : int, offspring_amount : int, generations : int, require_unique_population : bool = False, allow_duplicate_parents : bool = False, elitism : bool = False) -> tuple[list[int], list[float]]:
        population : list[list[int]] = self.create_population(population_size, n_genes)
        population_fitness : list[list[float]] = [[float('inf')]] * population_size
        self.best : list[int] = []
        self.best_fitness : list[float] = [float('inf')]
        for i in range(len(population)):
            fitness : list[float] = self.evaluate(population[i])
            population_fitness[i] = fitness
            if fitness[0] < self.best_fitness[0]:
                self.best = population[i]
                self.best_fitness = fitness
        for generation in range(generations):
            # create offsprings
            if generation%(generations/10) == 0:
                print(f'{generation} generations done.')
            offsprings : list[list[int]] = []
            offsprings_fitness : list[list[float]] = []
            for i in range(offspring_amount):
                parent_a = self.select(population, population_fitness)
                parent_b = self.select(population, population_fitness)
                while not allow_duplicate_parents and parent_a == parent_b:
                    parent_b = self.select(population, population_fitness)
                # recombine
                offspring = self.recombine(parent_a, parent_b)
                # mutate
                self.mutate(offspring)
                offsprings.append(offspring)
                # evaluate offsprings
                offspring_fitness : list[float] = self.evaluate(offspring)
                offsprings_fitness.append(offspring_fitness)
            # select new population
            selection_pool : list[tuple[list[int], list[float]]] = []
            selection_pool.extend(zip(offsprings, offspring_fitness))
            if elitism:
                selection_pool.extend(zip(population, population_fitness))
            selection_pool.sort(key=lambda x: x[1][0]) # NOTE: only uses first value in fitness of each individual for now, single objective
            if selection_pool[0][1][0] < self.best_fitness[0]:
                self.best = selection_pool[0][0]
                self.best_fitness = selection_pool[0][1]
            population = []
            population_fitness = []
            for i in range(population_size):
                if not require_unique_population or selection_pool[i][0] not in population:
                    population.append(selection_pool[i][0])
                    population_fitness.append(selection_pool[i][1])
                else:
                    individual = self.create_individual(n_genes)
                    population.append(individual)
                    individual_fitness = self.evaluate(individual)
                    population_fitness.append(individual_fitness)
        return population[0], population_fitness[0]
    
class InnerGA:

    def __init__(self, workstation_assignments : list[int], orders : list[int]):
        # workstation_assignemnts : solution of the outer solver, contains all assignments of the jobs to the workstations
        # orders : ex. [0, 0, 1, 1, 1, 2, 2] contains the order id for each job to check the order sequences
        self.workstations = workstation_assignments
        self.orders = orders
    
    def run(self, population_size : int, offspring_amount : int, generations : int):
        population = []
        population_fitness = []
        # ...

class InnerCMAES:
    
        pass

class InnerPSO:
    
        pass

class InnerAISA:
    
        pass

class InnerGurobi:
    
        pass


"""offsprings = ['a', 'b', 'c']
offspring_fitness = [2, 1, 3]
selection_pool : list[tuple[list[int], list[float]]] = []
selection_pool.extend(zip(offsprings, offspring_fitness))
print(selection_pool)
selection_pool.sort(key=lambda x: x[1])
print(selection_pool)
population = []
population_fitness = []
for i in range(len(offsprings)):
    population.append(selection_pool[i][0])
    population_fitness.append(selection_pool[i][1])
print(population)
print(population_fitness)"""

"""ones = 0
zeros = 0
for i in range(100):
    values = [1 if random.random() < 0.5 else 0 for _ in range(10)]
    ones += values.count(1) / 10
    zeros += values.count(0) / 10
print(ones)
print(zeros)"""

"""population_fitness = [10, 100, 5, 20, 30]
fitness_sum = 0
for fitness in population_fitness:
    fitness_sum += fitness # NOTE: only use first
probabilities = [0.0] * len(population_fitness)
previous_probability = 0.0
for i in range(len(probabilities)):
    probabilities[i] = previous_probability + (population_fitness[i] / fitness_sum)
    previous_probability = probabilities[i]
n = random.random()
print(probabilities)
print(n)
for i in range(len(probabilities)):
    if n < probabilities[i]:
        print(f'SELECTED: {population_fitness[i]}')
        break"""
