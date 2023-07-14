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

    def __init__(self, workstation_options : list[list[int]], orders : list[int], durations : list[list[int]]):
        #[0] -> [0, 1, 2]
        #[1] -> [2, 3]
        #...
        self.workstation_options = workstation_options
        self.orders = orders
        self.durations = durations
        self.results : dict[list[int], tuple[list[int], list[float]]] = dict()

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
            fitness_sum += fitness # NOTE: only use first
        probabilities = [0.0] * len(population_fitness)
        previous_probability = 0.0
        for i in range(len(probabilities)):
            probabilities[i] = previous_probability + (population_fitness[i] / fitness_sum)
            previous_probability = probabilities[i]
        n = random.random()
        for i in range(len(probabilities)):
            if n < probabilities[i]:
                return population[i]
        return population[-1]

    def evaluate(self, individual : list[int]) -> list[float]:
        if self.results.get(str(individual)):
            return self.results[str(individual)][1] # fitness
        inner_ga = InnerGA(individual, self.orders, self.durations) # durations could get fixed at this point
        result, fitness = inner_ga.run()
        self.results[str(individual)] = (result, fitness)
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
        self.best_fitness : list[float] = float('inf')#[float('inf')]
        for i in range(len(population)):
            fitness : list[float] = self.evaluate(population[i])
            population_fitness[i] = fitness
            if fitness < self.best_fitness:
                self.best = population[i]
                self.best_fitness = fitness
        for generation in range(generations):
            # create offsprings
            if generation%(generations/10) == 0 or True:
                print(f'{generation} generations done. Current Best: {self.best_fitness}')
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
            selection_pool.extend(zip(offsprings, offsprings_fitness))
            if elitism:
                selection_pool.extend(zip(population, population_fitness))
            selection_pool.sort(key=lambda x: x[1]) # NOTE: only uses first value in fitness of each individual for now, single objective
            if selection_pool[0][1] < self.best_fitness:
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
        return population[0], self.results[str(population[0])][0], population_fitness[0]
    
