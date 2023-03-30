from model import ProductionEnvironment, Job, Order
from copy import deepcopy
import random

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

    def initialize_population(self) -> list[list[int]]: # TODO
        pass

    def _is_feasible(self, individual : list[int]) -> bool: # TODO
        pass

    def _evaluate(self, individual : list[int]) -> list[float]: # TODO
        pass

    def _evaluate_population(self, population : list[list[int]]) -> list[list[float]]:
        population_fitness : list[list[float]] = []
        for individual in population:
            objective_values = self._evaluate(individual)
            population_fitness.append(objective_values)
        return population_fitness

    def _get_weighted_probabilities(self, population : list[list[int]], population_fitness : list[list[float]]) -> list[float]:
        probabilities : list[float] = []
        sum = 0
        for fitness in population_fitness:
            sum += fitness[0] #NOTE/TODO: only one objective value for now
        population = []
        previous_probability = 0.0
        while len(population) < self.population_size:
            for i in range(len(population)):
                probability = previous_probability + (fitness[i] / sum)
                probabilities.append(probability)
                previous_probability = probability
        return probabilities

    def _roulette_wheel_selection(self, population : list[list[int]], population_fitness : list[list[float]]):
        r = random.random()
        probabilities = self._get_weighted_probabilities(population, population_fitness)
        for i in range(len(probabilities)):
            if r < probabilities[i]:
                return population[i]
        return population[-1]

    def _select_parents(self, population : list[list[int]], population_fitness : list[list[float]]) -> tuple[list[int], list[int]]:
        parent_a = self._roulette_wheel_selection(population, population_fitness)
        parent_b = []
        while parent_a == parent_b: # force 2 different parents
            parent_b = self._roulette_wheel_selection(population, population_fitness)
        return parent_a, parent_b

    def _mutate(self, individual : list[int]) -> list[int]: # TODO
        pass

    def _recombine(self, parent_a : list[int], parent_b : list[int]) -> tuple[list[int], list[int]]:
        crossover_point_a = random.randint(0, len(parent_a) - 2)
        crossover_point_b = random.randint(crossover_point_a + 1, len(parent_a) - 1)
        offspring_a = []
        offspring_b = []
        for i in range(crossover_point_a):
            offspring_a.append(parent_a[i])
            offspring_b.append(parent_b[i])
        for i in range(crossover_point_a + 1, crossover_point_b):
            offspring_a.append(parent_b[i])
            offspring_b.append(parent_a[i])
        for i in range(crossover_point_b + 1, len(parent_a)):
            offspring_a.append(parent_a[i])
            offspring_b.append(parent_b[i])
        return deepcopy(offspring_a), deepcopy(offspring_b)
    
    def get_best(self, population : list[list[int]], population_fitness : list[list[float]]):
        best : tuple[list[list[int]], list[list[float]]] = population[0]
        for i in range(1, len(population_fitness)):
            if population_fitness[i][0] < best[1][0]:
                best = (population[i], population_fitness[i])
        return deepcopy(best)


    def solve(self, jobs : list[Job]):
        self.jobs = jobs
        population : list[list[int]] = self.initialize_population()
        population_fitness : list[list[float]] = self._evaluate_population(population)
        offsprings : list[list[int]] = []
        offspring_fitness : list[list[float]] = []
        best : tuple[list[int], list[float]] = self.get_best(population, population_fitness)
        
        for generation in range(self.max_generations):
            offsprings.clear()
            offspring_fitness.clear()

            # recombine
            while len(offsprings < self.offspring_amount):
                parent_a, parent_b = self._select_parents(population, population_fitness)
                offspring_a, offspring_b = self._recombine(parent_a, parent_b)
                # mutate
                self._mutate(offspring_a)
                offsprings.append(offspring_a)
                if len(offsprings) + 1 <= self.offspring_amount:
                    self._mutate(offspring_b)
                    offsprings.append(offspring_b)

            # evaluate offsprings
            offspring_fitness = self._evaluate_population(offsprings)
            
            best_offspring = self.get_best(offsprings, offspring_fitness)
            if best_offspring[1][0] < best[1][0]:
                best = best_offspring

            # select next generation
            if self.elitism:
                offsprings.extend(population)
                offspring_fitness.extend(population_fitness)
            
            population.clear()
            population_fitness.clear()

            while len(population) < self.population_size:
                individual : list[int] = self._roulette_wheel_selection(offsprings, offspring_fitness)
                idx = offsprings.index(individual)
                population.append(individual)
                population_fitness.append(offspring_fitness[idx])
                offsprings.pop(idx)
                offspring_fitness.pop(idx)
        return best
