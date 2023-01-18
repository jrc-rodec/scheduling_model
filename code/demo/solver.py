import random
import pygad
import cma
import copy
from models import SimulationEnvironment, Order
import sys

class Solver:
    
    def get_order(self, index : int) -> Order:
        job_index = int(index/2)
        sum = 0
        for order in self.orders:
            recipe = self.environment.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            if job_index < sum + len(recipe.tasks):
                return order
            sum += len(recipe.tasks)
        return self.orders[len(self.orders)-1]

    def get_order_index(self, index : int) -> int:
        job_index = int(index/2)
        sum = 0
        index = 0
        for order in self.orders:
            recipe = self.environment.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            if job_index < sum + len(recipe.tasks):
                return index
            sum += len(recipe.tasks)
            index += 1
        return len(self.orders) -1

class GASolver(Solver):

    instance = None

    def __init__(self, encoding : list[int], durations : dict[int, list[int]], job_list : list[int], env : SimulationEnvironment, orders : list[Order]):
        self.name = "GASolver"
        self.encoding = encoding
        self.durations = durations
        self.jobs = job_list
        self.environment = env
        self.orders = orders
        self.assignments_best = []
        self.average_assignments = []
        GASolver.instance = self

    def initialize(self, earliest_slot : int = 0, last_slot : int = 0, population_size : int = 100, offspring_amount : int = 50, max_generations : int = 5000, crossover : str = 'two_points', selection : str = 'rws', mutation : str = 'workstation_only', objective : str ='makespan') -> None:
        self.earliest_slot = earliest_slot
        self.last_slot = last_slot
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        self.max_generations = max_generations
        self.crossover_type = crossover
        self.parent_selection_type = selection
        self.mutation_type = GASolver.alternative_mutation_function # set as default if no feasible option is provided
        if mutation == 'workstation_only':
            self.mutation_type = GASolver.alternative_mutation_function
        elif mutation == 'full_random':
            self.mutation_type = GASolver.mutation_function
        elif mutation == 'random_only_feasible':
            self.mutation_type = GASolver.only_feasible_mutation
        self.mutation_percentage_genes = 10 # not used, but necessary parameter
        self.gene_type = int
        self.keep_parents = int(self.population_size / 4) # TODO: add as parameter
        gene_space_workstations = {'low': 0, 'high': len(self.environment.workstations)}
        gene_space_starttime = {'low': self.earliest_slot, 'high': self.last_slot}
        self.gene_space = []
        self.objective = objective
        self.objective_function = GASolver.fitness_function
        if objective == 'makespan':
            self.objective_function = GASolver.fitness_function
        elif objective == 'idle_time':
            self.objective_function = GASolver.fitness_function_idle_time
        for _ in range(0, len(self.encoding), 2):
            self.gene_space.append(gene_space_workstations)
            self.gene_space.append(gene_space_starttime)
        self.ga_instance = pygad.GA(num_generations=max_generations, num_parents_mating=int(self.population_size/2), fitness_func=self.objective_function, on_fitness=GASolver.on_fitness_assignemts, sol_per_pop=population_size, num_genes=len(self.encoding), init_range_low=self.earliest_slot, init_range_high=self.last_slot, parent_selection_type=self.parent_selection_type, keep_parents=self.keep_parents, crossover_type=self.crossover_type, mutation_type=self.mutation_type, mutation_percent_genes=self.mutation_percentage_genes, gene_type=self.gene_type, gene_space=self.gene_space)
        
        self.best_solution = None

    def run(self) -> None:
        self.ga_instance.run()
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        self.solution_index = solution_idx
        self.best_solution = (solution, solution_fitness)
        print("Done")

    def get_best(self) -> list[int]:
        return self.best_solution[0]

    def get_best_fitness(self) -> int:
        return self.best_solution[1]

    def get_result_jobs(self) -> list[int]:
        return self.jobs

    def mutation_function(offsprings : list[list[int]], ga_instance) -> list[list[int]]:
        instance : GASolver = GASolver.instance
        index = 0
        for offspring in offsprings:
            p = 1 / (len(offspring)/2) # amount of jobs
            for i in range(0, len(offspring), 2):
                if random.random() < p:
                    # mutate workstation assignment
                    workstations = instance.environment.get_all_workstations_for_task( instance.jobs[int(i/2)])
                    offspring[i] = random.choice(workstations).id
                    # mutate start time
                    offspring[i+1] = random.randint(instance.earliest_slot, instance.last_slot)
            index += 1
        return offsprings
    
    def has_overlaps(self, offspring : list[int], i : int, start_time : int, end_time : int) -> bool:
        instance : GASolver = GASolver.instance
        for j in range(0, len(offspring), 2):
                if not i == j:
                    if offspring[i] == offspring[j]: # tasks run on the same workstation
                        other_job = instance.jobs[int(j/2)]
                        own_start = start_time
                        other_start = offspring[j+1]
                        other_duration = instance.durations[other_job][offspring[j]]
                        own_end = end_time
                        other_end = other_start + other_duration
                        if own_start >= other_start and own_start < other_end:
                            return True
                        if own_end > other_start and own_end <= other_end:
                            return True
                        if other_start >= own_start and other_start < own_end:
                            return True
                        if other_end > own_start and other_end <= own_end:
                            return True
        return False

    def only_feasible_mutation(offsprings : list[list[int]], ga_instance) -> list[list[int]]:
        instance : GASolver = GASolver.instance
        for offspring in offsprings:
            p = 1 / (len(offspring)/2)
            for i in range(0, len(offspring), 2):
                if random.random() < p:
                    workstations = instance.environment.get_all_workstations_for_task(instance.jobs[int((i)/2)])
                    offspring[i] = random.choice(workstations).id
                    # choose random start time until fitting spot is found, or amount of tries is up
                    tries = 10000
                    start_time = random.randint(instance.earliest_slot, instance.last_slot)
                    duration = instance.durations[instance.jobs[int(i / 2)]][offspring[i]]
                    end_time = start_time + duration
                    current_try = 0
                    while current_try < tries and instance.has_overlaps(offspring, i, start_time, end_time):
                        start_time = random.randint(instance.earliest_slot, instance.last_slot)
                        end_time = start_time + duration
                        current_try += 1
                    offspring[i+1] = start_time
        return offsprings

    def alternative_mutation_function(offsprings : list[list[int]], ga_instance) -> list[list[int]]:
        instance = GASolver.instance
        for offspring in offsprings:
            prev_order = -1
            current_order = 0
            p = 1 / (len(offspring)/2)
            for i in range(0, len(offspring), 2):
                current_order = instance.get_order_index(i)
                if random.random() < p:
                    # adjust workstation
                    workstations = instance.environment.get_all_workstations_for_task( instance.jobs[int(i/2)])
                    offspring[i] = random.choice(workstations).id
                # adjust start time for all, independent of workstation assignment mutation
                min_time_previous_job = 0
                if prev_order == current_order:
                    min_time_previous_job = offspring[i-1] + instance.durations[instance.jobs[int((i-2)/2)]][offspring[i-2]] # end of previous task in the same order
                min_time_workstation = -1
                current_duration = instance.durations[instance.jobs[int((i-1)/2)]][offspring[i]]
                # gather all jobs currently assigned to the same workstation
                assignments = []
                for j in range(0, i, 2): # NOTE: maybe needs to consider ALL jobs <start time, end time>
                    if offspring[j] == offspring[i]:
                        assignments.append([offspring[j+1], offspring[j+1] + instance.durations[instance.jobs[int(j/2)]][offspring[j]]])
                # find first slot big enough to fit the job
                if len(assignments) > 1: # if more than one job is on the same workstation, find first fitting slot
                    for j in range(1, len(assignments)):
                        if assignments[j][0] - assignments[j-1][1] >= current_duration and assignments[j-1][1] >= min_time_previous_job:
                            min_time_workstation = assignments[j-1][1]
                            break
                    if min_time_workstation == -1: # this should only be the case if there is no free slot in between, so put it at the end
                        min_time_workstation = assignments[len(assignments)-1][1] # set to end of the last assigned job
                elif len(assignments) == 1: # if only only one other job is on the same workstation, set to end of that job
                    min_time_workstation = assignments[0][1]
                else:
                    min_time_workstation = 0 # no other jobs on the same workstation, can start at 0
                offspring[i+1] = max(min_time_previous_job, min_time_workstation) # max between the two is the first feasible slot for the job
                prev_order = current_order
        return offsprings

    def on_fitness_assignemts(ga_instance, population_fitness) -> None:
        instance = GASolver.instance
        current_best = abs(sorted(population_fitness, reverse=True)[0]) - 1
        if len(instance.assignments_best) == 0:
            instance.assignments_best.append(current_best)
        elif current_best < instance.assignments_best[len(instance.assignments_best)-1]:
            instance.assignments_best.append(current_best)
        else:
            instance.assignments_best.append(instance.assignments_best[len(instance.assignments_best)-1])
        sum = 0
        for individual_fitness in population_fitness:
            sum += abs(individual_fitness)-1
        instance.average_assignments.append(sum/len(population_fitness))

    def fitness_function(solution : list[int], solution_idx) -> int:
        fitness = 0
        if not GASolver.is_feasible(solution):
            return - (2 * GASolver.instance.last_slot)
        # use makespan for now
        min = float('inf')
        max = -float('inf')
        for i in range(1, len(solution), 2): # go through all start times
            if solution[i] < min:
                min = solution[i]
            task = GASolver.instance.jobs[int((i-1) / 2)]
            if solution[i] + GASolver.instance.durations[task][solution[i-1]] > max:
                max = solution[i] + GASolver.instance.durations[task][solution[i-1]]
        fitness += abs(max - min)
        return -fitness # NOTE: PyGAD always maximizes

    def fitness_function_idle_time(solution : list[int], solution_idx) -> int:
        fitness = 0
        if not GASolver.is_feasible(solution):
            return - (2 * GASolver.instance.last_slot)
        unused_workstations = 0
        last_timeslot = 0
        for workstation in GASolver.instance.environment.workstations:
            used = False
            slots = []
            for i in range(0, len(solution), 2):
                if solution[i] == workstation.id:
                    used = True
                    start = solution[i + 1]
                    duration = GASolver.instance.durations[GASolver.instance.jobs[int(i/2)]][solution[i]]
                    end = start + duration
                    slots.append((start, end))
                    if end > last_timeslot:
                        last_timeslot = end
            sorted_slots = sorted(slots, key=lambda x: x[0])
            last_end = 0
            for slot in sorted_slots:
                fitness += slot[0] - last_end
                last_end = slot[1]
            if not used:
                unused_workstations += 1
        fitness += unused_workstations * last_timeslot
        return -fitness

    def is_feasible(solution : list[int]) -> bool:
        order = None
        instance : GASolver = GASolver.instance
        for i in range(0, len(solution), 2): # go through all workstation assignments
            job = instance.jobs[int(i/2)]
            # check for last time slot
            if solution[i+1] + instance.durations[job][solution[i]] > instance.last_slot:
                return False
            # check for earliest time slot
            if solution[i+1] < instance.earliest_slot:
                return False
            # check for overlaps
            for j in range(0, len(solution), 2):
                if not i == j:
                    if solution[i] == solution[j]: # tasks run on the same workstation
                        other_job = instance.jobs[int(j/2)]
                        own_start = solution[i+1]
                        other_start = solution[j+1]
                        own_duration = instance.durations[job][solution[i]]
                        other_duration = instance.durations[other_job][solution[j]]
                        own_end = own_start + own_duration
                        other_end = other_start + other_duration
                        if own_start >= other_start and own_start < other_end:
                            return False
                        if own_end > other_start and own_end <= other_end:
                            return False
                        if other_start >= own_start and other_start < own_end:
                            return False
                        if other_end > own_start and other_end <= own_end:
                            return False
            # check for correct sequence
            prev_order = order
            order = instance.get_order(i) # find order corresponding to task
            if order:
                if not prev_order is None and order.id == prev_order.id: # if current task is not the first job of this order, check if the previous job ends before the current one starts
                    prev_start = solution[i-1]
                    prev_end = prev_start + instance.durations[instance.jobs[int((i-2)/2)]][solution[i-2]]
                    if solution[i+1] < prev_end:
                        return False
            else:
                print("Something went completely wrong!") # TODO: should probably throw exception
        return True

