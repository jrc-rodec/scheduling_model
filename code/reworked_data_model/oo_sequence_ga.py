import random
import time

class Individual:
    
    required_operations : list[int] = []
    available_workstations : list[list[int]] = []
    available_workers : list[list[int]] = []
    base_durations : list[list[int]] = [] # NOTE: if 0, operation can't be processed on workstation

    # required for initialization with dissimilarity function
    initialization_attempts = 100
    distance_adjustment_rate = 0.75
    min_distance_success = []

    def __init__(self, parent_a = None, parent_b = None, parent_split : list[int] = None, population : list = None):
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
        elif population and len(population) > 0:
            self.sequence : list[int] = Individual.required_operations.copy()
            #dissimilarity = float('inf')
            dissimilarity = []
            min_distance = self._get_max_dissimilarity()
            attempts = 0
            #while dissimilarity == float('inf') or dissimilarity < min_distance:
            while len(dissimilarity) == 0 or sum(dissimilarity)/len(dissimilarity) < min_distance:
                if attempts > Individual.initialization_attempts:
                    min_distance = int(min_distance * Individual.distance_adjustment_rate)
                    attempts = 0
                random.shuffle(self.sequence)
                self.workstations = [random.choice(x) for x in Individual.available_workstations]
                for other in population:
                    #dissimilarity = min(self.get_dissimilarity(other), dissimilarity)
                    dissimilarity.append(self.get_dissimilarity(other))
                attempts += 1
            self.workers : list[int] = [0] * len(self.sequence) # NOTE: not in use
            self.durations : list[int] = [] # NOTE: not in use
            for i in range(len(self.workstations)):
                self.durations.append(Individual.base_durations[i][self.workstations[i]])
            Individual.min_distance_success.append(min_distance)
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
    
    def _get_max_dissimilarity(self):
        return len(self.sequence) + sum([len(x) for x in Individual.available_workstations])

    def get_dissimilarity(self, other):
        dissimilarity = 0
        
        for i in range(len(self.sequence)):
            if self.workstations[i] != other.workstations[i]:
                dissimilarity += len(Individual.available_workstations[i])
                
            if self.sequence[i] != other.sequence[i]:
                dissimilarity += 1
        return dissimilarity

    def __eq__(self, other):
        for i in range(len(self.sequence)):
            if self.sequence[i] != other.sequence[i]:
                return False
        for i in range(len(self.workstations)):
            if self.workstations[i] != other.workstations[i]:
                return False
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return f'Fitness: {self.fitness} | Sequence: {self.sequence} | Workstation Assignments: {self.workstations} | Workers: {self.workers} | Durations: {self.durations}'

