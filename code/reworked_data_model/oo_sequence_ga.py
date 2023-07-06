import random

class Individual:
    
    required_operations :list[int] = []
    available_workstations : list[list[int]] = []
    available_workers : list[list[int]] = []
    base_durations : list[list[int]] = [] # NOTE: if 0, operation can't be processed on workstation

    def __init__(self, parent_a = None, parent_b = None, parent_split : list[int] = None):
        self.fitness = float('inf')
        self.workers = [0] * len(Individual.required_operations)
        if parent_a and parent_b:
            #crossover
            #sequence crossover
            jobs = []
            for x in Individual.required_operations:
                if x not in jobs:
                    jobs.append(x)
            set_a = [jobs[j] for j in range(len(jobs)) if parent_split[jobs[j]] == 0]
            set_b = [jobs[j] for j in range(len(jobs)) if parent_split[jobs[j]] == 1]
            b_index = 0
            parent_b_values = [x for x in parent_b.sequence if x in set_b]
            self.sequence = [-1] * len(parent_a.sequence)
            for i in range(0, len(parent_a.sequence)):
                if parent_a.sequence[i] in set_a:
                    self.sequence[i] = parent_a.sequence[i]
                else:
                    self.sequence[i] = parent_b_values[b_index]
                    b_index += 1
            #workstation crossover
            self.workstations : list[int] = []
            split = [0 if random.random() < 0.5 else 1 for _ in range(len(parent_a.workstations))]
            for i in range(len(parent_a.workstations)):
                self.workstations.append(parent_a.workstations[i] if split[i] == 0 else parent_b.workstations[i])
            #workers
            #durations, currently just base durations
            self.durations = []
            for i in range(len(self.workstations)):
                self.durations.append(Individual.base_durations[i][self.workstations[i]])
        elif parent_a or parent_b:
            #copy
            if parent_a:
                self.sequence = parent_a.sequence.copy()
                self.workstations = parent_a.workstations.copy()
                self.workers = parent_a.workers.copy()
                self.durations = parent_a.durations.copy()
                self.fitness = parent_a.fitness
            else:
                self.sequence = parent_b.sequence.copy()
                self.workstations = parent_b.workstations.copy()
                self.workers = parent_b.workers.copy()
                self.durations = parent_b.durations.copy()
                self.fitness = parent_b.fitness
        else:
            # randomize
            self.sequence : list[int] = []
            jobs = Individual.required_operations.copy()
            for _ in range(len(Individual.required_operations)):
                while len(jobs) > 0:
                    self.sequence.append(jobs.pop(random.randint(0, len(jobs)-1)))
            self.workstations : list[int] = []
            for i in range(len(self.sequence)):
                self.workstations.append(random.choice(Individual.available_workstations[i]))    
            self.workers : list[int] = [0] * len(self.sequence) # NOTE: not in use
            self.durations : list[int] = [] # NOTE: not in use
            for i in range(len(self.workstations)):
                self.durations.append(Individual.base_durations[i][self.workstations[i]])
    
    def mutate(self, p : float = None):
        if not p:
            p = 1 / (len(self.sequence) + len(self.workstations)) # NOTE: currently only these 2 lists are in use
        for i in range(len(self.sequence)):
            if random.random() < p:
                swap = random.choice([x for x in range(len(self.sequence)) if x != i])
                tmp = self.sequence[swap]
                self.sequence[swap] = self.sequence[i]
                self.sequence[i] = tmp
        for i in range(len(self.workstations)):
            if random.random() < p:
                if len(Individual.available_workstations[i]) > 1: # otherwise, can't mutate
                    self.workstations[i] = random.choice([x for x in self.available_workstations[i] if x != self.workstations[i]])
                    self.durations[i] = (Individual.base_durations[i][self.workstations[i]])
    
    def __str__(self):
        return f'Fitness: {self.fitness} | Sequence: {self.sequence} | Workstation Assignments: {self.workstations} | Workers: {self.workers} | Durations: {self.durations}'