from pyswarm import pso # NOTE: pyswarm, not pyswarms (2 different libraries) -> pyswarm allows constraints and multiple lb+ub
# example and explanation for pyswarm: https://pythonhosted.org/pyswarm/
#NOTE: pyswarm always minimizes
class PSOSolver(Solver):
    
    instance = None

    def __init__(self, encoding, durations, job_list, environment, orders):
        self.name = "PSOSolver"
        self.encoding = encoding
        self.durations = durations
        self.jobs = job_list
        self.environment = environment
        self.orders = orders
        
        self.objective = 'makespan'

        self.assignments_best = []
        self.average_assignments = []
        PSOSolver.instance = self

    def initialize(self, earliest_slot, last_slot, c1 : float = 0.5, c2 : float = 0.3, w : float = 0.9, swarmsize : int = 100, max_iter : int = 1000):
        self.options = {'c1': c1, 'c2': c2, 'w':w}
        self.swarmsize = swarmsize
        self.max_iter = max_iter
        self.minstep = 0.1 # minimum stepsize of swarm's position before the search terminates, currently unused
        self.lb = [] # TODO: maybe add as parameter?
        self.ub = []
        for i in range(0, len(self.encoding), 2):
            self.lb.append(0)
            self.ub.append(len(self.environment.workstations)-1) # NOTE: the upper bounds are inclusive
            self.lb.append(earliest_slot)
            self.ub.append(min(self.get_order(i).latest_acceptable_time, last_slot))

    def run(self):
        # Perform optimization
        xopt, fopt = pso(PSOSolver.objective_function, self.lb, self.ub, maxiter=self.max_iter, phip=self.options['c1'], phig=self.options['c2'], omega=self.options['w'], swarmsize=self.swarmsize, ieqcons=[PSOSolver.correct_assignment_con, PSOSolver.correct_sequence_con, PSOSolver.no_overlaps_con]) # maybe needs lb=lb, ub=ub
        self.best_solution = (xopt, fopt)
        print("Done")

    def correct_assignment_con(x):
        instance = PSOSolver.instance
        for i in range(0, len(x), 2):
            if instance.durations[instance.jobs[int(i/2)]][int(x[i] + 0.5)] == 0:
                return -1
        return 0.0
    
    def correct_sequence_con(x):
        instance = PSOSolver.instance
        for i in range(2, len(x), 2):
            prev_order = instance.get_order_index(i-2)
            current_order = instance.get_order_index(i)
            if prev_order == current_order:
                start = int(x[i+1] + 0.5)
                prev_end = int(x[i-1] + 0.5) + instance.durations[instance.jobs[int((i-2)/2)]][int(x[i-2] + 0.5)]
                if start - prev_end < 0:
                    return -1
        return 0.0

    def no_overlaps_con(x):
        instance = PSOSolver.instance
        for i in range(0, len(x), 2):
            workstation = int(x[i] + 0.5)
            start = int(x[i+1] + 0.5)
            duration = instance.durations[instance.jobs[int(i / 2)]][workstation]
            end = start + duration
            for j in range(0, len(x), 2):
                if j != i and int(x[j] + 0.5) == workstation:
                    # check for overlaps
                    other_start = int(x[j+1] + 0.5)
                    other_duration = instance.durations[instance.jobs[int(j/2)]][workstation]
                    other_end = other_start + other_duration
                    # check if start is between other_start and other_end
                    if start >= other_start and start < other_end:
                        return -1
                    # check if end is between other_start and other_end
                    if end > other_start and end <= other_end:
                        return -1
                    # check the other way around, in case other is enclosed by the current task
                    if other_start >= start and other_start < end:
                        return -1
                    if other_end > start and other_end <= end:
                        return -1
        return 0.0

    # objective function - using makespan for now
    def objective_function(x):
        instance = PSOSolver.instance
        min = float('inf')
        max = 0
        for i in range(0, len(x), 2):
            workstation = int(x[i] + 0.5)
            start = int(x[i+1] + 0.5)
            end = start + instance.durations[instance.jobs[int(i / 2)]][workstation]
            if start < min:
                min = start
            if end > max:
                max = end
        return max - min
        
    def get_best_real_values(self):
        return self.best_solution[0]

    def get_best(self):
        result = []
        for value in self.best_solution[0]:
            result.append(int(value+0.5))
        return result

    def get_best_fitness(self):
        return self.best_solution[1]


