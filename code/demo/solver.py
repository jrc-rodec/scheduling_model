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
        self.alternatives = alternatives
        self.env = env
        self.orders = orders
        GASolver.instance = self

    def initialize(self, earliest_slot : int = 0, last_slot : int = 0, population_size : int = 100, offspring_amount : int = 50, max_generations : int = 5000):
        jobs = []
        for _ in range(population_size):
            jobs.append(self.jobs)
        self.jobs = jobs
        self.earliest_slot = earliest_slot
        self.last_slot = last_slot
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        self.max_generations = max_generations
        self.crossover_type = 'two_points'
        self.parent_selection_type = 'rws'
        self.mutation_type = GASolver.mutation_function
        self.mutation_percentage_genes = 10 # not used, but necessary parameter
        self.gene_type = int
        self.keep_parents = int(self.population_size / 4) # TODO: add as parameter
        gene_space_workstations = {'low': 0, 'high': len(self.env.workstations)}
        gene_space_starttime = {'low': self.earliest_slot, 'high': self.last_slot}
        self.gene_space = []
        for i in range(0, len(self.encoding), 2):
            self.gene_space.append(gene_space_workstations)
            self.gene_space.append(gene_space_starttime)
        self.ga_instance = pygad.GA(num_generations=max_generations, num_parents_mating=int(self.population_size/2), fitness_func=GASolver.fitness_function, sol_per_pop=population_size, num_genes=len(self.encoding), init_range_low=self.earliest_slot, init_range_high=self.last_slot, parent_selection_type=self.parent_selection_type, keep_parents=self.keep_parents, crossover_type=self.crossover_type, mutation_type=self.mutation_type, mutation_percent_genes=self.mutation_percentage_genes, gene_type=self.gene_type, gene_space=self.gene_space)
        
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
        return self.jobs[self.solution_index]

    def mutation_function(offsprings, ga_instance):
        instance : GASolver = GASolver.instance
        index = 0
        for offspring in offsprings:
            p = 1 / (len(offspring)/2) # amount of jobs
            for i in range(0, len(offspring), 2):
                if random.random() < p:
                    alternatives = instance.alternatives[int(i/2)]
                    # mutate workstation assignment
                    alternative = random.choice(alternatives)
                    instance.jobs[index][int(i/2)] = alternative
                    workstations = instance.env.get_all_workstations_for_task(alternative)
                    offspring[i] = random.choice(workstations).id
                    # mutate start time
                    offspring[i+1] = random.randint(instance.earliest_slot, instance.last_slot)
            index += 1
        return offsprings

    def fitness_function(solution, solution_idx):
        fitness = 0
        if not GASolver.is_feasible(solution, solution_idx):
            fitness += (2 * GASolver.instance.last_slot)
        # use makespan for now
        min = float('inf')
        max = -float('inf')
        for i in range(1, len(solution), 2): # go through all start times
            if solution[i] < min:
                min = solution[i]
            task = GASolver.instance.jobs[solution_idx][int((i-1) / 2)]
            if solution[i] + GASolver.instance.durations[task][solution[i-1]] > max:
                max = solution[i] + GASolver.instance.durations[task][solution[i-1]]
        fitness += abs(max - min)
        return -fitness # NOTE: PyGAD always maximizes

    def is_feasible(solution, index):
        order = None
        instance : GASolver = GASolver.instance
        for i in range(0, len(solution), 2): # go through all workstation assignments
            job = instance.jobs[index][int(i/2)]
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
                        other_job = instance.jobs[index][int(j/2)]
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
                    prev_end = prev_start + instance.durations[instance.jobs[index][int(i/2) - 1]][solution[i-2]]
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
            if sum >= job_index:
                return order
            recipe = instance.env.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
            sum += len(recipe.tasks)
        return None
    