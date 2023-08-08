import random
import time
from multiprocessing import Process, Queue, freeze_support
import copy
import math

class Individual:
    
    required_operations : list[int] = []
    available_workstations : list[list[int]] = []
    available_workers : list[list[int]] = []
    base_durations : list[list[int]] = [] # NOTE: if 0, operation can't be processed on workstation

    # required for initialization with dissimilarity function
    initialization_attempts = 100
    distance_adjustment_rate = 0.75
    min_distance_success = []
    avoid_local_mins = False

    def __init__(self, parent_a = None, parent_b = None, parent_split : list[int] = None, population : list = None, avoid_individuals : list = None, min_avoid_distance : int = 1):
        self.feasible = True
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
            dissimilarity = []
            min_distance = Individual._get_max_dissimilarity()
            attempts = 0
            self.feasible = True
            while len(dissimilarity) == 0 or sum(dissimilarity)/len(dissimilarity) < min_distance:# or (min_distance <= min_avoid_distance and attempts > Individual.initialization_attempts):
                if attempts > Individual.initialization_attempts:
                    min_distance = int(min_distance * Individual.distance_adjustment_rate)
                    if min_distance <= min_avoid_distance:
                        self.feasible = False or not Individual.avoid_local_mins
                        break
                    attempts = 0
                random.shuffle(self.sequence)
                self.workstations = [random.choice(x) for x in Individual.available_workstations]
                for other in population:
                    #dissimilarity = min(self.get_dissimilarity(other), dissimilarity)
                    dissimilarity.append(self.get_dissimilarity(other))
                for local_min in avoid_individuals:
                    if self.get_dissimilarity(local_min) < min_avoid_distance:
                        # TODO: reject
                        dissimilarity = [0]
                attempts += 1
            if min_distance <= 1 and attempts > Individual.initialization_attempts:
                # reject ? - should never happen right now
                print('Failed')
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
    
    def mutate(self, p : float = None, sequence_muatation : str = 'swap'):
        if not p:
            p = 1 / (len(self.sequence) + len(self.workstations)) # NOTE: currently only these 2 lists are in use
        for i in range(len(self.sequence)):
            if random.random() < p:
                if sequence_muatation == 'swap':
                    swap = random.choice([x for x in range(len(self.sequence)) if x != i])
                    tmp = self.sequence[swap]
                    self.sequence[swap] = self.sequence[i]
                    self.sequence[i] = tmp
                elif sequence_muatation == 'insert':
                    take_from = random.choice([x for x in range(len(self.sequence)) if x != i])
                    insert_at = random.choice([x for x in range(len(self.sequence)) if x != i and x != take_from])
                    value = self.sequence.pop(take_from)
                    self.sequence.insert(insert_at, value)
                else:
                    # mixed
                    if random.random() < 0.5:
                        swap = random.choice([x for x in range(len(self.sequence)) if x != i])
                        tmp = self.sequence[swap]
                        self.sequence[swap] = self.sequence[i]
                        self.sequence[i] = tmp
                    else:
                        take_from = random.choice([x for x in range(len(self.sequence)) if x != i])
                        insert_at = random.choice([x for x in range(len(self.sequence)) if x != i and x != take_from])
                        value = self.sequence.pop(take_from)
                        self.sequence.insert(insert_at, value)
        for i in range(len(self.workstations)):
            if random.random() < p:
                if len(Individual.available_workstations[i]) > 1: # otherwise, can't mutate
                    self.workstations[i] = random.choice([x for x in Individual.available_workstations[i] if x != self.workstations[i]])
                    self.durations[i] = (Individual.base_durations[i][self.workstations[i]])
    
    def _get_max_dissimilarity():
        return len(Individual.required_operations) + sum([len(x) for x in Individual.available_workstations])

    def get_dissimilarity(self, other):
        dissimilarity = 0
        
        for i in range(len(self.sequence)):
            if self.workstations[i] != other.workstations[i]:
                dissimilarity += len(Individual.available_workstations[i])
                
            if self.sequence[i] != other.sequence[i]:
                dissimilarity += 1
        return dissimilarity

    def min_makespan_of_workstation_assignment(self):
        # NOTE: ignores all sequence constraints, allows everything parallel
        makespan = [0] * len(self.base_durations[0]) # 0 for all workstations
        for i in range(len(self.workstations)):
            makespan[self.workstations[i]] += self.durations[i]
        return max(makespan)

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
        self.memory : dict[Individual, float] = dict()
        self.memory_access = 0 # keep track of how many solutions were explored multiple times

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

    def evaluate(self, individual : Individual, fill_gaps : bool = False, pruning : bool = False) -> None:
        #if str(individual) in self.memory:
        #    self.memory_access += 1
        #    return self.memory[individual][1]
        if pruning:
            min_makespan = individual.min_makespan_of_workstation_assignment()
            if min_makespan > self.current_best.fitness:
                return 2 * min_makespan
        if not individual.feasible:
            self.infeasible_solutions += 1
            return float('inf')
        if self.avoid_local_mins:
            for local_min in self.local_min:
                if individual.get_dissimilarity(local_min) < self.local_min_distance:
                    individual.feasible = False
                    self.infeasible_solutions += 1
                    return float('inf')
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
        #self.memory[str(individual)] = max(end_times)
        self.function_evaluations+=1

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

    def evaluate_parallel(self, population : list[Individual], adjust_individuals : bool):
        processes = []
        for i in range(len(population)):
            q = Queue()
            if adjust_individuals:
                p = Process(target=evaluate_and_adjust_parallel, args=(population[i], q, len(self.jobs)))
            else:
                p = Process(target=evaluate_only_parallel, args=(population[i], q, len(self.jobs)))
            processes.append((p, q))
            p.start()
        for i in range(len(population)):
            result = processes[i][1].get()
            processes[i][0].join()
            if adjust_individuals:
                population[i] = result
            else:
                population[i].fitness = result

    def create_population(self, population_size, random_initialization, adjust_optimized_individuals, fill_gaps, parallel_evaluation, local_mins = []):
        population = []
        for _ in range(population_size):
            if random_initialization:
                individual = Individual()
            else:
                individual = Individual(population=population, avoid_individuals=local_mins, min_avoid_distance=self.local_min_distance)
            if not parallel_evaluation:
                if adjust_optimized_individuals:
                    self.adjust_individual(individual)
                self.evaluate(individual, fill_gaps)
                """if not self.current_best or individual.fitness < self.current_best.fitness:
                    self.current_best = individual"""
            if True or individual.feasible: # TODO: just for testing
                # NOTE: can lead to smaller population
                population.append(individual)
        if parallel_evaluation:
            batch_size = int(len(population) / 20)
            for i in range(0, len(population)-batch_size, batch_size):
                self.evaluate_parallel(population[i:i+batch_size], adjust_optimized_individuals)
        population.sort(key=lambda individual: individual.fitness)
        if not self.current_best or population[0].fitness < self.current_best.fitness:
            self.current_best = population[0]
        return population

    def update_mutation_probability(self, p, generations_since_last_improvement, max_waiting_before_restart, max_p):
        return p + ((generations_since_last_improvement * (1 / max_waiting_before_restart)) ** 4) * max_p

    def update_mutation_probability_old(self, elitism, starting_p, p, p_increase_rate, max_p, generation_best_history, generation, update_interval, population, overall_best_history):
        if elitism > 0: # NOTE: just experimental, shouldn't make a difference wihtout restarting
            if sum(generation_best_history[generation - update_interval:generation])/update_interval == population[0].fitness:
                return min(p*p_increase_rate, max_p)
            else:
                return starting_p
        else:
            if sum(overall_best_history[generation - update_interval:generation])/update_interval == overall_best_history[-1]: # TODO: change
                return min(p*p_increase_rate, max_p)
            else:
                # should never happen anyway since parameters are adjusted in case of new overall best
                return starting_p


    def simulated_annealing(self, individual):

        def mutate_machine_vector(individual):
            p = 1 / len(individual.workstations)
            for i in range(len(individual.workstations)):
                if random.random() < p:
                    individual.workstations[i] = random.choice([x for x in Individual.available_workstations[i] if x != individual.workstations[i]])
                    individual.durations[i] = (Individual.base_durations[i][individual.workstations[i]])

        def mutate_sequence_vector(individual):
            p = 1 / len(individual.sequence)
            for i in range(len(individual.sequence)):
                if random.random() < p:
                    # insert instead of swap for now
                    take_from = random.choice([x for x in range(len(individual.sequence)) if x != i])
                    insert_at = random.choice([x for x in range(len(individual.sequence)) if x != i and x != take_from])
                    value = individual.sequence.pop(take_from)
                    individual.sequence.insert(insert_at, value)

        n_machine_muatations = 5
        n_sequence_mutations = 20
        initial_T = 20
        alpha = 0.8
        n_T = 7
        T = initial_T
        best = copy.deepcopy(individual)
        for i in range(n_machine_muatations):
            y = copy.deepcopy(individual)
            if i > 0: # check already assigned machines first
                mutate_machine_vector(y)
            for j in range(n_T):
                y_temp = copy.deepcopy(y)
                self.evaluate(y_temp)
                for k in range(n_sequence_mutations):
                    z = copy.deepcopy(y)
                    mutate_sequence_vector(z)
                    self.evaluate(z)
                    if z.fitness < y_temp.fitness:
                        y_temp = z
                if y_temp.fitness < y.fitness or random.random() < math.exp(-(y_temp.fitness - y.fitness)/T):
                    y = y_temp
                if y.fitness < best.fitness:
                    best = y
                T *= alpha
            T = initial_T
        return best

    def run(self, population_size : int, offspring_amount : int, max_generations : int = None, run_for : int = None, stop_at : float = None, selection : str = 'roulette_wheel', tournament_size : int = 0, adjust_parameters : bool = False, update_interval : int = 50, p_increase_rate : float = 1.2, max_p : float = 0.4, restart_at_max_p : bool = False, avoid_local_mins : bool = True, local_min_distance : float = 0.1, elitism : int = 0, sequence_mutation : str = 'swap', pruning : bool = False, fill_gaps : bool = False, adjust_optimized_individuals : bool = False, random_individuals : int = 0, allow_duplicate_parents : bool = False, random_initialization : bool = True, output_interval : int = 100, parallel_evaluation : bool = False):
        self.infeasible_solutions = 0
        self.function_evaluations = 0
        self.restarts = 0
        population : list[Individual] = []
        overall_best_history : list[float] = []
        generation_best_history : list[float] = []
        average_population_history : list[float] = []
        p_history : list[float] = []
        self.current_best : Individual = None
        start_time = time.time()
        self.local_min : list[Individual] = []
        self.avoid_local_mins = avoid_local_mins
        Individual.avoid_local_mins = avoid_local_mins
        self.local_min_distance = Individual._get_max_dissimilarity() * local_min_distance # TODO: add as parameter
        population = self.create_population(population_size, random_initialization, adjust_optimized_individuals, fill_gaps, parallel_evaluation)
        self.overall_best = population[0]
        self.current_best = population[0]
        if len(population) == 0:
            pass # TODO: abort, no feasible population
        if output_interval > 0:
            print(Individual.min_distance_success)
            print(Individual._get_max_dissimilarity())
        population.sort(key=lambda x: x.fitness)
        generation = 0
        starting_p = p = 1 / (len(self.current_best.sequence) + len(self.current_best.workstations)) # mutation probability
        
        gen_stop = (max_generations and generation >= max_generations)
        time_stop = (run_for and False)
        fitness_stop = (stop_at and self.current_best.fitness <= stop_at)
        stop = gen_stop or time_stop or fitness_stop
        last_update = 0
        old_adaptation = False
        while not stop:
            self._update_history(overall_best_history, generation_best_history, average_population_history, p_history, self.overall_best, population, p)
            if output_interval > 0 and generation % output_interval == 0:
                print(f'Generation {generation}: Overall Best: {self.overall_best.fitness}, Current Best: {self.current_best.fitness}, Generation Best: {generation_best_history[-1]}, Average Generation Fitness: {average_population_history[-1]} - Current Runtime: {time.time() - start_time}s, Function Evaluations: {self.function_evaluations}, Restarts: {len(self.local_min)}, Infeasible Solutions: {self.infeasible_solutions}')
            offsprings = []
            # recombine and mutate, evaluate
            # check if mutation probability should be adjusted
            if old_adaptation:
                if adjust_parameters and generation > 0 and generation - last_update >= update_interval:
                    last_update = generation
                    p = self.update_mutation_probability_old(elitism, starting_p, p, p_increase_rate, max_p, generation_best_history, generation, update_interval, population, overall_best_history)
            else:
                if adjust_parameters and generation > 0 and last_update < generation-1:
                    p = self.update_mutation_probability(starting_p, generation - last_update, update_interval, max_p) # TODO: change update interval to different parameter
                
            if restart_at_max_p and p >= max_p:
                #NOTE: could start a local search for the best in the population (not current best known) at this point, maybe even prevent future populations to get too close to the general area (min dissimilarity distance to previous found best)
                local_minimum = self.simulated_annealing(population[0])
                if local_minimum.fitness < population[0].fitness:
                    print(f'Found a better local minimum with simulated annealing with fitness {local_minimum.fitness}')
                if local_minimum.fitness < self.overall_best.fitness:
                    self.overall_best = local_minimum
                self.local_min.append(local_minimum)
                #self.local_min.append(population[0]) # TODO: Maybe use local search algorithm here
                population = self.create_population(population_size, random_initialization, adjust_optimized_individuals, fill_gaps, parallel_evaluation)
                self.current_best = population[0]
                p = starting_p
                p = self.update_mutation_probability(starting_p, len(self.local_min), update_interval, max_p)
                last_update = generation
                self.restarts += 1

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
                    offspring_a.mutate(p, sequence_mutation)
                    if not parallel_evaluation:
                        if adjust_optimized_individuals: # TODO: include into paralell runs, check if changes to individual would be visible in main process
                            self.adjust_individual(offspring_a)
                        self.evaluate(offspring_a, fill_gaps, pruning)
                        self._insert_individual(offspring_a, offsprings)
                    else:
                        offsprings.append(offspring_a)
                if len(offsprings) < offspring_amount: # NOTE: might be false for odd amounts of offsprings
                    offspring_b.mutate(p, sequence_mutation)
                    if not parallel_evaluation:
                        if adjust_optimized_individuals:
                            self.adjust_individual(offspring_b)
                        self.evaluate(offspring_b, fill_gaps, pruning)
                        self._insert_individual(offspring_b, offsprings)
                    else:
                        offsprings.append(offspring_b)
            if parallel_evaluation:
                batch_size = int(len(population) / 20)
                for i in range(0, len(population)-batch_size, batch_size):
                    self.evaluate_parallel(offsprings[i:i+batch_size], adjust_optimized_individuals)
                offsprings.sort(key=lambda offspring: offspring.fitness)
            selection_pool = []
            selection_pool.extend(offsprings) # already sorted
            
            for i in range(elitism):
                self._insert_individual(population[i], selection_pool) # population should be sorted at this point, insert sorted into selection pool
            population = selection_pool[:population_size - random_individuals] if len(selection_pool) >= population_size else selection_pool[:len(selection_pool) - random_individuals] if len(selection_pool) - random_individuals > 0 else []
            while len(population) < population_size:
                if random_initialization:
                    random_individual = Individual()
                else:
                    random_individual = Individual(population=population)
                if adjust_optimized_individuals:
                    self.adjust_individual(random_individual)
                self.evaluate(random_individual, fill_gaps, pruning)
                self._insert_individual(random_individual, population)
            if population[0].fitness < self.current_best.fitness:
                self.current_best = population[0]
                if population[0].fitness < self.overall_best.fitness:
                    self.overall_best = population[0]
                if adjust_parameters:
                    last_update = generation
                    p = starting_p
            generation += 1
            gen_stop = (max_generations and generation >= max_generations)
            time_stop = (run_for and time.time() - start_time >= run_for)
            fitness_stop = (stop_at and self.current_best.fitness <= stop_at)
            stop = gen_stop or time_stop or fitness_stop or len(population) == 0
        if output_interval > 0: # only produce output if needed
            print(f'Finished in {time.time() - start_time} seconds after {generation} generations with best fitness {self.overall_best.fitness}')
            print(f'Max Generation defined: {max_generations} | Max Generation reached: {gen_stop}\nRuntime defined: {run_for} | Runtime finished: {time_stop}\nStopping Fitness defined: {stop_at} | Stopping Fitness reached: {fitness_stop}')
            if len(population) == 0:
                print(f'Could not find any more feasible individuals!')
        return self.overall_best, [overall_best_history, generation_best_history, average_population_history, p_history]

from evaluate_parallel import evaluate_and_adjust_parallel, evaluate_only_parallel
if __name__ == '__main__':
    #freeze_support()
    print('Starting...')