class GA:

    def __init__(self, jobs : list[int], workstations_per_operation : list[list[int]], base_durations : list[list[int]]):
        Individual.required_operations = jobs # TODO
        Individual.available_workstations = workstations_per_operation
        Individual.base_durations = base_durations

    def recombine(self, parent_a : Individual, parent_b : Individual) -> tuple[Individual, Individual]:
        jobs = []
        for x in Individual.required_operations:
            if x not in jobs:
                jobs.append(x)
        split = [0 if random.random() < 0.5 else 1 for _ in range(len(jobs))]
        offspring_a = Individual(parent_a, parent_b, split)
        offspring_b = Individual(parent_b, parent_a, split)
        return offspring_a, offspring_b
    
    def roulette_wheel_selection(self, population):
        fitness_sum = 0
        for individual in population:
            fitness_sum += individual.fitness if individual.fitness != float('inf') else 100000 # NOTE: only use first
        probabilities = [0.0] * len(population)
        previous_probability = 0.0
        for i in range(len(probabilities)):
            probabilities[i] = previous_probability + (population[i].fitness / fitness_sum)
            previous_probability = probabilities[i]
        n = random.random()
        for i in range(len(probabilities)):
            if n < probabilities[i]:
                return population[i]
        return population[-1]
    
    def tournament_selection(self, population, tournament_size):
        # tournament selection
        if tournament_size == 0:
            tournament_size = int(len(population) / 10)
        participants = random.choices(range(0, len(population)), k=tournament_size)
        winner = sorted(participants, key=lambda x: population[x].fitness)[0]
        return population[winner]

    def evaluate(self, individual : Individual) -> None:
        jobs = []
        for x in Individual.required_operations:
            if x not in jobs:
                jobs.append(x)
        next_operations = [0] * len(jobs)
        end_on_workstations = [0] * len(Individual.base_durations[0])
        end_times = [-1] * len(Individual.required_operations)
        gaps_on_workstations :list[list[tuple[int, int]]]= []
        for i in range(len(Individual.base_durations[0])):
            gaps_on_workstations.append([])
        for i in range(len(individual.sequence)):
            job = individual.sequence[i]
            operation = next_operations[job]
            start_index = 0
            for j in range(len(Individual.required_operations)):
                if Individual.required_operations[j] == job:
                    start_index = j
                    break
                start_index = j
            start_index += operation
            next_operations[job] += 1
            workstation = individual.workstations[start_index]
            duration = individual.durations[start_index]
            offset = 0
            min_start_job = 0
            if operation > 0:
                # check end on prev workstation NOTE: if there is a previous operation of this job, start_index-1 should never be out of range
                offset = max(0, end_times[start_index-1] - end_on_workstations[workstation])
                min_start_job = end_times[start_index-1]
            end_times[start_index] = end_on_workstations[workstation]+duration+offset
            end_on_workstations[workstation] = end_times[start_index]
            """use_gap = None
            for gap in gaps_on_workstations[workstation]:
                if gap[0] >= min_start_job and gap[1] - gap[0] >= duration:
                    # found a gap
                    use_gap = gap
                    break
            if use_gap:
                # should not have any impact on the end time
                # however, check for new, smaller gap
                index = gaps_on_workstations[workstation].index(use_gap)
                if len(gaps_on_workstations[workstation]) > index+1:
                    # should be sorted
                    if use_gap[1] + duration < gaps_on_workstations[workstation][index+1][0]:
                        gaps_on_workstations[workstation][index] = (use_gap[1], gaps_on_workstations[workstation][index+1][0])
                    else:
                        gaps_on_workstations[workstation].remove(use_gap) # no new gap, just remove the gap from the list
            else:
                if offset > 0:
                    gaps_on_workstations[workstation].append((end_on_workstations[workstation], end_on_workstations[workstation]+offset)) # register the created gap on the workstation
                end_times[start_index] = end_on_workstations[workstation]+duration+offset
                end_on_workstations[workstation] = end_times[start_index]
            gaps_on_workstations[workstation].sort(key=lambda x: x[0]) # NOTE: slow"""
        individual.fitness = max(end_times)


    def _insert_individual(self, individual : Individual, individuals : list[Individual]) -> None:
        if len(individuals) < 1:
            individuals.append(individual)
        else:
            insert_at = 0
            for i in range(len(individuals)):
                if individual.fitness < individuals[i].fitness:
                    insert_at = i
                    break
            individuals.insert(insert_at, individual)

    def _update_history(self, overall_best_history, generation_best_history, average_population_history, current_best, current_population) -> None:
        overall_best_history.append(current_best.fitness)
        generation_best = float('inf')
        generation_average = 0
        for individual in current_population:
            if individual.fitness < generation_best:
                generation_best = individual.fitness
            generation_average += individual.fitness # NOTE: might be float('inf')
        generation_best_history.append(generation_best)
        average_population_history.append(generation_average/len(current_population))
        
    def run(self, population_size : int, offspring_amount : int, max_generations : int, selection : str = 'roulette_wheel', tournament_size : int = 0, elitism : bool = False, random_individuals : int = 0, allow_duplicate_parents : bool = False, output_interval : int = 100):
        population : list[Individual] = []
        overall_best_history : list[float] = []
        generation_best_history : list[float] = []
        average_population_history : list[float] = []
        current_best : Individual = None
        for _ in range(population_size):
            individual = Individual()
            self.evaluate(individual)
            if not current_best or individual.fitness < current_best.fitness:
                current_best = individual
            population.append(individual)
        for i in range(max_generations):
            self._update_history(overall_best_history, generation_best_history, average_population_history, current_best, population)
            if i % output_interval == 0:
                print(f'Generation {i}: Overall Best: {overall_best_history[-1]}, Generation Best: {generation_best_history[-1]}, Average Generation Fitness: {average_population_history[-1]}')
            offsprings = []
            # recombine and mutate, evaluate
            for i in range(0, offspring_amount, 2):
                if selection == 'roulette_wheel':
                    parent_a = self.roulette_wheel_selection(population)
                    parent_b = self.roulette_wheel_selection(population)
                    while not allow_duplicate_parents and parent_a == parent_b:
                        parent_b = self.roulette_wheel_selection(population)
                elif selection == 'tournament':
                    parent_a = self.tournament_selection(population, tournament_size)
                    parent_b = self.tournament_selection(population, tournament_size)
                    while not allow_duplicate_parents and parent_a == parent_b:
                        parent_b = self.tournament_selection(population, tournament_size)
                else:
                    print('Unknown selection parameter')
                offspring_a, offspring_b = self.recombine(parent_a, parent_b)
                if len(offsprings) < offspring_amount: # NOTE: should always be true
                    offspring_a.mutate()
                    self.evaluate(offspring_a)
                    self._insert_individual(offspring_a, offsprings)
                if len(offsprings) < offspring_amount: # NOTE: might be false for odd amounts of offsprings
                    offspring_b.mutate()
                    self.evaluate(offspring_b)
                    self._insert_individual(offspring_b, offsprings)
                selection_pool = []
                selection_pool.extend(offsprings) # already sorted
                if elitism:
                    for individual in population:
                        self._insert_individual(individual, selection_pool) # insert sorted
                population = selection_pool[:population_size - random_individuals]
                while len(population) < population_size:
                    random_individual = Individual()
                    self.evaluate(random_individual)
                    population.append(random_individual)
                if population[0].fitness < current_best.fitness:
                    current_best = population[0]
        return current_best, [overall_best_history, generation_best_history, average_population_history]