class GreedyAgentSolver(Solver):

    instance = None

    def __init__(self, encoding, durations, job_list, environment, orders):
        self.name = "GreedyAgentSolver"
        self.encoding = encoding
        self.objective = 'makespan'
        self.durations = durations
        self.jobs = job_list
        self.environment = environment
        self.orders = orders

        self.assignments_best = []
        self.average_assignments = []
        GreedyAgentSolver.instance = self

    def initialize(self):
        pass

    def run(self, output : bool = True):
        result = len(self.encoding) * [-1]
        prev_order = -1
        for i in range(0, len(result), 2):
            current_order = self.get_order_index(i)
            workstation_options = []
            for j in range(len(self.durations[self.jobs[int(i/2)]])):
                if self.durations[self.jobs[int(i/2)]][j] != 0:
                    duration = self.durations[self.jobs[int(i/2)]][j] # save workstation with duration
                    tasks_on_workstation = []
                    for k in range(0, i, 2):
                        if j == result[k]:
                            tasks_on_workstation.append([k, result[k+1], result[k+1] + self.durations[self.jobs[int(k/2)]][result[k]]]) # save index, start time and end time, probably don't need index
                    tasks_on_workstation.sort(key=lambda x:x[1]) # sort by start time
                    # find gaps
                    for k in range(1, len(tasks_on_workstation)):
                        if tasks_on_workstation[k][1] - tasks_on_workstation[k-1][2] >= duration:
                            workstation_options.append((j, tasks_on_workstation[k-1][2])) # save workstation + end of previous task
                    if len(tasks_on_workstation) > 0:
                        workstation_options.append((j, tasks_on_workstation[-1][2])) # add the workstation + end of the current last task on the workstation as option
                    else:
                        workstation_options.append((j, 0)) # first task on this workstation
            # workstation_options should contain all viable slots for the current task
            # remove all slots that would invalidate the sequence of an order
            if prev_order == current_order:
                prev_start = result[i-1]
                prev_end = prev_start + self.durations[self.jobs[int((i-2)/2)]][result[i-2]]
                workstation_options = [option for option in workstation_options if option[1] >= prev_end] # should remove every starting slot before prev_end
            # at this point, workstation_option should only contain valid possible starting slots for the current task
            # evaluate all options to find options with the smallest impact on makespan
            best_makespan = []
            for option in workstation_options:
                test_solution = copy.deepcopy(result) # slow
                test_solution[i] = option[0] # workstation
                test_solution[i+1] = option[1] # start time slot
                test_fitness = self.makespan(test_solution)
                if len(best_makespan) == 0 or test_fitness <= best_makespan[0][1]:
                    if len(best_makespan) > 0 and test_fitness < best_makespan[0][1]:
                        best_makespan = []
                    best_makespan.append((test_solution, test_fitness))
            # TODO: if more than one best solution, evaluate secondary objective, or choose randomly
            best_idle = [] # copy.deepcopy(best_makespan)
            for option in best_makespan:
                test_solution = copy.deepcopy(option[0]) # slow
                test_fitness = self.idle_time(test_solution)
                if len(best_idle) == 0 or test_fitness <= best_idle[0][1]:
                    if len(best_idle) > 0 and test_fitness < best_idle[0][1]:
                        best_idle = []
                    best_idle.append((test_solution, test_fitness))
            # choose randomly from all best_idle solutions
            result = copy.deepcopy(random.choice(best_idle))[0] # choose randomly for now
            prev_order = current_order
        self.best_solution = (result, self.makespan(result))
        if output:
            print("Done")
        
    def makespan(self, solution):
        min = float('inf')
        max = 0
        for i in range(0, len(solution), 2):
            if solution[i] != -1:
                if solution[i+1] < min:
                    min = solution[i+1]
                if solution[i+1] + self.durations[self.jobs[int(i/2)]][solution[i]] > max:
                    max = solution[i+1] + self.durations[self.jobs[int(i/2)]][solution[i]]
        return max - min
    
    def idle_time(self, solution):
        result = 0
        for workstation in self.environment.workstations:
            id = workstation.id
            on_workstation = []
            # get all start and end times on workstation:
            for i in range(0, len(solution), 2):
                if solution[i] == id:
                    start = solution[i+1]
                    end = start + self.durations[self.jobs[int(i/2)]][id]
                    on_workstation.append((start, end))
            on_workstation.sort(key= lambda x:x[0]) # sort by start times
            for i in range(1, len(on_workstation)):
                result += on_workstation[i][0] - on_workstation[i-1][1]
        return result

    def get_best(self):
        return self.best_solution[0]

    def get_best_fitness(self):
        return self.best_solution[1]

