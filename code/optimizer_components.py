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
"""
    Note: following are the implementations of different optimizer components.
    Important: function interfaces have to be the same for each type (e.g. every
    Evaluation Method needs to have the function interface <def evaluate(self, individuals, orders)>)
"""
# Evaluation Methods
class EvaluationMethod:

    def evaluate(self, individuals, orders):
        pass
###############################################
# Example for Evaluation Method Implementation#
###############################################
class TardinessEvaluator(EvaluationMethod):

    def evalute(self, individuals, orders):
        for individual in individuals:
            fitness = 0
            if not individual.is_feasible:
                fitness += len(individual.genes)
            for i in range(len(individual.genes)):
                _, order = map_index_to_operation(i, orders, self.recipes)
                duration = get_duration(individual.genes[i][0], individual.genes[i][1], self.workstations)
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
            child1.set_gene(i, parent2.get_gene(i))
            child2.set_gene(i, parent1.get_gene(i))
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

    def mutate_gene(self, individual, index):
        pass

    def mutate(self, individuals, orders, recipes):
        pass
#############################################
# Example for Mutation Method Implementation#
#############################################
class RandomizeMutation(MutationMethod):

    def mutate_gene(self, individual, index):
        # new gene format <task_id, machine_id, start_time>
        operation_index, order = map_index_to_operation(index, self.orders, self.recipes)
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

    def mutate(self, individuals, orders, recipes):
        for individual in individuals:
            p = 1 / len(individual.genes())
            for i in range(len(individual.genes)):
                if random.uniform(0, 1) < p:
                    self.mutate_gene(individual, i)


# Helper methods
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

def get_all_workstations_for_task(workstations, task_id):
    result = []
    for workstation in workstations:
        for task in workstation.tasks:
            if task.external_id == task_id:
                result.append(workstation)
                break
    return result

# Input Generators
class InputGenerator:

    def generate_input(self, orders, earliest_time_slot, last_time_slot):
        pass

class BaseInputGenerator(InputGenerator):

    def generate_input(self, orders, earliest_time_slot, last_time_slot):
        input = []
        for order in orders:
            recipe_id = order[0]
            recipe = get_by_id(self.recipes, recipe_id)
            all_tasks = get_all_tasks_for_recipe(recipe)
            for task in all_tasks:
                workstations = get_all_workstations_for_task(task.external_id)
                input.append([task.external_id, random.choice(workstations).external_id, random.randint(earliest_time_slot, last_time_slot)])
        return None