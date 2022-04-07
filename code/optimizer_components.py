import random
import copy

from agent import AgentSimulator, Agent

class Individual:

    def __init__(self, genes, fitness):
        self.genes = genes
        self.fitness = fitness
        self.feasible = False

    def set_gene(self, index, gene):
        self.genes[index] = copy.deepcopy(gene)
    
    def get_gene(self, index):
        return copy.deepcopy(self.genes[index])
    
    def is_feasible(self, orders, environment, earliest_slot, last_slot):
        pass

class ScheduleIndividual(Individual):
    
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
            if gene[2] + duration > last_slot:
                return False
            # no operation scheduled before the earliest allowed time slot
            if gene[2] < earliest_slot:
                return False
            data = copy.deepcopy(gene)
            if order[2] not in order_operations.keys():
                order_operations[order[2]] = []
            order_operations[order[2]].append(data)
            i += 1
            workstations = dict()
            # map genes to workstations
            if gene[1] not in workstations:
                workstations[gene[1]] = []
            workstations[gene[1]].append(copy.deepcopy(gene))
            # check for overlap
            for key in workstations.keys():
                workstations[key].sort(key=lambda x: x[2]) # sort by start time slot
                for o in range(len(workstations[key])):
                    op = workstations[key][o]
                    duration = environment.get_duration(op[0], op[1])
                    start = op[2]
                    end = op[2] + duration
                    # fetch necessary data
                    prev_start = earliest_slot
                    prev_end = earliest_slot
                    if o > 0:
                        prev_start = workstations[key][o-1][2]
                        prev_end = prev_start + environment.get_duration(workstations[key][o-1][0], workstations[key][o-1][1])
                    follow_start = last_slot
                    follow_end = last_slot
                    if o < len(workstations[key]) - 1:
                        follow_start = workstations[key][o+1][2]
                        follow_end = follow_start + environment.get_duration(workstations[key][o-1][0], workstations[key][o-1][1])
                    # check overlap with previous
                    if start > prev_start and start < prev_end:
                        return False
                    if end > prev_start and end < prev_end:
                        return False
                    if prev_start > start and prev_start < end and prev_end > start and prev_end < end:
                        return False
                    # check overlap with following
                    if start > follow_start and start < follow_end:
                        return False
                    if end > follow_start and end < follow_end:
                        return False
                    if follow_start > start and follow_start < end and follow_end > start and follow_end < end:
                        return False
        for order_id in order_operations.keys():
            # check for correct sequence
            for j in range(len(order_operations[order_id])):
                #if j > 0:
                operation = order_operations[order_id][j]
                prev = order_operations[order_id][j-1]
                if operation[2] <= prev[2] + environment.get_duration(prev[0], prev[1]):
                    return False
        self.feasible = True
        return self.feasible


class AgentIndividual(Individual):
    
    def is_feasible(self, orders, environment, earliest_slot, last_slot):
        self.feasible = True
        return self.feasible


class VLCIndividual(Individual):

    def __init__(self, genes, fitness):
        self.unscheduled_orders = []
        super().__init__(genes, fitness)

    def is_feasible(self, orders, environment, earliest_slot, last_slot):
        return True # TODO: write feasibility function

class TimeSlotIndividual(Individual):

    def is_feasible(self, orders, environment, earliest_slot, last_slot):
        return True # TODO: write feasibility function


class IndividualFactory:

    def __init__(self, minimize = True):
        self.minimize = minimize

    def create_individual(self, type : str, genes):
        fitness = float('inf')
        if not self.minimize:
            fitness = 0
        if type == 'schedule':
            return ScheduleIndividual(genes, fitness)
        elif type == 'agent':
            return AgentIndividual(genes, fitness)
        elif type == 'vlc':
            return VLCIndividual(genes, fitness)
        elif type == 'timeslot':
            return TimeSlotIndividual(genes, fitness)


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