class InnerGA:

    def __init__(self, workstation_assignments : list[int], orders : list[int], durations : list[list[int]]):
        # workstation_assignemnts : solution of the outer solver, contains all assignments of the jobs to the workstations
        # orders : ex. [0, 0, 1, 1, 1, 2, 2] contains the order id for each job to check the order sequences
        self.workstations = workstation_assignments
        self.job_operations = orders
        self.durations = durations
        self.jobs = []
        for job in self.job_operations:
            if job not in self.jobs:
                self.jobs.append(job)
    
    def select(self, population, population_fitness) -> list[int]:
        if self.tournament_size == 0:
            self.tournament_size = int(len(population) / 10)
        participants = random.choices(range(0, len(population)), k=self.tournament_size)
        winner = sorted(participants, key=lambda x: population_fitness[x])[0]
        return population[winner]

    def recombine(self, parent_a, parent_b) -> tuple[list[int], list[int]]:
        split = [0 if random.random() < 0.5 else 1 for _ in range(len(self.jobs))]
        set_a = []
        set_b = []
        for i in range(len(self.jobs)):
            if split[i] == 0:
                set_a.append(self.jobs[i])
            else:
                set_b.append(self.jobs[i])
        offspring_a = [-1] * len(parent_a)
        offspring_b = [-1] * len(parent_b)
        a_index = 0
        b_index = 0
        a_values = [x for x in parent_a if x in set_a]
        b_values = [x for x in parent_b if x in set_b]
        for i in range(len(parent_a)):
            if parent_a[i] in set_a:
                offspring_a[i] = parent_a[i]
            else:
                offspring_a[i] = b_values[b_index]
                b_index += 1
            if parent_b[i] in set_b:
                offspring_b[i] = parent_b[i]
            else:
                offspring_b[i] = a_values[a_index]
                a_index += 1
        return offspring_a, offspring_b

    def mutate(self, individual):
        p = 1 / len(individual)
        for i in range(len(individual)):
            if random.random() < p:
                swap = random.choice([x for x in range(len(individual)) if x != i])
                tmp = individual[swap]
                individual[swap] = individual[i]
                individual[i] = tmp
    
    def evaluate(self, individual) -> float:
        next_operations = [0] * len(self.jobs)
        end_on_workstations = [0] * len(self.durations[0]) # amount of workstations
        end_times = [-1] * len(self.job_operations)
        # only needed if gap filling is used, currently not implemented for inner solver
        """gaps_on_workstations : list[list[tuple[int, int]]] = []
        for i in range(len(end_on_workstations)):
            gaps_on_workstations.append([])"""
        for i in range(len(individual)):
            job = individual[i]
            operation = next_operations[job]
            start_index = 0
            for j in range(len(self.job_operations)):
                if self.job_operations[j] == job:
                    start_index = j
                    break
                start_index = j
            start_index += operation
            next_operations[job] += 1
            workstation = self.workstations[start_index]
            duration = self.durations[start_index][workstation]
            offset = 0
            if operation > 0:
                offset = max(0, end_times[start_index-1] - end_on_workstations[workstation])
            end_times[start_index] = end_on_workstations[workstation]+duration+offset
            end_on_workstations[workstation] = end_times[start_index]
        return max(end_times)

    def run(self, population_size : int = 50, offspring_amount : int = 100, generations : int = 100, tournament_size : int = 5, elitism : int = 1):
        self.tournament_size = tournament_size
        population : list[list[int]] = []
        population_fitness : list[float] = []
        overall_best = []
        overall_best_fitness = float('inf')
        for _ in range(population_size):
            individual = self.job_operations.copy()
            random.shuffle(individual)
            fitness = self.evaluate(individual)
            population.append(individual)
            population_fitness.append(fitness)
        best = sorted([i for i in range(len(population_fitness))], key=lambda x: population_fitness[x])[0]
        overall_best = population[best]
        overall_best_fitness = population_fitness[best]
        for generation in range(generations):
            offsprings : list[list[int]] = []
            offspring_fitness : list[float] = []
            while len(offsprings) < offspring_amount:
                parent_a = self.select(population, population_fitness)
                parent_b = self.select(population, population_fitness)
                while (parent_a == parent_b):
                    parent_b = self.select(population, population_fitness)
                offspring_a, offspring_b = self.recombine(parent_a, parent_b)
                offsprings.append(offspring_a)
                fitness = self.evaluate(offspring_a)
                if fitness < overall_best_fitness:
                    overall_best_fitness = fitness
                    overall_best = offspring_a
                offspring_fitness.append(fitness)
                if len(offsprings) < offspring_amount:
                    offsprings.append(offspring_b)
                    fitness = self.evaluate(offspring_b)
                    if fitness < overall_best_fitness:
                        overall_best_fitness = fitness
                        overall_best = offspring_b
                    offspring_fitness.append(fitness)
            selection_pool = offsprings
            selection_pool_fitness = offspring_fitness
            if elitism > 0:
                sorted_indices = sorted([j for j in range(len(population_fitness))], key=lambda x: population_fitness[x])
                for j in range(elitism):
                    selection_pool.append(population[sorted_indices[j]])
                    selection_pool_fitness.append(population_fitness[sorted_indices[j]])
            sorted_selection_indices = sorted([j for j in range(len(selection_pool_fitness))], key=lambda x: selection_pool_fitness[x])
            population = []
            population_fitness = []
            for j in range(population_size):
                population.append(selection_pool[sorted_selection_indices[j]])
                population_fitness.append(selection_pool_fitness[sorted_selection_indices[j]])
        
        return overall_best, overall_best_fitness


class InnerCMAES:
    
        pass

class InnerPSO:
    
        pass

class InnerAISA:
    
        pass

class InnerGurobi:
    
        pass

from translation import SequenceGAEncoder, FJSSPInstancesTranslator
from evaluation import Makespan
from visualization import visualize_schedule
from model import Order, ProductionEnvironment
def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders


encoder = SequenceGAEncoder()
source = '6_Fattahi'
instance = 20 # 20 -> aim for < 1276
production_environment = FJSSPInstancesTranslator().translate(source, instance)
orders = generate_one_order_per_recipe(production_environment)
production_environment.orders = orders
workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)

ga = OuterGA(workstations_per_operation, job_operations, base_durations)
workstations, sequence, fitness = ga.run(len(job_operations), 50, 100, 25, elitism=True)

print(workstations)
print(sequence)
print(fitness)

durations = []
for i in range(len(job_operations)):
    durations.append(base_durations[i][workstations[i]])
schedule = encoder.decode(sequence, workstations, [], durations, job_operations, production_environment, False)

visualize_schedule(schedule, production_environment, orders)

"""import matplotlib.pyplot as plt
best_history = history[0]
generation_history = history[1]
average_history = history[2]
labels = ['Overall Best', 'Generation Best', 'Average']

if adjust_parameters:
    fig, axs = plt.subplots(2)
else:
    fig, ax = plt.subplots(1)
    axs = [ax]

axs[0].set_title('Fitness History')
axs[0].plot(best_history)
axs[0].plot(generation_history, c='g', linewidth=0.1)
axs[0].plot(average_history, c='r', linewidth=0.1)
axs[0].legend(labels)

if adjust_parameters:
    p_history = history[3]
    axs[1].set_title('Mutation Probability History')
    axs[1].plot(p_history, c='m', linewidth=1.0)
    axs[1].legend(['Mutation Probability'])
plt.show()"""

from visualization import visualizer_for_schedule
visualizer_for_schedule(schedule, job_operations)