class GA:

    def __init__(self, jobs : list[int], workstations_per_operation : list[list[int]], base_durations : list[list[int]]):
        Individual.required_operations = jobs
        Individual.available_workstations = workstations_per_operation
        Individual.base_durations = base_durations
        self.jobs = []
        for x in jobs:
            if x not in self.jobs:
                self.jobs.append(x)

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
    
    def adjust_individual(self, individual : Individual):
        class Gap:
            def __init__(self, start, end, before_operation):
                self.start = start
                self.end = end
                self.preceeds_operation = before_operation
        gaps : list[list[Gap]] = []
        available_workstations = []
        n_workstations = len(Individual.base_durations[0])
        for w in range(n_workstations):
            if w not in available_workstations:
                available_workstations.append(w)
        for _ in range(n_workstations):
            gaps.append([])
        end_times_on_workstations : list[int] = [0] * n_workstations
        end_times_of_operations : list[int] = [0] * len(Individual.required_operations)
        next_operation = [0] * len(self.jobs)
        # build schedule
        for i in range(len(individual.sequence)):
            job = individual.sequence[i]
            operation = next_operation[job]
            operation_index = 0
            for j in range(len(Individual.required_operations)):
                if Individual.required_operations[j] == job:
                    operation_index = j
                    break
                operation_index = j
            operation_index += operation
            workstation = individual.workstations[operation_index]
            next_operation[job] += 1
            duration = individual.durations[operation_index]
            inserted : bool = False
            for gap in gaps[workstation]:
                if gap.end - gap.start >= duration:
                    # found a gap, check job seqeunce
                    if operation_index == 0 or (Individual.required_operations[operation_index-1] == Individual.required_operations[operation_index] and end_times_of_operations[operation_index-1] <= gap.end - duration): # AND pre_operation finishes before gap.end - duration
                        # gap can be used
                        inserted = True
                        start = 0 if operation_index == 0 else min(gap.start, end_times_of_operations[operation_index-1])
                        end = start + duration
                        if gap.end - end > 0:
                            # new gap
                            new_gap = Gap(end, gap.end, operation_index)
                            gaps[workstation].append(new_gap)
                        end_times_of_operations[operation_index] = end
                        # swap operations in sequence vector
                        job_swap = Individual.required_operations[gap.preceeds_operation]
                        swap_operation_index = 0
                        swap_start_index = 0
                        for j in range(len(Individual.required_operations)):
                            if Individual.required_operations[j] == job_swap:
                                swap_start_index = j
                                break
                            swap_start_index = j
                        swap_operation_index = gap.preceeds_operation - swap_start_index
                        count = 0
                        swap_individual_index = 0
                        for j in range(len(individual.sequence)):
                            if individual.sequence[j] == job_swap:
                                if count == swap_operation_index:
                                    swap_individual_index = j
                                    break
                                count += 1
                                swap_individual_index = j
                        tmp = individual.sequence[swap_individual_index]
                        individual.sequence[swap_individual_index] = individual.sequence[i]
                        individual.sequence[i] = tmp
                        # remove old gap
                        gaps[workstation].remove(gap)
                        # done
                        break
            if not inserted:
                job_min_start = 0
                if operation_index != 0 and Individual.required_operations[operation_index-1] == Individual.required_operations[operation_index]:
                    job_min_start = end_times_of_operations[operation_index-1]
                if job_min_start > end_times_on_workstations[workstation]:
                    # new gap
                    gaps[workstation].append(Gap(job_min_start, job_min_start + duration, operation_index))
                    end_times_on_workstations[workstation] = job_min_start + duration
                else:
                    end_times_on_workstations[workstation] += duration
                end_times_of_operations[operation_index] = end_times_on_workstations[workstation]

    def evaluate(self, individual : Individual, fill_gaps : bool = False) -> None:
        """jobs = []
        for x in Individual.required_operations:
            if x not in jobs:
                jobs.append(x)
        next_operations = [0] * len(jobs)"""
        next_operations = [0] * len(self.jobs)
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
            if fill_gaps:
                use_gap = None
                for gap in gaps_on_workstations[workstation]:
                    if gap[0] >= min_start_job and gap[0] >= end_on_workstations[workstation] and gap[1] - gap[0] >= duration:
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
                            gaps_on_workstations[workstation].remove(use_gap)
                else:
                    if offset > 0:
                        # register the created gap on the workstation, insert sorted
                        insert_at = 0
                        found = False
                        for i in range(len(gaps_on_workstations[workstation])):
                            if gaps_on_workstations[workstation][i][0] < end_on_workstations[workstation]:
                                insert_at = i
                                found = True
                                break
                        if found:
                            gaps_on_workstations[workstation].insert(insert_at, (end_on_workstations[workstation], end_on_workstations[workstation]+offset))
                        else:
                            gaps_on_workstations[workstation].append((end_on_workstations[workstation], end_on_workstations[workstation]+offset)) 
                    end_times[start_index] = end_on_workstations[workstation]+duration+offset
                    end_on_workstations[workstation] = end_times[start_index]
            else:
                end_times[start_index] = end_on_workstations[workstation]+duration+offset
                end_on_workstations[workstation] = end_times[start_index]
            
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
                insert_at = i
            individuals.insert(insert_at, individual)

    def _update_history(self, overall_best_history, generation_best_history, average_population_history, p_history, current_best, current_population, p) -> None:
        overall_best_history.append(current_best.fitness)
        generation_best = float('inf')
        generation_average = 0
        for individual in current_population:
            if individual.fitness < generation_best:
                generation_best = individual.fitness
            generation_average += individual.fitness # NOTE: might be float('inf')
        generation_best_history.append(generation_best)
        average_population_history.append(generation_average/len(current_population))
        p_history.append(p)
        
    def run(self, population_size : int, offspring_amount : int, max_generations : int = None, run_for : int = None, stop_at : float = None, selection : str = 'roulette_wheel', tournament_size : int = 0, adjust_parameters : bool = False, update_interval : int = 50, p_increase_rate : float = 1.2, max_p : float = 0.4, elitism : int = 0, fill_gaps : bool = False, adjust_optimized_individuals : bool = False, random_individuals : int = 0, allow_duplicate_parents : bool = False, random_initialization : bool = True, output_interval : int = 100):
        population : list[Individual] = []
        overall_best_history : list[float] = []
        generation_best_history : list[float] = []
        average_population_history : list[float] = []
        p_history : list[float] = []
        current_best : Individual = None
        start_time = time.time()
        for _ in range(population_size):
            if random_initialization:
                individual = Individual()
            else:
                individual = Individual(population=population)
            if adjust_optimized_individuals:
                self.adjust_individual(individual)
            self.evaluate(individual, fill_gaps)
            if not current_best or individual.fitness < current_best.fitness:
                current_best = individual
            population.append(individual)
        print(Individual.min_distance_success)
        print(population[0]._get_max_dissimilarity())
        population.sort(key=lambda x: x.fitness)
        generation = 0
        starting_p = p = 1 / (len(current_best.sequence) + len(current_best.workstations)) # mutation probability
        
        gen_stop = (max_generations and generation >= max_generations)
        time_stop = (run_for and False)
        fitness_stop = (stop_at and current_best.fitness <= stop_at)
        stop = gen_stop or time_stop or fitness_stop
        last_update = 0
        while not stop:
        #for i in range(max_generations):
            self._update_history(overall_best_history, generation_best_history, average_population_history, p_history, current_best, population, p)
            if generation % output_interval == 0:
                print(f'Generation {generation}: Overall Best: {overall_best_history[-1]}, Generation Best: {generation_best_history[-1]}, Average Generation Fitness: {average_population_history[-1]} - Current Runtime: {time.time() - start_time}s')
            offsprings = []
            # recombine and mutate, evaluate
            # check if mutation probability should be adjusted
            if adjust_parameters and generation > 0 and generation - last_update >= update_interval:
                # TODO: add progress rate and update interval as parameter
                last_update = generation
                if sum(overall_best_history[generation - update_interval:generation])/update_interval == overall_best_history[-1]:
                    p = min(p*p_increase_rate, max_p)
                else:
                    # should never happen anyway since parameters are adjusted in case of new overall best
                    p = starting_p
                    #p = max(starting_p, p/4)
            for j in range(0, offspring_amount, 2):
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
                    offspring_a.mutate(p)
                    if adjust_optimized_individuals:
                        self.adjust_individual(offspring_a)
                    self.evaluate(offspring_a, fill_gaps)
                    self._insert_individual(offspring_a, offsprings)
                if len(offsprings) < offspring_amount: # NOTE: might be false for odd amounts of offsprings
                    offspring_b.mutate(p)
                    if adjust_optimized_individuals:
                        self.adjust_individual(offspring_b)
                    self.evaluate(offspring_b, fill_gaps)
                    self._insert_individual(offspring_b, offsprings)
            selection_pool = []
            selection_pool.extend(offsprings) # already sorted
            
            for i in range(elitism):
                self._insert_individual(population[i], selection_pool) # population should be sorted at this point, insert sorted into selection pool
            population = selection_pool[:population_size - random_individuals]
            while len(population) < population_size:
                if random_initialization:
                    random_individual = Individual()
                else:
                    random_individual = Individual(population=population)
                self.evaluate(random_individual, fill_gaps)
                self._insert_individual(random_individual, population)
                #population.append(random_individual)
            if population[0].fitness < current_best.fitness:
                current_best = population[0]
                if adjust_parameters:
                    last_update = generation
                    p = starting_p
                    #p = max(starting_p, p/4)
            generation += 1
            gen_stop = (max_generations and generation >= max_generations)
            time_stop = (run_for and time.time() - start_time >= run_for)
            fitness_stop = (stop_at and current_best.fitness <= stop_at)
            stop = gen_stop or time_stop or fitness_stop
        print(f'Finished in {time.time() - start_time} seconds after {generation} generations with best fitness {current_best.fitness}')
        print(f'Max Generation defined: {max_generations} | Max Generation reached: {gen_stop}\nRuntime defined: {run_for} | Runtime finished: {time_stop}\nStopping Fitness defined: {stop_at} | Stopping Fitness reached: {fitness_stop}')
        return current_best, [overall_best_history, generation_best_history, average_population_history, p_history]

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
source = '4_ChambersBarnes'
instance = 7
production_environment = FJSSPInstancesTranslator().translate(source, instance)
orders = generate_one_order_per_recipe(production_environment)
production_environment.orders = orders
workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)
ga = GA(job_operations, workstations_per_operation, base_durations)

