import random
from copy import deepcopy

class GeneticAlgorithm:
    
    def __init__(self, dimensions : int = 10, lower_bounds : list[int] = [], upper_bounds : list[int] = [], population_size : int = 25, offspring_amount : int = 50, elitism : bool = False, mutation_probability : float = None, max_generations : int = 100) -> None:
        self.max_generations = max_generations
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        self.dimensions = dimensions
        self.elitism = elitism
        if not mutation_probability:
            mutation_probability = 1 / dimensions
        self.mutation_probability = mutation_probability
        self.lower_bounds = lower_bounds
        self.upper_bounds = upper_bounds
        self.max_mutation = 50

    def initialize_population(self) -> list[list[int]]:
        population : list[list[int]] = []
        for i in range(self.population_size):
            population.append([])
            for j in range(self.dimensions):
                population[i].append(random.randint(self.lower_bounds[j], self.upper_bounds[j]+1))
        return population

    def _is_feasible(self, individual : list[int]) -> bool:
        return True

    def _evaluate(self, individual : list[int]) -> list[float]:
        sum = 0
        for value in individual:
            sum += value
        return sum

    def _evaluate_population(self, population : list[list[int]]) -> list[list[float]]:
        population_fitness : list[list[float]] = []
        for individual in population:
            objective_values = self._evaluate(individual)
            population_fitness.append(objective_values)
        return population_fitness

    def _select(self, population, probabilities):
        r = random.random()
        for i in range(len(probabilities)):
            if r < probabilities[i]:
                return population[i]
        return population[-1]
    
    def _select_next_generation(self, pool : list[list[int]], fitness) -> list[list[int]]:
        probabilities : list[float] = []
        sum = 0
        for f in fitness:
            sum += f
        population = []
        population_fitness = []
        previous_probability = 0.0
        while len(population) < self.population_size:
            for i in range(len(pool)):
                probability = previous_probability + (fitness[i] / sum)
                probabilities.append(probability)
                previous_probability = probability
            selection = self._select(pool, probabilities)
            probabilities.clear()
            population.append(selection)
            idx = pool.index(selection)
            population_fitness.append(fitness[idx])
            pool.pop(idx)
            fitness.pop(idx)
            """del pool[idx]
            del fitness[idx]"""
        return deepcopy(population), deepcopy(population_fitness)

    def _select_parents(self, population : list[list[int]], population_fitness : list[list[float]]) -> tuple[list[int], list[int]]:
        sum = 0
        for fitness in population_fitness:
            sum += fitness
        probabilities : list[float] = []
        previous_probability = 0.0
        for i in range(len(population)):
            probability = previous_probability + (population_fitness[i] / sum)
            probabilities.append(probability)
            previous_probability = probability
        return self._select(population, probabilities), self._select(population, probabilities) # just for testing

    def _mutate(self, individual : list[int]) -> None:
        for i in range(len(individual)):
            if random.random() < self.mutation_probability:
                individual[i] = random.randint(max(self.lower_bounds[i], individual[i] - self.max_mutation), min(self.upper_bounds[i]+1, individual[i] + self.max_mutation))

    def _recombine(self, parent_a : list[int], parent_b : list[int]) -> tuple[list[int], list[int]]:
        crossover_point_a = random.randint(0, len(parent_a)-1)
        #crossover_point_b = random.randint(crossover_point_a, len(parent_a))
        offspring_a : list[int] = []
        offspring_b : list[int] = []
        offspring_a = parent_a[:crossover_point_a]
        offspring_a.extend(parent_b[crossover_point_a:])
        offspring_b = parent_b[:crossover_point_a]
        offspring_b.extend(parent_a[crossover_point_a:])
        return offspring_a, offspring_b

    def solve(self):
        population : list[list[int]] = self.initialize_population()
        population_fitness : list[list[float]] = self._evaluate_population(population)
        offsprings : list[list[int]] = []
        offspring_fitness : list[list[float]] = []
        best = (population[0], population_fitness[0])
        best_fitness_history = []
        average_fitness_history = []
        for generation in range(self.max_generations):
            offsprings.clear()
            offspring_fitness.clear()
            best_fitness_history.append(best[1])
            average_fitness_of_generation = 0
            for fitness in population_fitness:
                average_fitness_of_generation += fitness
            average_fitness_history.append(average_fitness_of_generation / len(population))
            # recombine
            while len(offsprings) < self.offspring_amount:
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
            for i in range(len(offspring_fitness)):
                if offspring_fitness[i] < best[1]:
                    best = (offsprings[i], offspring_fitness[i])
            # select next generation
            if self.elitism:
                offsprings.extend(population)
                offspring_fitness.extend(population_fitness)
            population.clear()
            population_fitness.clear()
            # ...
            population, population_fitness = self._select_next_generation(offsprings, offspring_fitness)
            
        return best, best_fitness_history, average_fitness_history

dimensions = 10   
ga = GeneticAlgorithm(dimensions, [0] * dimensions, [10] * dimensions, 50, 100, False, 1/10, 1000)
result, best_fitness_history, average_fitness_history = ga.solve()
print(result)

import matplotlib.pyplot as plt

plt.plot(best_fitness_history)
plt.plot(average_fitness_history)
plt.show()
