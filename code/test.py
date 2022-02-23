from external_test_data.read_data import read_dataset_1
import random

#from visualize import visualize
def get_amount_operations_for_job(index : int, jobs) -> int:
    return len(jobs[index])

def get_duration(machine_id : int, worker_id : int, operation_index : int, job_index : int, jobs, show_combination : bool = False):
    #for combinations in jobs[job_index][operation_index]:
    combinations = get_combinations_for_operation(operation_index, job_index, jobs)
    if show_combination:
        print(f'Checking for duration in {combinations}, looking for {machine_id}, {worker_id}')
    for combination in combinations:
        if combination[0] == machine_id and combination[1] == worker_id:
            return combination[2]
    # print(f'Did not find duration for {machine_id}, {worker_id}, in combinations {jobs[job_index][operation_index]} for operation {operation_index} in job {job_index} :(')
    return 0

def map_index_to_operation(index, orders, jobs):
    current = 0
    # operation_amount = 0
    if index == 0:
        return 0, orders[0]
    while current < index:
        for order in orders:
            operation_amount = get_amount_operations_for_job(order[0], jobs)
            if current + operation_amount > index:
                # found correct order
                operation_id = current + operation_amount - index
                # found the id of the operation inside the job
                return operation_id - 1, order
            current += operation_amount
    return -1, -1

def get_combinations_for_operation(operation, job, jobs):
    combinations = []
    for machine_combinations in jobs[job][operation]:
        for combination in machine_combinations:
            combinations.append(combination)
    return combinations

class Individual:

    def __init__(self, genes, fitness):
        self.genes = genes
        self.fitness = fitness

    def set_gene(self, index, gene):
        self.genes[index] = gene
    
    def get_gene(self, index):
        return self.genes[index]
    
    def is_feasible(self, orders, jobs):
        i = 0
        for gene in self.genes:
            operation, order = map_index_to_operation(i, orders, jobs)
            if operation == -1 or order == -1:
                return False
            if get_duration(gene[0], gene[1], operation, order[0], jobs) == 0:
                return False
            i += 1
        return True

class SimpleGA:
    
    def __init__(self):
        self.current_best = Individual([], float('inf'))

    def randomize_gene(self, individual, index, operation_id, order):
        combinations = get_combinations_for_operation(operation_id, order[0], self.jobs)
        #print(f'Choosing from {combinations}')
        combination = random.choice(combinations)
        individual.genes[index][0] = combination[0]
        individual.genes[index][1] = combination[1]
        #individual.genes[index][0] = random.choice(get_available_machines_for_operation(operation_id, order[0], self.jobs))
        #individual.genes[index][1] = random.choice(get_available_worker_for_machine_for_operation(individual.genes[index][0], operation_id, order[0], self.jobs))
        individual.genes[index][2] = random.randint(self.earliest_slot, self.last_slot)
        #return individual

    def randomize_individual(self, individual, orders, jobs):
            j = 0
            for order in orders:
                operations = get_amount_operations_for_job(order[0], jobs)
                for k in range(operations):
                    self.randomize_gene(individual, j, k, order)
                    j+=1
            #return individual

    def evaluate(self, individuals):
        for individual in individuals:
            # calc fitness
            individual.fitness = 0
            for i in range(len(individual.genes)):
                operation_id, order = map_index_to_operation(i, self.orders, self.jobs)
                # order = self.orders[order_id]
                if not order == -1:
                    delivery_date = order[1]
                    duration = get_duration(individual.genes[i][0], individual.genes[i][1], operation_id, order[0], self.jobs)
                    if individual.genes[i][2] + duration > delivery_date: # counts all late operations, not just late order once
                        individual.fitness += 1
            if not individual.is_feasible(self.orders, self.jobs):
                individual.fitness += 300

    def tournament_selection(self, population):
        parents = random.choices(population, k=5)
        best = parents[0]
        for parent in parents:
            if parent.fitness < best.fitness:
                best = parent
        return best

    def roulette_wheel_selection(self, population):
        sum = 0
        max = 0
        min = float('inf')
        for individual in population:
            sum += individual.fitness
            if individual.fitness > max:
                max = individual.fitness
            if individual.fitness < min:
                min = individual.fitness
        p = random.random() * sum
        t = max + min
        # parent = random.choice(population)
        parent = population[0]
        for individual in population:
            p -= (t - individual.fitness)
            if p < 0:
                return individual
        return parent

    def select(self, population):
        return self.roulette_wheel_selection(population)

    def crossover(self, parents):
        # select parents (just random for now)
        #parent1 = random.choice(parents)
        #parent2 = random.choice(parents)
        #parent1, parent2 = self.select(parents)
        parent1 = self.select(parents)
        parent2 = self.select(parents)
        while parent1 == parent2: # making sure 2 different parents are selected
            #parent2 = random.choice(parents)
            parent2 = self.select(parents)
        # simple one point crossover for testing
        crossover_point = random.randint(0, len(parent1.genes))
        child1 = Individual(parent1.genes.copy(), float('inf'))
        child2 = Individual(parent2.genes.copy(), float('inf'))
        for i in range(crossover_point, len(parent1.genes)):
            child1.set_gene(i, parent2.get_gene(i))
            child2.set_gene(i, parent1.get_gene(i))
        return child1, child2

    def run(self, input, orders, system_info, jobs, max_generations, population_size, offspring_amount, earliest_slot, last_slot):
        population = []
        offsprings =  []
        self.earliest_slot = earliest_slot
        self.last_slot = last_slot
        self.orders = orders
        self.jobs = jobs
        for i in range(population_size):
            individual = input.copy()
            x = Individual(individual, float('inf'))
            self.randomize_individual(x, orders, jobs)
            population.append(x)
        self.evaluate(population)
        self.current_best = random.choice(population)
        for parent in population:
            if parent.fitness < self.current_best.fitness:
                self.current_best = parent
        p = 1 / len(input)
        gen = 0
        while gen < max_generations and self.current_best.fitness > 0:
            print(f'Current generation: {gen}, Current Best: {self.current_best.fitness}')
            # create offsprings
            offsprings = []
            # crossover
            i = 0
            while i < offspring_amount:
                offspring1, offspring2 = self.crossover(population)
                offsprings.append(offspring1)
                i+=1
                if len(offsprings) + 1 < offspring_amount:
                    offsprings.append(offspring2) # discard offspring 2 if too many offsprings were created
                    i += 1
            # mutate
            for offspring in offsprings:
                i = 0
                for i in range(len(offspring.genes)):
                    if random.uniform(0, 1) < p:
                        operation_id, order = map_index_to_operation(i, orders, jobs)
                        self.randomize_gene(offspring, i, operation_id, order)
                    i += 1
            # evaluate
            self.evaluate(offsprings)
            # select new population
            all = population + offsprings # use elitism
            all.sort(key=lambda x: x.fitness)
            population = all[0:population_size]
            if population[0].fitness < self.current_best.fitness:
                self.current_best = population[0]
            # random.shuffle(population)
            gen += 1
        return self.current_best