class HybridGreedyAgentSolver(Solver):
    instance = None

    def __init__(self, inner_encoding, durations, job_list, environment, orders):
        self.agent = GreedyAgentSolver(inner_encoding, durations, job_list, environment, orders)
        self.encoding = []
        for i in range(len(job_list)):
            self.encoding.append(i)
        self.durations = durations
        self.inner_encoding = inner_encoding
        self.jobs = job_list
        self.environment = environment
        self.orders = orders

    def initialize(self, mutation : str = 'swap', crossover : str = 'two_points', selection : str = 'rws', max_generations : int = 1000, population_size : int = 100, earliest_slot : int = 0, last_slot : int = 1000):
        self.last_slot = last_slot
        self.earliest_slot = earliest_slot
        self.mutation = mutation
        self.crossover = crossover
        self.selection = selection

        self.max_generations = max_generations
        self.population_size = population_size
        self.mutation_percentage_genes = 10 # not used, but necessary parameter
        self.gene_type = int
        self.keep_parents = int(self.population_size / 4) # TODO: add as parameter

        self.ga_instance = pygad.GA(num_generations=max_generations, num_parents_mating=int(self.population_size/2), fitness_func=HybridGreedyAgentSolver.objective_function, sol_per_pop=population_size, num_genes=len(self.encoding), parent_selection_type=self.selection, keep_parents=self.keep_parents, crossover_type=self.crossover, mutation_type=self.mutation, mutation_percent_genes=self.mutation_percentage_genes, gene_type=self.gene_type)
        
        HybridGreedyAgentSolver.instance = self

    def objective_function(solution : list[int], solution_idx) -> int:
        instance = HybridGreedyAgentSolver.instance
        job_list = []
        for entry in solution:
            job_list.append(instance.jobs[entry])
        instance.agent.jobs = job_list
        instance.agent.run(False)
        result = instance.agent.get_best()
        if not HybridGreedyAgentSolver.is_feasible(result):
            return -1000 #TODO: replace value
        fitness = instance.agent.get_best_fitness()
        return -fitness

    def is_feasible(solution : list[int]) -> bool:
        order = None
        instance = HybridGreedyAgentSolver.instance
        for i in range(0, len(solution), 2): # go through all workstation assignments
            job = instance.jobs[int(i/2)]
            # check for last time slot
            if solution[i+1] + instance.durations[job][solution[i]] > instance.last_slot:
                return False
            # check for earliest time slot
            if solution[i+1] < instance.earliest_slot:
                return False
            # check for overlaps
            for j in range(0, len(solution), 2):
                if not i == j:
                    if solution[i] == solution[j]: # tasks run on the same workstation
                        other_job = instance.jobs[int(j/2)]
                        own_start = solution[i+1]
                        other_start = solution[j+1]
                        own_duration = instance.durations[job][solution[i]]
                        other_duration = instance.durations[other_job][solution[j]]
                        own_end = own_start + own_duration
                        other_end = other_start + other_duration
                        if own_start >= other_start and own_start < other_end:
                            return False
                        if own_end > other_start and own_end <= other_end:
                            return False
                        if other_start >= own_start and other_start < own_end:
                            return False
                        if other_end > own_start and other_end <= own_end:
                            return False
            # check for correct sequence
            prev_order = order
            order = instance.get_order(i) # find order corresponding to task
            if order:
                if not prev_order is None and order.id == prev_order.id: # if current task is not the first job of this order, check if the previous job ends before the current one starts
                    prev_start = solution[i-1]
                    prev_end = prev_start + instance.durations[instance.jobs[int((i-2)/2)]][solution[i-2]]
                    if solution[i+1] < prev_end:
                        return False
            else:
                print("Something went completely wrong!") # TODO: should probably throw exception
        return True


    def run(self):
        self.ga_instance.run()
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        self.solution_index = solution_idx
        self.best_solution = (solution, solution_fitness)
        self.agent.run()
        self.agent_best_solution = self.agent.best_solution
        print("Done")

    def re_run_agent(self):
        self.agent.run()
        return self.agent.best_solution

    def get_best(self):
        return self.agent_best_solution[0]
    
    def get_best_fitness(self):
        return self.agent_best_solution[1]

