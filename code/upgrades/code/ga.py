import random
import time
import copy
import math

class Individual:
    
    required_operations : list[int] = []
    available_workstations : list[list[int]] = []
    base_durations : list[list[int]] = [] # NOTE: if 0, operation can't be processed on workstation
    jobs : list[int] = []

    # required for initialization with dissimilarity function
    initialization_attempts = 100
    distance_adjustment_rate = 0.75
    min_distance_success = []
    avoid_local_mins = False

    def __init__(self, parent_a = None, parent_b = None, parent_split : list[int] = None, population : list = None, avoid_individuals : list = None, min_avoid_distance : int = 1):
        self.feasible = True
        self.fitness : list[float] = [float('inf')]
        if parent_a and parent_b:
            #crossover
            #sequence crossover
            jobs = Individual.jobs
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
            #self.workstations : list[int] = []
            split = [0 if random.random() < 0.5 else 1 for _ in range(len(parent_a.workstations))]
            self.workstations : list[int] = [parent_a.workstations[i] if split[i] == 0 else parent_b.workstations[i] for i in range(len(parent_a.workstations))]
            #workers
            #durations, currently just base durations
            self.durations : list[int] = [Individual.base_durations[i][self.workstations[i]] for i in range(len(self.workstations))]
        elif parent_a or parent_b:
            #copy
            if parent_a:
                self.sequence = parent_a.sequence.copy()
                self.workstations = parent_a.workstations.copy()
                self.durations = parent_a.durations.copy()
                self.fitness = parent_a.fitness.copy()
            else:
                self.sequence = parent_b.sequence.copy()
                self.workstations = parent_b.workstations.copy()
                self.durations = parent_b.durations.copy()
                self.fitness = parent_b.fitness.copy()
        elif population and len(population) > 0:
            self.sequence : list[int] = Individual.required_operations.copy()
            dissimilarity = []
            min_distance = Individual._get_max_dissimilarity()
            attempts = 0
            #self.feasible = True
            while len(dissimilarity) == 0 or sum(dissimilarity)/len(dissimilarity) < min_distance:
                if attempts > Individual.initialization_attempts:
                    min_distance = int(min_distance * Individual.distance_adjustment_rate)
                    #if min_distance <= min_avoid_distance:
                    #    self.feasible = False or not Individual.avoid_local_mins
                    #    break
                    attempts = 0
                #NOTE: there could probably be a better strategy for this
                random.shuffle(self.sequence)
                self.workstations = [random.choice(x) for x in Individual.available_workstations]
                for other in population:
                    dissimilarity.append(self.get_dissimilarity(other))
                attempts += 1
            if min_distance <= 1 and attempts > Individual.initialization_attempts:
                print('Failed')
            self.durations : list[int] = [Individual.base_durations[i][self.workstations[i]] for i in range(len(self.workstations))]
            Individual.min_distance_success.append(min_distance)
        else:
            # randomize
            self.sequence : list[int] = Individual.required_operations.copy()
            random.shuffle(self.sequence)
            self.workstations : list[int] = [random.choice(Individual.available_workstations[i]) for i in range(len(self.sequence))]  
            self.durations : list[int] = [Individual.base_durations[i][self.workstations[i]] for i in range(len(self.workstations))]
    
    def mutate(self, p : float = None, sequence_muatation : str = 'swap') -> None:
        # note: sequence mutation could probably assigned only once since it shouldn't change during otpimization, also could skip ifs by assigning function pointer
        if not p:
            p = 1 / (len(self.sequence) + len(self.workstations))
        for i in range(len(self.sequence)):
            if random.random() < p:
                if sequence_muatation == 'swap':
                    swap = random.choice([x for x in range(len(self.sequence)) if x != i])
                    tmp = self.sequence[swap]
                    self.sequence[swap] = self.sequence[i]
                    self.sequence[i] = tmp
                elif sequence_muatation == 'insert':
                    insert_at = random.choice([x for x in range(len(self.sequence)) if x != i])
                    value = self.sequence.pop(i)
                    self.sequence.insert(insert_at, value)
                else:
                    # mixed
                    if random.random() < 0.5:
                        swap = random.choice([x for x in range(len(self.sequence)) if x != i])
                        tmp = self.sequence[swap]
                        self.sequence[swap] = self.sequence[i]
                        self.sequence[i] = tmp
                    else:
                        insert_at = random.choice([x for x in range(len(self.sequence)) if x != i])
                        value = self.sequence.pop(i)
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
        return f'Fitness: {self.fitness[0]} | Sequence: {self.sequence} | Workstation Assignments: {self.workstations} | Durations: {self.durations}'