class OrderCountEvaluator(EvaluationMethod):
    
    def set_simulator(self, simulator : AgentSimulator):
        self.simulator = simulator
    
    def set_agent(self, agent : Agent):
        self.agent = agent

    def evaluate(self, individuals, orders, environment, earliest_slot, last_slot):
        for individual in individuals:
            _, schedule_count = self.simulator.simulate(self.agent, individual.genes)
            individual.fitness = schedule_count
            individual.is_feasible(orders, environment, earliest_slot, last_slot)
            if not individual.feasible:
                individual.fitness = individual.fitness + len(orders)


"""class MakeSpanEvaluator(EvaluationMethod):
    
    def evaluate(self, individuals, orders, environment, earliest_slot, last_slot):
        for individual in individuals:
            fitness = 0
            # check for feasibility
            if not individual.is_feasible(orders, environment, earliest_slot, last_slot):
                fitness += len(individual.genes)
            # evaluate genes"""


# Recombination Methods
class RecombinationMethod:

    def __init__(self, environment, orders = None):
        self.environment = environment
        self.orders = orders

    def set_individual_factory(self, individual_factory : IndividualFactory, type : str):
        self.individual_factory = individual_factory
        self.type = type

    def recombine(self, parent1, parent2):
        pass
##################################################
# Example for Recombination Method Implementation#
##################################################
class OnePointCrossover(RecombinationMethod):

    def recombine(self, parent1, parent2):
        crossover_point = random.randint(0, len(parent1.genes))
        child1 = self.individual_factory.create_individual(self.type, copy.deepcopy(parent1.genes))
        child2 = self.individual_factory.create_individual(self.type, copy.deepcopy(parent2.genes))
        for i in range(crossover_point, len(parent1.genes)):
            child1.set_gene(i, copy.deepcopy(parent2.get_gene(i)))
            child2.set_gene(i, copy.deepcopy(parent1.get_gene(i)))
        return child1, child2

class TwoPointCroosover(RecombinationMethod):

    def recombine(self, parent1, parent2):
        crossover_point1 = random.randint(0, len(parent1.genes) - 1) # -1 to make sure there can be a second point
        crossover_point2 = random.randint(crossover_point1 + 1, len(parent1.genes))
        child1 = self.individual_factory.create_individual(self.type, copy.deepcopy(parent1.genes))
        child2 = self.individual_factory.create_individual(self.type, copy.deepcopy(parent2.genes))
        for i in range(crossover_point1, crossover_point2):
            child1.set_gene(i, copy.deepcopy(parent2.get_gene(i)))
            child2.set_gene(i, copy.deepcopy(parent1.get_gene(i)))
        return child1, child2

class NoCrossover(RecombinationMethod):

    def recombine(self, parent1, parent2):
        return copy.deepcopy(parent1), copy.deepcopy(parent2)


class VLCCrossover(RecombinationMethod):
    
    def __init__(self, environment, orders = None, minimize=True):
        self.individual_factory = IndividualFactory(minimize)
        self.type = "vlc"
    
    def set_individual_factory(self, individual_factory : IndividualFactory, type : str):
        print(f'IndividualFactory for VLC-Crossover is fixed and should not be changed')

    def recombine(self, parent1, parent2):
        p1 = copy.deepcopy(parent1)
        p2 = copy.deepcopy(parent2)
        # change list of genes into list of orders
        p1_orders = to_order_list(p1, self.orders, self.environment)
        p2_orders = to_order_list(p2, self.orders, self.environment)
        # recombine on order basis
        unscheduled_orders = []
        for order in p1.unscheduled_orders:
            if order not in unscheduled_orders:
                unscheduled_orders.append(order)
        for order in p2.unscheduled_orders:
            if order not in unscheduled_orders:
                unscheduled_orders.append(order)
        c_unscheduled_orders = copy.deepcopy(unscheduled_orders)
        c_genes = []
        c_orders = []
        # uniform crossover (including distinct orders)
        shared_orders = []
        for order in p1_orders:
            if order not in p2_orders:
                if random.uniform(0, 1) > 0.5:
                    # take order from p1
                    genes = get_genes_for_order(order, p1, self.orders, self.environment)
                    c_genes.append(genes)
                    c_orders.append(order)
                elif order not in shared_orders:
                    if random.uniform(0, 1) > 0.5:
                        # take order from p1
                        genes = get_genes_for_order(order, p1, self.orders, self.environment)
                        c_genes.append(genes)
                        c_orders.append(order)
                    else:
                        # take order from p2
                        genes = get_genes_for_order(order, p2, self.orders, self.environment)
                        c_genes.append(genes)
                        c_orders.append(order)
        for order in p2_orders:
            if order not in p1_orders:
                if random.uniform(0, 1) > 0.5:
                    # take order from p2
                    genes = get_genes_for_order(order, p2, self.orders, self.environment)
                    c_genes.append(genes)
                    c_orders.append(order)
        child = self.individual_factory.create_individual(self.type, c_genes)
        for order in c_unscheduled_orders:
            if order not in c_orders:
                child.unscheduled_orders.append(order)
        return child


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

    def __init__(self, mutation_probability=None):
        self.p = mutation_probability

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
            if not self.p:
                p = 1 / len(individual.genes)
            else:
                p = self.p
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
            if not self.p:
                p = 1 / len(individual.genes)
            else:
                p = self.p
            for i in range(len(individual.genes)):
                if random.uniform(0, 1) < p:
                    self.mutate_gene(individual, orders, environment, i, earliest_slot, last_slot)