class CMAWeightSolver(Solver):

    instance = None

    def __init__(self, encoding, durations, job_list, environment, orders):
        self.name = "CMAWeightSolver"
        self.encoding = encoding
        self.objective = 'makespan'
        self.durations = durations
        self.jobs = job_list
        self.environment = environment
        self.orders = orders
        
        CMAWeightSolver.instance = self

    def initialize(self):
        pass

    def constraints(x):
        return [0]

    def run(self):
        x0 = len(self.encoding) * [0.0]
        xopt, es = cma.fmin2(objective_function=CMAWeightSolver.fitness_function, x0=x0, sigma0=0.5, options={'bounds': [0.0,100.0], 'is_feasible': CMAWeightSolver._is_feasible})
        #xopt, es = cma.fmin_con2(objective_function=CMAWeightSolver.fitness_function, x0=x0, sigma0=0.5, find_feasible_first=True, find_feasible_final=False, options={'bounds': [0.0, 100.0], 'is_feasible': CMAWeightSolver._is_feasible})
        #cfun = cma.ConstrainedFitnessAL(CMAWeightSolver.fitness_function, CMAWeightSolver.constraints, find_feasible_first=True)
        #es = cma.CMAEvolutionStrategy(x0, 0.5, inopts={'tolstagnation': 0})
        #es = es.optimize(cfun, callback=cfun.update)
        #xopt = es.result.xfavorite
        self.best_solution = (xopt, es) # TODO: lookup fitness value for 2nd parameter
        print("Done")

    def _get_assignments_for_workstation(self, assignments, workstation):
        return assignments[workstation]

    def _get_order(self, index):
        sum = 0
        for order in self.orders:
            recipe = self.environment.get_recipe_by_id(order.resources[0])
            if index < sum + len(recipe.tasks):
                return order
            sum += len(recipe.tasks)
        return self.orders[len(self.orders)-1]

    def _is_first(self, index):
        sum = 0
        for i in range(len(self.orders)):
            if i < sum + (len(self.environment.get_recipe_by_id(self.orders[i].resources[0]).tasks)):
                return index - sum == 0 #?
            sum += len(self.environment.get_recipe_by_id(self.orders[i].resources[0]).tasks)
        return False

    def _find_suitable_slots(self, assignments, job, durations, workstation):
        duration = durations[job][workstation]
        prev_end_time = 0
        slots = []
        if len(assignments) == 0:
            slots.append(0)
        else:
            for assignment in assignments:
                if assignment[1] - prev_end_time >= duration:
                    slots.append(prev_end_time)
                prev_end_time = assignment[2]
            last_assignment = assignments[len(assignments)-1]
            if last_assignment[1] + durations[last_assignment[0]][workstation] not in slots:
                slots.append(last_assignment[1] + durations[last_assignment[0]][workstation])
        return slots

    def _get_start_times(self, assignments, jobs, durations, scheduled):
        start_times = []
        workstation_assignments = []
        for workstation in self.environment.workstations:
            w_assignments = self._get_assignments_for_workstation(assignments, workstation.id)
            if not w_assignments:
                w_assignments : list[tuple[int, int, int, int]] = []
            workstation_assignments.append(w_assignments)
        for i in range(len(jobs)):
            order = self._get_order(i)
            times = [order.latest_acceptable_time for _ in self.environment.workstations]
            min_times = [0 for _ in self.environment.workstations]
            if not scheduled[i]:
                # get order id
                order : Order = self._get_order(i)
                # check if job is first of order
                first : bool = self._is_first(i)
                if not first:
                    # find previous scheduled tasks of same order
                    for workstation in self.environment.workstations:
                        for assignment in workstation_assignments[workstation.id]: # assignment = <task_id, start_time, end_time, order_id>
                            if assignment[3].id == order.id:
                                min_times[workstation.id] = assignment[2]
                for workstation in self.environment.workstations:
                    sorted_assignments = copy.deepcopy(assignments[workstation.id])
                    sorted_assignments.sort(key = lambda x : x[1])
                    possible_start_times = self._find_suitable_slots(sorted_assignments, jobs[i], durations, workstation.id)
                    for start_time in possible_start_times:
                        if start_time >= max(min_times) and start_time < times[workstation.id]:
                            times[workstation.id] = start_time
            start_times.append(times)
        return start_times

    def _get_next(self, costs):
        current_min = float('inf')
        index = 0
        for i in range(len(costs)):
            if any(value < current_min for value in costs[i]):
                index = i
                current_min = min(costs[i])
        return index

    def _cost_function(self, weight, p_all, due_date, start_times): # calculate priority of each job to be scheduled next, big weight = low priority score (min priority score is next)
        d = due_date # just consider deliver time, not latest acceptable
        costs = []
        for i in range(len(p_all)):
            if start_times[i] == 0:
                start_times[i] = 1 # TODO: change
            if weight == 0:
                weight = 0.00000000001 # TODO: change
            costs.append((p_all[i] * (d / start_times[i])) / weight) # if cost = 0, not possible on workstation
        return costs # returns cost for each workstation

    def _build_schedule(self, weights, workstations, durations, jobs):
        assignments : list[list[tuple[int, int, int, int]]] = [[] for _ in workstations] # tuples of job_id, start_time, end_time, order_id for each workstation
        scheduled = [False for _ in jobs]
        values = copy.deepcopy(weights)
        for _ in range(len(values)):
            # find start times
            start_times = self._get_start_times(assignments, jobs, durations, scheduled)
            # find cost
            costs = []
            for i in range(len(values)):
                due_date = self._get_order(i).delivery_time # TODO: double check
                costs.append(self._cost_function(values[i], durations[jobs[i]], due_date, start_times[i]))
            # choose next job to schedule
            next_job = self._get_next(costs)
            # schedule next job
            workstation = costs[next_job].index(min(costs[next_job])) # TODO: double check
            values[next_job] = float('inf')
            start_time = start_times[jobs[next_job]][workstation]
            end_time = start_time + durations[jobs[next_job]][workstation]
            assignments[workstation].append((jobs[next_job], start_time, end_time, self._get_order(next_job))) # TODO: double check next_job use for _get_order
            scheduled[next_job] = True
        return assignments

    def _is_feasible(x, f):
        return True

    def fitness_function(x):
        # makespan
        instance : CMAWeightSolver = CMAWeightSolver.instance # get access to all information
        workstations : list[int] = [w.id for w in instance.environment.workstations]
        durations : dict[int, list[int]] = instance.durations
        jobs = instance.jobs
        assignments : list[list[tuple[int, int, int, int]]] = instance._build_schedule(x, workstations, durations, jobs)
        last = 0
        first = float('inf')
        for i in range(len(assignments)):
            w_assignment = copy.deepcopy(assignments[i])
            w_assignment.sort(key = lambda y : y[1]) # sort by start times
            if len(w_assignment) == 0:
                w_assignment.append((0,0,0,0))
            if w_assignment[len(w_assignment) - 1][2] > last:
                last = w_assignment[len(w_assignment) - 1][2]
            if w_assignment[len(w_assignment) - 1][1] < first:
                first = w_assignment[len(w_assignment) - 1][1]
        return last - first