population_size = 50
offspring_amount = 100
# stopping criteria - if more than one is defined, GA stops as soon as the first criteria is met
# if a criteria is not in use, initialize it with None
max_generations = 50000
run_for = 600 # seconds, NOTE: starts counting after population initialization
stop_at = None # target fitness

elitism = int(population_size/10) #population_size # maximum amount of individuals of the parent generation that can be transferred into the new generation -> 0 = no elitism, population_size = full elitism
allow_duplicate_parents = True # decides whether or not the same parent can be used as parent_a and parent_b for the crossover operation
fill_gaps = False # optimization for the schedule construction
adjust_optimized_individuals = True # change optimized individuals order of operations
random_initialization = False # False = use dissimilarity function

adjust_parameters = True # decides whether or not the mutation rate should be adjusted during the optimization process
update_interval = 1000 # update after n generations without progress, NOTE: only relevant if adjust_parameters = True
p_increase_rate = 1.1 # multiply current p with p_increase_rate, NOTE: only relevant if adjust_parameters = True
max_p = 1.0 # 1.0 -> turns into random search if there's no progress for a long time, NOTE: only relevant if adjust_parameters = True

selection = 'tournament' # 'roulette_wheel' or 'tournament'
tournament_size = max(2, int(population_size / 10)) # NOTE: only relevant if selection = 'tournament'
random_individual_per_generation_amount = 0#int(population_size / 10) # amount of randomly created individuals included into each new generation, these are also affected by the random_initialization parameter
output_interval = max_generations/20 if max_generations else 100 # frequency of terminal output (in generations)

result, history = ga.run(population_size, offspring_amount, max_generations, run_for, stop_at, selection, tournament_size, adjust_parameters, update_interval=update_interval, p_increase_rate=p_increase_rate, max_p=max_p, elitism=False, fill_gaps=fill_gaps, adjust_optimized_individuals=adjust_optimized_individuals, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, random_initialization=random_initialization, output_interval=output_interval)
print(result)

schedule = encoder.decode(result.sequence, result.workstations, result.workers, result.durations, job_operations, production_environment, fill_gaps)

visualize_schedule(schedule, production_environment, orders)

import matplotlib.pyplot as plt
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
plt.show(block=False)

from visualization import visualizer_for_schedule
visualizer_for_schedule(schedule, job_operations)