import random
import copy

class Individual:

    def __init__(self, genes, fitness):
        self.genes = genes
        self.fitness = fitness
        self.feasible = False

    def set_gene(self, index, gene):
        self.genes[index] = gene
    
    def get_gene(self, index):
        return self.genes[index]
    
    def is_feasible(self, orders, environment, earliest_slot, last_slot):
        self.feasbile = False
        i = 0
        order_operations = dict()
        for gene in self.genes:
            operation, order = map_index_to_operation(i, orders, environment)
            # check if gene should exist
            if operation == -1 or order == -1:
                return False
            duration = environment.get_duration(gene[0], gene[1])
            # check if combination is correct
            if duration == 0:
                return False
            # finish everything before the end of the planning horizon
            #if gene[2] + duration > last_slot:
            #    return False
            if gene[2] < earliest_slot:
                return False
            i += 1
            data = copy.deepcopy(gene)
            if order[2] not in order_operations.keys():
                order_operations[order[2]] = []
            order_operations[order[2]].append(data)
        for order_id in order_operations.keys():
            order = None
            for order in orders:
                if order[2] == order_id:
                    order = order
                    break
            amount = len(environment.recipes[order[0]].tasks)
            # somehow an operation vanished
            if len(order_operations[order_id]) != amount:
                return False
            for j in range(len(order_operations[order_id])):
                if j > 0:
                    operation = order_operations[order_id][j]
                    prev = order_operations[order_id][j-1]
                    if operation[2] <= prev[2] + environment.get_duration(prev[0], prev[1]):
                        return False
        self.feasible = True
        return True

class Particle:

    def __init__(self, individual : Individual):
        self.individual = individual
        self.best_genes = []
        self.best_fitness = float('inf')
        self.veclocities = []
        self.feasible = False
        for i in range(len(self.individual.genes)):
            self.veclocities = 0
            self.best_genes.append(copy.deepcoy(self.individual.genes[i]))
"""
    Note: following are the implementations of different optimizer components.
    Important: function interfaces have to be the same for each type (e.g. every
    Recombination Method needs to have the function interface <def recombine(self, parent1, parent2)>)
"""
# Evaluation Methods
class EvaluationMethod:

    def evaluate(self, individuals, orders, environment, earliest_slot, last_slot):
        pass
###############################################
# Example for Evaluation Method Implementation#
###############################################
class TardinessEvaluator(EvaluationMethod):

    def evaluate(self, individuals, orders, environment, earliest_slot, last_slot):
        for individual in individuals:
            fitness = 0
            if not individual.is_feasible(orders, environment, earliest_slot, last_slot):
                fitness += len(individual.genes)
            for i in range(len(individual.genes)):
                _, order = map_index_to_operation(i, orders, environment)
                duration = environment.get_duration(individual.genes[i][0], individual.genes[i][1])
                if individual.genes[i][2] + duration > order[1]:
                    fitness += 1 # counts every OPERATIONS after deadline
            individual.fitness = fitness

# Recombination Methods
class RecombinationMethod:

    def recombine(self, parent1, parent2):
        pass
##################################################
# Example for Recombination Method Implementation#
##################################################
class OnePointCrossover(RecombinationMethod):

    def recombine(self, parent1, parent2):
        crossover_point = random.randint(0, len(parent1.genes))
        child1 = Individual(copy.deepcopy(parent1.genes), float('inf'))
        child2 = Individual(copy.deepcopy(parent2.genes), float('inf'))
        for i in range(crossover_point, len(parent1.genes)):
            child1.set_gene(i, copy.deepcopy(parent2.get_gene(i)))
            child2.set_gene(i, copy.deepcopy(parent1.get_gene(i)))
        return child1, child2

class TwoPointCroosover(RecombinationMethod):

    def recombine(self, parent1, parent2):
        crossover_point1 = random.randint(0, len(parent1.genes) - 1) # -1 to make sure there can be a second point
        crossover_point2 = random.randint(crossover_point1 + 1, len(parent1.genes))
        child1 = Individual(copy.deepcopy(parent1.genes), float('inf'))
        child2 = Individual(copy.deepcopy(parent2.genes), float('inf'))
        for i in range(crossover_point1, crossover_point2):
            child1.set_gene(i, copy.deepcopy(parent2.get_gene(i)))
            child2.set_gene(i, copy.deepcopy(parent1.get_gene(i)))
        return child1, child2

# Selection Methods
class SelectionMethod:

    def select(self, population, minimize=True):
        pass
##############################################
# Example for Selection Method Implementation#
##############################################
class RouletteWheelSelection(SelectionMethod):

    def select(self, population, minimize=True):
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
        parent = population[0]
        for individual in population:
            if minimize:
                p -= (t - individual.fitness)
            else:
                p -= individual.fitness
            if p < 0:
                return individual
        return parent

# Mutation Methods
class MutationMethod:

    def mutate_gene(self, individual, orders, environment, index, earliest_slot, last_slot):
        pass

    def mutate(self, individuals, orders, environment, earliest_slot, last_slot):
        pass
