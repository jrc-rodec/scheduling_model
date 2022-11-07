import random
import pygad

class Solver:
    pass

class GASolver(Solver):

    instance = None

    def __init__(self, encoding, durations, job_list, alternatives, env, orders):
        self.encoding = encoding
        self.durations = durations
        self.jobs = job_list
        #self.alternatives = alternatives
        self.env = env
        self.orders = orders
        self.assignments_best = []
        self.average_assignments = []
        GASolver.instance = self

    def initialize(self, earliest_slot : int = 0, last_slot : int = 0, population_size : int = 100, offspring_amount : int = 50, max_generations : int = 5000, crossover : str = 'two_points', selection : str = 'rws'):
        self.earliest_slot = earliest_slot
        self.last_slot = last_slot
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        self.max_generations = max_generations
        self.crossover_type = crossover
        self.parent_selection_type = selection
        #self.mutation_type = GASolver.mutation_function
        self.mutation_type = GASolver.alternative_mutation_function
        self.mutation_percentage_genes = 10 # not used, but necessary parameter
        self.gene_type = int
        self.keep_parents = int(self.population_size / 4) # TODO: add as parameter
        gene_space_workstations = {'low': 0, 'high': len(self.env.workstations)}
        gene_space_starttime = {'low': self.earliest_slot, 'high': self.last_slot}
        self.gene_space = []
        for i in range(0, len(self.encoding), 2):
            self.gene_space.append(gene_space_workstations)
            self.gene_space.append(gene_space_starttime)
        self.ga_instance = pygad.GA(num_generations=max_generations, num_parents_mating=int(self.population_size/2), fitness_func=GASolver.fitness_function, on_fitness=GASolver.on_fitness_assignemts, sol_per_pop=population_size, num_genes=len(self.encoding), init_range_low=self.earliest_slot, init_range_high=self.last_slot, parent_selection_type=self.parent_selection_type, keep_parents=self.keep_parents, crossover_type=self.crossover_type, mutation_type=self.mutation_type, mutation_percent_genes=self.mutation_percentage_genes, gene_type=self.gene_type, gene_space=self.gene_space)
        
        self.best_solution = None

    def run(self):
        self.ga_instance.run()
        solution, solution_fitness, solution_idx = self.ga_instance.best_solution()
        self.solution_index = solution_idx
        self.best_solution = (solution, solution_fitness)
        print("Done")

    def get_best(self):
        return self.best_solution[0]

    def get_best_fitness(self):
        return self.best_solution[1]

    def get_result_jobs(self):
        return self.jobs

    def mutation_function(offsprings, ga_instance):
        instance : GASolver = GASolver.instance
        index = 0
        for offspring in offsprings:
            p = 1 / (len(offspring)/2) # amount of jobs
            for i in range(0, len(offspring), 2):
                if random.random() < p:
                    #alternatives = instance.alternatives[int(i/2)]
                    # mutate workstation assignment
                    #alternative = random.choice(alternatives)
                    #instance.jobs[index][int(i/2)] = alternative
                    workstations = instance.env.get_all_workstations_for_task( instance.jobs[int(i/2)])
                    offspring[i] = random.choice(workstations).id
                    # mutate start time
                    offspring[i+1] = random.randint(instance.earliest_slot, instance.last_slot)
            index += 1
        return offsprings

    def alternative_mutation_function(offsprings, ga_isntance):
        instance = GASolver.instance
        for offspring in offsprings:
            prev_order = 0
            current_order = 0
            p = 1 / (len(offspring)/2)
            for i in range(0, len(offspring), 2):
                current_order = GASolver.get_order_index(i)
                if random.random() < p:
                    # adjust workstation
                    workstations = instance.env.get_all_workstations_for_task( instance.jobs[int(i/2)])
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

    def on_fitness_assignemts(ga_instance, population_fitness):
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

    def fitness_function(solution, solution_idx):
        fitness = 0
        if not GASolver.is_feasible(solution):
            #fitness += (2 * GASolver.instance.last_slot)
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

    def is_feasible(solution):
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
            order = GASolver.get_order(i) # find order corresponding to task
            if order:
                if not prev_order is None and order.id == prev_order.id: # if current task is not the first job of this order, check if the previous job ends before the current one starts
                    prev_start = solution[i-1]
                    prev_end = prev_start + instance.durations[instance.jobs[int(i/2) - 1]][solution[i-2]]
                    if solution[i+1] < prev_end:
                        return False
            else:
                print("Something went completely wrong!") # TODO: should probably throw exception
        return True

    def get_order(index):
        instance = GASolver.instance
        job_index = int(index/2)
        #job = instance.jobs[int(index/2)]
        sum = 0
        for order in instance.orders:
            recipe = instance.env.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            if job_index < sum + len(recipe.tasks):# >= job_index:
                return order
            sum += len(recipe.tasks)
        return instance.orders[len(instance.orders)-1]
    
    def get_order_index(index):
        instance = GASolver.instance
        job_index = int(index/2)
        #job = instance.jobs[int(index/2)]
        sum = 0
        index = 0
        for order in instance.orders:
            """if sum >= job_index:
                return index"""
            recipe = instance.env.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            if job_index < sum + len(recipe.tasks):# >= job_index:
                return index
            sum += len(recipe.tasks)
            index += 1
        return len(instance.orders) -1