class GA:

    def __init__(self, jobs : list[int], workstations_per_operation : list[list[int]], base_durations : list[list[int]]):
        Individual.required_operations = jobs
        Individual.available_workstations = workstations_per_operation
        Individual.base_durations = base_durations
        self.jobs = []
        for x in jobs:
            if x not in self.jobs:
                self.jobs.append(x)
        Individual.jobs = self.jobs.copy()

    def recombine(self, parent_a : Individual, parent_b : Individual) -> tuple[Individual, Individual]:
        split = [0 if random.random() < 0.5 else 1 for _ in range(len(self.jobs))]
        offspring_a = Individual(parent_a, parent_b, split)
        offspring_b = Individual(parent_b, parent_a, split)
        return offspring_a, offspring_b
    
    def tournament_selection(self, population : list[Individual], tournament_size : int) -> Individual:
        # tournament selection
        if tournament_size == 0:
            tournament_size = int(len(population) / 10)
        participants = random.choices(range(0, len(population)), k=tournament_size)
        winner = sorted(participants, key=lambda x: population[x].fitness[0])[0]
        return population[winner]
    
    def tournament_selection_random(self, population : list[Individual], tournament_size : int) -> Individual:
        if tournament_size == 0:
            tournament_size = int(len(population) / 10)
        participants = random.choices(range(0, len(population)), k=tournament_size)
        sorted_participants = sorted(participants, key=lambda x: population[x].fitness[0])
        equal_winners = [x for x in sorted_participants if population[x].fitness[0] == population[sorted_participants[0]].fitness[0]]
        return population[random.choice(equal_winners)]
    
    def adjust_individual(self, individual : Individual) -> None:
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
        if not individual.feasible:
            self.infeasible_solutions += 1
            individual.fitness[0] = float('inf')
        next_operations = [0] * len(self.jobs)
        end_on_workstations = [0] * len(Individual.base_durations[0])
        end_times = [-1] * len(Individual.required_operations)

        job_start_indices = [0] * len(self.jobs)
        for i in range(1, len(Individual.required_operations)):
            if Individual.required_operations[i] != Individual.required_operations[i-1]:
                job_start_indices[Individual.required_operations[i]] = i


        """gaps_on_workstations : list[list[tuple[int, int]]]= []
        for i in range(len(Individual.base_durations[0])):
            gaps_on_workstations.append([])"""
        for i in range(len(individual.sequence)):
            job = individual.sequence[i]
            operation = next_operations[job]
            start_index = job_start_indices[job]
            """for j in range(len(Individual.required_operations)):
                if Individual.required_operations[j] == job:
                    start_index = j
                    break
                start_index = j"""
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
        individual.fitness[0] = max(end_times)
        self.function_evaluations+=1

    def _insert_individual(self, individual : Individual, individuals : list[Individual]) -> None:
        if len(individuals) < 1:
            individuals.append(individual)
        else:
            inserted = False
            for i in range(len(individuals)):
                if individual.fitness[0] < individuals[i].fitness[0]:
                    individuals.insert(i, individual)
                    break
            if not inserted:
                individuals.append(individual)

    def _update_history(self, overall_best_history, current_best_history, generation_best_history, average_population_history, p_history, current_population, p) -> None:
        overall_best_history.append((self.overall_best[0].fitness[0], self.overall_best))
        current_best_history.append((self.current_best[0].fitness[0], self.current_best))
        generation_best = []#float('inf')
        generation_average = 0
        for individual in current_population:
            if len(generation_best) == 0 or individual.fitness[0] < generation_best[0].fitness[0]:
                generation_best = [individual]
                #generation_best = individual.fitness
            elif individual.fitness[0] == generation_best[0].fitness[0]:
                generation_best.append(individual)
            generation_average += individual.fitness[0] # NOTE: might be float('inf')
        generation_best_history.append((generation_best[0].fitness[0], generation_best))
        average_population_history.append(generation_average/len(current_population))
        p_history.append(p)

    def create_population(self, population_size, random_initialization, adjust_optimized_individuals, fill_gaps) -> list[Individual]:
        population = []
        for _ in range(population_size):
            if random_initialization:
                individual = Individual()
            else:
                individual = Individual(population=population)

            if adjust_optimized_individuals:
                self.adjust_individual(individual)
            self.evaluate(individual, fill_gaps)
            self._insert_individual(individual, population)
        return population

    def update_mutation_probability(self, p, generations_since_last_improvement, max_waiting_before_restart, max_p) -> float:
        return p + ((generations_since_last_improvement * (1 / max_waiting_before_restart)) ** 4) * max_p

    def simulated_annealing(self, individual : Individual) -> Individual:

        def mutate_machine_vector(individual : Individual) -> None:
            p = 1 / len(individual.workstations)
            for i in range(len(individual.workstations)):
                if random.random() < p:
                    individual.workstations[i] = random.choice([x for x in Individual.available_workstations[i] if x != individual.workstations[i]]) if len(Individual.available_workstations[i]) > 1 else individual.workstations[i]
                    individual.durations[i] = (Individual.base_durations[i][individual.workstations[i]])

        def mutate_sequence_vector(individual : Individual) -> None:
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
                    if z.fitness[0] < y_temp.fitness[0]:
                        y_temp = z
                if y_temp.fitness[0] < y.fitness[0] or random.random() < math.exp(-(y_temp.fitness[0] - y.fitness[0])/T):
                    y = y_temp
                if y.fitness[0] < best.fitness[0]:
                    best = y
                T *= alpha
            T = initial_T
        return best

    def determine_ud(self) -> float:
        count = 0
        unique_durations = []
        for row in Individual.base_durations:
            for duration in row:
                if duration > 0:
                    if duration not in unique_durations:
                        unique_durations.append(duration)
                    count += 1
        return len(unique_durations)/count

    def run(self, population_size : int, offspring_amount : int, max_generations : int = None, run_for : int = None, stop_at : float = None, stop_after : int = None, tournament_size : int = 2, adjust_parameters : bool = False, restart_generations : int = 50, max_p : float = 0.4, restart_at_max_p : bool = False, elitism : int = 0, sequence_mutation : str = 'swap', pruning : bool = False, fill_gaps : bool = False, adjust_optimized_individuals : bool = False, random_individuals : int = 0, allow_duplicate_parents : bool = False, random_initialization : bool = True, output_interval : int = 100, elitism_size_scale : float = 0.1, tournament_size_scale : float = 0.2, population_size_growth_per_restart : int = 2, time_checkpoints : list[int] = []):
        ud = self.determine_ud()
        self.infeasible_solutions = 0
        self.function_evaluations = 0
        self.restarts = 0
        population : list[Individual] = []
        overall_best_history : list[list[tuple[float, Individual]]] = []
        current_best_history : list[list[tuple[float, Individual]]] = []
        generation_best_history : list[list[tuple[float, Individual]]] = []
        average_population_history : list[float] = []
        p_history : list[float] = []
        restart_history : list[int] = []
        self.current_best : Individual = None
        start_time = time.time()
        self.local_min : list[Individual] = []
        start_population_size = population_size
        start_offspring_amount = offspring_amount
        population = self.create_population(population_size, random_initialization, adjust_optimized_individuals, fill_gaps) # NOTE: population should be sorted at this point
        self.overall_best = [x for x in population if x.fitness[0] == population[0].fitness[0]]
        self.current_best = self.overall_best.copy()
        generation = 0
        starting_p = p = 1 / (len(self.current_best[0].sequence) + len(self.current_best[0].workstations)) # mutation probability
        time_checkpoint_best = []
        
        time_checkpoint_index = 0

        gen_stop = (max_generations and generation >= max_generations)
        time_stop = (run_for and False)
        fitness_stop = (stop_at and self.current_best[0].fitness[0] <= stop_at)
        feval_stop = (stop_after and self.function_evaluations <= stop_after)
        stop = gen_stop or time_stop or fitness_stop or feval_stop
        last_update = 0
        self._update_history(overall_best_history, current_best_history, generation_best_history, average_population_history, p_history, population, p)
        while not stop:
            if time_checkpoint_index < len(time_checkpoints) and time.time() - start_time >= time_checkpoint_index[time_checkpoint_index]:
                time_checkpoint_best.append((time.time() - start_time, self.overall_best))
                time_checkpoint_index += 1
            if output_interval > 0 and generation % output_interval == 0:
                print(f'Generation {generation}: Overall Best: {self.overall_best[0].fitness[0]}, Current Best: {self.current_best[0].fitness[0]}, Generation Best: {generation_best_history[-1][0]}, Average Generation Fitness: {average_population_history[-1]} - Current Runtime: {time.time() - start_time}s, Function Evaluations: {self.function_evaluations}, Restarts: {len(self.local_min)}, Infeasible Solutions: {self.infeasible_solutions}')

            # check if mutation probability should be adjusted
            if adjust_parameters and generation > 0 and last_update < generation-1:
                p = self.update_mutation_probability(starting_p, generation - last_update, restart_generations, max_p)
                
            if restart_at_max_p and p >= max_p:
                local_minimum = self.simulated_annealing(population[0])

                if local_minimum.fitness[0] < self.overall_best[0].fitness[0]:
                    self.overall_best = [local_minimum]
                elif local_minimum.fitness[0] == self.overall_best[0].fitness[0]:
                    self.overall_best.append(local_minimum)

                #if local_minimum.fitness < self.current_best[0].fitness:
                #    generation_best_history[-1] = local_minimum.fitness
                self.local_min.append(local_minimum)
                max_population_size = 400 # TODO: parameters
                max_offspring_amount = 4* max_population_size # TODO: parameters
                population_size = min(max_population_size, population_size_growth_per_restart * population_size)
                offspring_amount = min(max_offspring_amount, population_size_growth_per_restart * offspring_amount)

                elitism = max(0, int((population_size * elitism_size_scale * ud) + 0.5)) if elitism else 0 # NOTE: population_size_scale between 0 and 1 - if 0, elitism stays 1, but should be allowed to be 0?
                tournament_size = max(1, int((population_size * tournament_size_scale * ud) + 0.5)) # NOTE: tournament_size_scale between 0 and 1 - if 0, tournament_size stays 1 -> random selection

                population = self.create_population(population_size, random_initialization, adjust_optimized_individuals, fill_gaps)
                self.current_best = [population[0]]
                p = starting_p

                last_update = generation
                restart_history.append(generation)
                self.restarts += 1
            offsprings = []
            # recombine and mutate, evaluate
            for j in range(0, offspring_amount, 2):

                parent_a = self.tournament_selection(population, tournament_size)
                parent_b = self.tournament_selection(population, tournament_size)
                while not allow_duplicate_parents and parent_a == parent_b:
                    parent_b = self.tournament_selection(population, tournament_size)

                offspring_a, offspring_b = self.recombine(parent_a, parent_b)
                if len(offsprings) < offspring_amount: # NOTE: should always be true
                    offspring_a.mutate(p, sequence_mutation)

                    if adjust_optimized_individuals:
                        self.adjust_individual(offspring_a)
                    self.evaluate(offspring_a, fill_gaps, pruning)
                    self._insert_individual(offspring_a, offsprings)

                if len(offsprings) < offspring_amount: # NOTE: might be false for odd amounts of offsprings
                    offspring_b.mutate(p, sequence_mutation)

                    if adjust_optimized_individuals:
                        self.adjust_individual(offspring_b)
                    self.evaluate(offspring_b, fill_gaps, pruning)
                    self._insert_individual(offspring_b, offsprings)

            selection_pool : list[Individual] = offsprings # offsprings should already be sorted
            if elitism > 0:
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
            if population[0].fitness[0] < self.current_best[0].fitness[0]:
                self.current_best = [population[0]]
                if adjust_parameters:
                    last_update = generation
                    p = starting_p
            best_index = 0
            while best_index < len(population) and population[best_index].fitness[0] == self.current_best[0].fitness[0]:
                if population[best_index] not in self.current_best:
                    self.current_best.append(population[best_index])
                best_index += 1
            if self.current_best[0].fitness[0] < self.overall_best[0].fitness[0]:
                self.overall_best = self.current_best
            elif self.current_best[0].fitness[0] == self.overall_best[0].fitness[0]:
                for entry in self.current_best:
                    # make sure to not store copies
                    if entry not in self.overall_best:
                        self.overall_best.append(entry)
            self._update_history(overall_best_history, current_best_history, generation_best_history, average_population_history, p_history, population, p)
            generation += 1
            gen_stop = (max_generations and generation >= max_generations)
            time_stop = (run_for and time.time() - start_time >= run_for)
            fitness_stop = (stop_at and self.overall_best[0].fitness[0] <= stop_at)
            feval_stop = (stop_after and self.function_evaluations <= stop_after)
            stop = gen_stop or time_stop or fitness_stop or feval_stop or len(population) == 0
        end_time = time.time() - start_time
        if output_interval > 0: # only produce output if needed
            print(f'Finished in {end_time} seconds after {generation} generations with best fitness {self.overall_best[0].fitness[0]} ({self.restarts} Restarts)')
            print(f'Max Generation defined: {max_generations} | Max Generation reached: {gen_stop}\nRuntime defined: {run_for} | Runtime finished: {time_stop}\nStopping Fitness defined: {stop_at} | Stopping Fitness reached: {fitness_stop}')
            if len(population) == 0:
                print(f'Could not find any more feasible individuals!')
        self.generations = generation

        from history import History
        history = History()
        def to_history_list(in_list):
            out_list : list[tuple[float, list[tuple[int, int]]]]= []
            for entry in in_list:
                out_list.append((entry[0], [(x.sequence, x.workstations) for x in entry[1]]))
            return out_list
        history.overall_best = to_history_list(overall_best_history)
        history.run_best = to_history_list(current_best_history)
        history.generation_best = to_history_list(generation_best_history)
        history.mutation_probability = p_history
        history.restart_generations = restart_history
        history.time_checkpoints = to_history_list(time_checkpoint_best)
        history.function_evaluations = self.function_evaluations
        history.generations = self.generations
        history.runtime = end_time
        history.population_size = start_population_size
        history.offspring_amount = start_offspring_amount
        history.restart_time = restart_generations
        history.max_mutation_rate = max_p
        history.population_growth = population_size_growth_per_restart
        history.elitism_rate = elitism_size_scale
        history.tournament_size = tournament_size_scale
        history.time_limit = run_for
        history.max_generations = max_generations
        history.function_evaluation_limit = stop_after
        history.target_fitness = stop_at
        history.generations_reached = gen_stop
        history.time_exceeded = time_stop
        history.function_evaluations_exceeded = feval_stop
        history.target_fitness_reached = fitness_stop
        history.available_machines = Individual.available_workstations
        history.required_operations = Individual.required_operations
        history.durations = Individual.base_durations
        return history

if __name__ == '__main__':
    print('Starting...')