#############################################
# Example for Mutation Method Implementation#
#############################################
class RandomizeMutation(MutationMethod):

    def mutate_gene(self, individual, orders, environment, index, earliest_slot, last_slot):
        # new gene format <task_id, machine_id, start_time>
        operation_index, order = map_index_to_operation(index, orders, environment)
        tasks = environment.recipes[order[0]].tasks#environment.get_all_tasks_for_recipe(environment.recipes[order[0]].external_id)#environment.recipes[order[0]].tasks#get_all_tasks_for_recipe(recipes[order[0]], tasks)
        result_resource = tasks[operation_index].result_resources[0][0] # pick result resource 0 as default for now
        possible_tasks = []
        for task in tasks:
            if task.result_resources[0][0] == result_resource:
                possible_tasks.append(task)
        task = random.choice(tasks)
        workstation_list = []
        for workstation in environment.workstations:
            for w_task in workstation.tasks:
                if w_task[0] == task.external_id:
                    workstation_list.append(workstation)
        individual.genes[index][0] = task.external_id
        individual.genes[index][1] = random.choice(workstation_list).external_id
        individual.genes[index][2] = random.randint(earliest_slot, last_slot)

    def mutate(self, individuals, orders, environment, earliest_slot, last_slot):
        for individual in individuals:
            p = 1 / len(individual.genes)
            for i in range(len(individual.genes)):
                if random.uniform(0, 1) < p:
                    self.mutate_gene(individual, orders, environment, i, earliest_slot, last_slot)

class OnlyFeasibleTimeSlotMutation(MutationMethod):

    def mutate_gene(self, individual, orders, environment, index, earliest_slot, last_slot):
        # new gene format <task_id, machine_id, start_time>
        operation_index, order = map_index_to_operation(index, orders, environment)
        tasks = environment.recipes[order[0]].tasks#environment.get_all_tasks_for_recipe(orders[0])#environment.recipes[order[0]].tasks#get_all_tasks_for_recipe(recipes[order[0]], tasks)
        result_resource = tasks[operation_index].result_resources[0][0] # pick result resource 0 as default for now
        possible_tasks = []
        for task in tasks:
            if task.result_resources[0][0] == result_resource:
                possible_tasks.append(task)
        task = random.choice(tasks)
        workstation_list = []
        for workstation in environment.workstations:
            for w_task in workstation.tasks:
                if w_task[0] == task.external_id:
                    workstation_list.append(workstation)
        individual.genes[index][0] = task.external_id
        individual.genes[index][1] = random.choice(workstation_list).external_id
        duration = environment.get_duration(individual.genes[index][0], individual.genes[index][1])
        ub = order[1] - duration
        lb = earliest_slot
        if ub < lb:
            ub = earliest_slot
            lb = order[1] - duration
        individual.genes[index][2] = random.randint(lb, ub)

    def mutate(self, individuals, orders, environment, earliest_slot, last_slot):
        for individual in individuals:
            p = 1 / len(individual.genes)
            for i in range(len(individual.genes)):
                if random.uniform(0, 1) < p:
                    self.mutate_gene(individual, orders, environment, i, earliest_slot, last_slot)

# Helper methods
def map_index_to_operation(index, orders, environment):
    current = 0
    if index == 0:
        return 0, orders[0]
    for i in range(len(orders)):
        recipe = get_by_id(environment.recipes, orders[i][0])
        tasks = recipe.tasks#environment.get_all_tasks_for_recipe(recipe.external_id)#recipe.tasks #get_all_tasks_for_recipe
        for j in range(len(tasks)):
            if current == index:
                return j, orders[i]
            current += 1
    return None

def get_by_id(entities, id):
    for entity in entities:
        if entity.external_id == id:
            return entity
    print(f'couldn\'t find {id} in {len(entities)} entities')
    return None

"""
def get_all_tasks(task, task_list):
    all = []
    if isinstance(task, int):
        task = get_by_id(task_list, task)
    for pre in task.preceding_tasks:
        all += get_all_tasks(pre, task_list)
    all.append(task)
    for follow_up in task.follow_up_tasks:
        all += get_all_tasks(follow_up, task_list)
    return all

def get_all_tasks_for_recipe(recipe, task_list):
    tasks = recipe.tasks
    # print(f'checking recipe: {recipe.name}')
    all = []
    for task in tasks:
        all += get_all_tasks(task, task_list)
    return all
"""

# Input Generators
class InputGenerator:

    def generate_input(self, orders, environment, earliest_time_slot, last_time_slot):
        pass

class BaseInputGenerator(InputGenerator):

    def generate_input(self, orders, environment, earliest_time_slot, last_time_slot):
        input = []
        for order in orders:
            recipe_id = order[0]
            recipe = environment.get_recipe(recipe_id)
            all_tasks = recipe.tasks#environment.get_all_tasks_for_recipe(recipe.external_id)#recipe.tasks # get_all_tasks_for_recipe -> depends on how it the task lists are supposed to be used
            for task in all_tasks:
                workstation_list = environment.get_valid_workstations(task.external_id)
                input.append([task.external_id, random.choice(workstation_list).external_id, random.randint(earliest_time_slot, last_time_slot)])
        return input

class SameLengthAlternativesInputGenerator(InputGenerator):

    def generate_input(self, orders, environment, earliest_time_slot, last_time_slot):
        input = []
        for order in orders:
            recipe_id = order[0]
            recipe = environment.get_recipe(recipe_id)
            all_tasks = recipe.tasks#environment.get_all_tasks_for_recipe(recipe.external_id)#recipe.tasks # get_all_tasks_for_recipe
            task = random.choice(all_tasks)
            workstation_list = environment.get_valid_workstations(task.external_id)
            input.append([task.external_id, random.choice(workstation_list).external_id, random.randint(earliest_time_slot, last_time_slot)])
            if len(task.follow_up_tasks) > 0:
                follow_up = random.choice(task.follow_up_tasks)
                workstation_list = environment.get_valid_workstations(follow_up)
                input.append([follow_up, random.choice(workstation_list).external_id, random.randint(earliest_time_slot, last_time_slot)])
            """for follow_up in task.follow_up_tasks:
                workstation_list = get_all_workstations_for_task(workstations, follow_up.external_id, tasks)
                input.append([follow_up.external_id, random.choice(workstation_list).external_id, random.randint(earliest_time_slot, last_time_slot)])"""
        return input