def print_instance(instance):
    print(f'System Information:')
    system_info = instance[0]
    print(f'There should be {system_info[0]} jobs, {system_info[1]} machines, and {system_info[2]} workers in the system')
    jobs = instance[1]
    print(f'Found {len(jobs)} different jobs')
    i = 0
    for job in jobs:
        print(f'Job {i} has {len(job)} operations')
        j = 0
        for operation in job:
            print(f'Operation {j} in Job {i} has {len(operation)} possible combinations')
            j += 1
        i += 1

# input structure:
# for each order
#   for each operation necessary for job from order
#       (<machine id> <worker id> <start time>)
# feasible if
#   machine m + worker w is an available option for operation n
#   operation n+1 starttime > operation n starttime + operation n duration using machine m and worker w
#   startime + duration of machine m with worker w for operation n < order o delivery date
#   no overlap of timeslots for each machine and each worker
# in the given dataset, all jobs seem to always have exactly the same amount of operations necessary
earliest_slot = 100
last_slot = 1000
input, orders, instance = read_dataset_1(use_instance=13, earliest_time=earliest_slot, planning_horizon=last_slot)
# print(orders)
system_info = instance[0]
jobs = instance[1]
n_jobs = system_info[0]
n_machines = system_info[1]
n_workers = system_info[2]
# print_instance(instance)
# ready to start optimization
print(f'{len(input)} operations need to be scheduled to {n_machines} machines with {n_workers} workers!')
ga = SimpleGA()
result = ga.run(input, orders, system_info, jobs, 100, 50, 100, earliest_slot, last_slot)
print(f'Finished with fitness: {result.fitness}!')
result.genes.sort(key=lambda x: x[2]) # sort all operations by start time (ascending)
#for operation in result.genes:
#    print(operation)
# sort operations to machines, ignore worker for now
workstations = dict()
i = 0
for operation in result.genes:
    if operation[0] not in workstations:
        workstations[operation[0]] = []
    operation_id, order = map_index_to_operation(i, orders, jobs)
    #print(f'Looking for duration for machine {operation[0]} and worker {operation[1]} in operation {operation_id} in job {order[0]}')
    workstations[operation[0]].append([order[2], order[0], operation_id, operation[1], operation[2], get_duration(operation[0], operation[1], operation_id, order[0], jobs)]) # job id, start_time, duration
    i+=1
sum = 0
keys = list(workstations.keys())
keys.sort()

for workstation in keys:
    print(f'Workstation w{workstation} has {len(workstations[workstation])} operations scheduled: <order_id, job_index, operation_index, worker_index, start_time, duration>')
    print(workstations[workstation])
    print('\n')
    sum += len(workstations[workstation])
print(f'For a total of {sum} scheduled operations!')
from visualize import visualize
visualize(workstations)
"""for j in range(len(jobs)):
    for i in range(len(jobs[j])):
        print(f'Operation {i} in Job {j}: {jobs[j][i]}')"""