# jobs : list[int], workstations_per_operation : list[list[int]], base_durations : list[list[int]]
job_operations = [0, 0, 1, 1, 1, 2, 2] # 7 operations
workstations_per_operation = [ # 4 workstations
    [0, 1, 2],  #0
    [1, 2],     #0
    [1, 2, 3],  #1
    [0, 3],     #1
    [1, 2],     #1
    [3],        #2
    [2, 3]      #2
]
base_durations = [
    [10, 5, 15, 0], # J0O0
    [0, 10, 15, 0], # J0O1
    [0, 5, 15, 10], # J1O0
    [5, 0, 0, 10],  # J1O1
    [0, 15, 5, 0],  # J1O2
    [0, 0, 0, 10],  # J2O0
    [0, 0, 10, 15]  # J2O1
]

"""ga = GA(joboperations, workstations_per_operation, base_durations)
result, history = ga.run(10, 20, 100, output_interval=10)
print(result)
"""
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
instance = 10
production_environment = FJSSPInstancesTranslator().translate(source, instance)
orders = generate_one_order_per_recipe(production_environment)
production_environment.orders = orders
workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)
ga = GA(job_operations, workstations_per_operation, base_durations)

population_size = 25
offspring_amount = 50
max_generations = 1000
elitism = False
allow_duplicate_parents = False
selection = 'roulette_wheel' # 'roulette_wheel' or 'tournament'
tournament_size = int(population_size / 10) # NOTE: only relevant if selection = 'tournament'
random_individual_per_generation_amount = 0#int(population_size / 10)
result, history = ga.run(population_size, offspring_amount, max_generations, selection, tournament_size, elitism=False, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, output_interval=max_generations/20)
print(result)

schedule = encoder.decode(result.sequence, result.workstations, result.workers, result.durations, job_operations, production_environment)

visualize_schedule(schedule, production_environment, orders)

import matplotlib.pyplot as plt
best_history = history[0]
generation_history = history[1]
average_history = history[2]

plt.plot(best_history)
#plt.scatter(range(max_generations), generation_history, s=5, marker='s', color='g')
plt.plot(generation_history, c='g', linewidth=0.5)
#plt.scatter(range(max_generations), average_history, s=1, marker='^', color='r')
plt.plot(average_history, c='r', linewidth=0.1)
plt.legend(['Overall Best', 'Generation Best', 'Average'])
plt.show()