class OrderChangeMutation(MutationMethod):

    def mutate_gene(self, individual, orders, environment, index, earliest_slot, last_slot):
        p1 = random.randint(0, len(individual.genes) - 2) # guarantee that a second point can exist
        p2 = random.randint(p1, len(individual.genes) - 1)
        genes = copy.deepcopy(individual.genes)
        selected = copy.deepcopy(genes[p1 : p2 + 1]) # selector is upper bound exclusive 
        selected.reverse()
        for i in range(len(selected)):
            individual.genes[p1 + i] = copy.deepcopy(selected[i])

    def mutate(self, individuals, orders, environment, earliest_slot, last_slot):
        if not self.p:
            p = 1.0
        else:
            p = self.p
        for individual in individuals:
            if random.uniform(0, 1) < p:
                self.mutate_gene(individual, orders, environment, 0, earliest_slot, last_slot)

class VLCMutation(MutationMethod):

    def __init__(self, mutation_probability=None):
        self.add_p = 0.1 # probability of readding a currently unscheduled order
        self.remove_p = 0.1 # probability of removing a currently scheduled order
        super().__init__(mutation_probability)

    # NOTE: copied from RandomizeMutation
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
            # add or remove orders
            if len(individual.unscheduled_orders) > 0:
                if random.uniform(0, 1) < self.add_p:
                    order_id = random.choice(individual.unscheduled_orders)
                    # create genes for selected order
                    order = get_by_id(orders, order_id)
                    tasks = order.tasks
                    for task in tasks:
                        individual.genes.append([task.external_id,0,0])
            if len(individual.genes) > 0: # just to be safe
                if random.uniform(0, 1) < self.remove_p:
                    scheduled_orders = to_order_list(individual, orders, environment)
                    order_id = random.choice(scheduled_orders)
                    # remove genes for selected order
                    genes = get_genes_for_order(order_id, individual, orders, environment)
                    for gene in genes:
                        individual.genes.remove(gene) # should work (?)
                    individual.unscheduled_orders.append(order_id)
            # mutate genes
            if not self.p:
                p = 1 / len(individual.genes)
            else:
                p = self.p
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

def to_order_list(individual, orders, environment):
    genes = copy.deepcopy(individual.genes)
    current_order = -1
    result = []
    for i in range(len(genes)):
        _, order_id = map_index_to_operation(i, orders, environment)
        if order_id != current_order:
            result.append(order_id)
            current_order = order_id
    return result

def get_genes_for_order(id, individual, orders, environment):
    result = []
    for i in range(individual.genes):
        _, order_id = map_index_to_operation(i, orders, environment)
        if order_id == id:
            result.append(copy.deepcopy(individual.genes[i]))
    return result

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