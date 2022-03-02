import random
import copy

from models import SimulationEnvironment

class Optimizer:

    def __init__(self):
        pass

    def optimize(self, assignments, jobs, simulation_environment, last_timeslot):
        pass

class Randomizer(Optimizer):

    def __init__(self):
        super().__init__()
        self.name = "Randomizer"
    
    def optimize(self, assignments, jobs, simulation_environment, last_timeslot):
        for i in range(len(assignments)):
            job = jobs[i]
            assignment = assignments[i]
            workstations = simulation_environment.get_valid_workstations(job.task_id)
            if len(workstations) == 0:
                print(job.task_id)
            assignment[0] = workstations[random.randint(0, len(workstations) - 1)].external_id
            assignment[1] = random.randint(0, last_timeslot)
        return assignments

class Individual:

    def __init__(self, genes, fitness):
        self.genes = genes
        self.fitness = fitness
        self.feasible = False

    def set_gene(self, index, gene):
        self.genes[index] = gene
    
    def get_gene(self, index):
        return self.genes[index]
    
    def is_feasible(self, orders, recipes, last_slot):
        self.feasbile = False
        i = 0
        order_operations = dict()
        for gene in self.genes:
            operation, order = map_index_to_operation(i, orders, recipes)
            # check if gene should exist
            if operation == -1 or order == -1:
                return False
            duration = get_duration(gene[0], gene[1], operation, order[0], recipes)
            # check if combination is correct
            if duration == 0:
                return False
            # finish everything before the end of the planning horizon
            if gene[2] + duration > last_slot:
                return False
            i += 1
            data = copy.deepcopy(gene)
            if order[2] not in order_operations.keys():
                order_operations[order[2]] = []
            order_operations[order[2]].append(data)
        for order_id in order_operations.keys():
            order = get_by_id(orders, order_id)
            amount = len(get_all_tasks_for_recipe(recipes[order[0]]))
            # somehow an operation vanished
            if len(order_operations[order_id]) != amount:
                return False
            for j in range(len(order_operations[order_id])):
                if j > 0:
                    operation = order_operations[order_id][j]
                    prev = order_operations[order_id][j-1]
                    if operation[2] <= prev[2] + get_duration(prev[0], prev[1], j-1, order[0], recipes):
                        return False
        self.feasible = True
        return True

def get_all_tasks(task):
    all = []
    for pre in task.preceding_tasks:
        all += get_all_tasks(pre)
    all.append(task)
    for follow_up in task.follow_up_tasks:
        all += get_all_tasks(follow_up)
    return all

def get_all_tasks_for_recipe(recipe):
    tasks = recipe.tasks
    all = []
    for task in tasks:
        all += get_all_tasks(task)
    return all
    
def map_index_to_operation(index, orders, recipes):
    current = 0
    if index == 0:
        return 0, orders[0]
    for i in range(len(orders)):
        recipe = get_by_id(recipes, orders[i][0])
        tasks = get_all_tasks_for_recipe(recipe)
        for j in range(len(tasks)):
            if current == index:
                return j, orders[i]
            current += 1
    return None

def get_duration(task_id, workstation_id, workstations):
    workstation = get_by_id(workstations, workstation_id)
    for task in workstation.tasks:
        if task[0].external_id == task_id:
            return task[1]
    return 0

def get_by_id(entities, id):
    for entity in entities:
        if entity.external_id == id:
            return entity
    return None

class SimpleGA:
    
    def __init__(self, simulation_environment : SimulationEnvironment, dataset):
        self.current_best = Individual([], float('inf'))
        self.recipes = simulation_environment.recipes
        self.resources = simulation_environment.resources
        self.workstations = simulation_environment.workstations
        self.tasks = simulation_environment.tasks
        self.dataset = dataset # needed for some flexibility

    def randomize_gene(self, individual, index, operation_index, order):
        # new gene format <task_id, machine_id, start_time>
        tasks = get_all_tasks_for_recipe(self.recipes[order[0]])
        result_resource = tasks[operation_index].result_resources[0][0] # pick result resource 0 as default for now
        possible_tasks = []
        for task in self.tasks:
            if task.result_resources[0][0] == result_resource:
                possible_tasks.append(task)
        task = random.choice(tasks)
        workstations = []
        for workstation in self.workstations:
            if task in workstation.tasks:
                workstations.append(workstation)
        individual.genes[index][0] = task.external_id
        individual.genes[index][1] = random.choice(workstations).external_id
        individual.genes[index][2] = random.randint(self.earliest_slot, self.last_slot)

    def randomize_individual(self, individual):
        for i in range(len(individual.genes)):
            operation_index, order = map_index_to_operation()
            self.randomize_gene(individual, i, operation_index, order)

    def evaluate(self, individuals):
        for individual in individuals:
            # calc fitness
            individual.fitness = 0
            for i in range(len(individual.genes)):
                operation_id, order = map_index_to_operation(i, self.orders, self.recipes)
                if not order == -1:
                    delivery_date = order[1]
                    duration = self.get_duration(individual.genes[i][0], individual.genes[i][1])
                    if individual.genes[i][2] + duration > delivery_date: # counts all late operations, not just late order once
                        individual.fitness += 1
            if not individual.is_feasible(self.orders, self.recipes, self.last_slot):
                individual.fitness += len(individual.genes)

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
        parent1 = self.select(parents)
        parent2 = self.select(parents)
        while parent1 == parent2: # making sure 2 different parents are selected
            parent2 = self.select(parents)
        # simple one point crossover for testing
        crossover_point = random.randint(0, len(parent1.genes))
        child1 = Individual(copy.deepcopy(parent1.genes), float('inf'))
        child2 = Individual(copy.deepcopy(parent2.genes), float('inf'))
        for i in range(crossover_point, len(parent1.genes)):
            child1.set_gene(i, parent2.get_gene(i))
            child2.set_gene(i, parent1.get_gene(i))
        return child1, child2

    def run(self, input, orders, max_generations, population_size, offspring_amount, earliest_slot, last_slot):
        population = []
        offsprings =  []
        self.earliest_slot = earliest_slot
        self.last_slot = last_slot
        self.orders = orders
        self.last_slot = last_slot
        history = []
        avg_history = []
        best_generation_history = []
        for i in range(population_size):
            individual = input.copy()
            x = Individual(individual, float('inf'))
            self.randomize_individual(x)
            population.append(x)
        self.evaluate(population)
        self.current_best = random.choice(population)
        # return self.current_best, history
        fitness = 0
        for parent in population:
            fitness += parent.fitness
            if parent.fitness < self.current_best.fitness:
                self.current_best = parent
        history.append(self.current_best.fitness)
        avg_history.append(fitness / len(population))
        best_generation_history.append(self.current_best.fitness)
        p = 1 / len(input)
        gen = 0
        feasible = self.current_best.feasible
        feasible_gen = max_generations
        while gen < max_generations and self.current_best.fitness > 0:
            if feasible:
                print(f'Current generation: {gen}, Current Best: {self.current_best.fitness}')
            else:
                print(f'Current generation: {gen}, Current Best: {self.current_best.fitness}, not feasible')
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
                        operation_id, order = map_index_to_operation(i, orders, self.recipes)
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
            history.append(self.current_best.fitness)
            best_generation_history.append(population[0].fitness)
            fitness = 0
            for individual in population:
                fitness += individual.fitness
            avg_history.append(fitness / len(population))
            if not feasible and self.current_best.feasible:
                feasible_gen = gen
                feasible = True
            gen += 1
        return self.current_best, history, avg_history, best_generation_history, feasible_gen