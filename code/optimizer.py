import random
import copy
from re import I
import sys

from models import SimulationEnvironment
from optimizer_components import BaseInputGenerator, Individual, TardinessEvaluator, OnePointCrossover, RouletteWheelSelection, RandomizeMutation, TwoPointCroosover
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

class GA(Optimizer):

    def __init__(self, simulation_environment : SimulationEnvironment):
        self.recipes = simulation_environment.recipes
        self.workstations = simulation_environment.workstations
        self.resources = simulation_environment.resources
        self.tasks = simulation_environment.tasks
        self.current_best = None
        self.minimize = True
        self.evaluation_method = None
        self.recombination_method = None
        self.selection_method = None
        self.mutation_method = None

    def evaluate(self, individuals, orders, last_slot):
        self.evaluation_method(individuals, orders, self.recipes, self.tasks, last_slot)

    def select(self, individuals):
        return self.selection_method.select(individuals, self.minimize)

    def recombine(self, individuals):
        parent1 = self.select(individuals)
        parent2 = self.select(individuals)
        while parent1 == parent2: # making sure 2 different parents are selected
            parent2 = self.select(individuals)
        return self.recombination_method(parent1, parent2)

    def mutate(self, individuals, earliest_slot, last_slot):
        self.mutation_method.mutate(individuals, self.orders, self.recipes, self.tasks, self.workstations, earliest_slot, last_slot)

    def set_minimize(self):
        self.minimize = True

    def set_maximize(self):
        self.minimize = False

    def configure(self, evaluation : str, recombination : str, selection : str, mutation : str):
        # evaluation method
        if evaluation.lower() == 'tardiness':
            self.evaluation_method = TardinessEvaluator()
        # recombination method
        if recombination.lower() == 'onepointcrossover':
            self.recombination_method = OnePointCrossover()
        elif recombination.lower() == 'twopointcrossover':
            self.recombination_method = TwoPointCroosover()
        # selection method
        if selection.lower() == 'roulettewheel':
            self.selection_method = RouletteWheelSelection()
        # mutation method
        if mutation.lower() == 'randomize':
            self.mutation_method = RandomizeMutation()

class BaseGA(GA):

    def __init__(self, simulation_environment : SimulationEnvironment):
        super().__init__(simulation_environment)

    def create_individual(self, input_format, orders, earliest_slot, last_slot):
        genes = copy.deepcopy(input_format)
        if self.minimize:
            individual = Individual(genes, sys.float_info.max)
        else:
            individual = Individual(genes, sys.float_info.min)
        for i in range(len(genes)):
            self.mutation_method.mutate_gene(individual, orders, self.recipes, self.tasks, self.workstations, i, earliest_slot, last_slot)
        return individual

    def optimize(self, orders, max_generation : int, earliest_time_slot : int, last_time_slot : int, population_size : int, offspring_amount : int, verbose=False):
        if self.evaluation_method == None or self.recombination_method == None or self.selection_method == None or self.mutation_method == None:
            self.configure('tardiness', 'onepointcrossover', 'roulettewheel', 'randomize')
        generator = BaseInputGenerator()
        input = generator.generate_input(orders, self.recipes, self.tasks, self.workstations, earliest_time_slot, last_time_slot)
        population = []
        offsprings = []
        # create starting population
        for _ in range(population_size):
            population.append(self.create_individual(input, orders, earliest_time_slot, last_time_slot))
        # evaluate starting population
        self.evaluate(population, orders, last_time_slot)
        # select current best
        self.current_best = population[0]
        for individual in population[1:]:
            if self.minimize:
                if individual.fitness < self.current_best.fitness:
                    self.current_best = individual
            else:
                if individual.fitness > self.current_best.fitness:
                    self.current_best = individual
        history = [] # fitness history (current best)
        best_generation_history = [] # fitness history (generation best) (same as history with elitism)
        avg_history = [] # fitness history (average of each generation)
        feasible_gen = max_generation # the generation in which the first feasible solution was found
        feasible = self.current_best.feasible
        # start optimizing
        generation = 0
        while generation < max_generation:
            if verbose:
                if feasible:
                    print(f'Current generation: {generation}, Current Best: {self.current_best.fitness}')
                else:
                    print(f'Current generation: {generation}, Current Best: {self.current_best.fitness}, not feasible')
            # create offsprings
            for i in range(offspring_amount):
                # recombine
                i = 0
                while i < offspring_amount:
                    offspring1, offspring2 = self.recombine(population)
                    offsprings.append(offspring1)
                    i+=1
                    if len(offsprings) + 1 < offspring_amount:
                        offsprings.append(offspring2) # discard offspring 2 if too many offsprings were created
                        i += 1
                # mutation
                self.mutate(offsprings, earliest_time_slot, last_time_slot)
            # evaluate offsprings
            self.evaluate(offsprings, orders, last_time_slot)
            # select next generation
            all = population + offsprings # use elitism for now
            if self.minimize:
                all.sort(key=lambda x: x.fitness, reverse=False)
            else:
                all.sort(key=lambda x: x.fitness, reverse=True)
            population = all[0:population_size]
            # select current best
            if self.minimize:
                if population[0].fitness < self.current_best.fitness:
                    if verbose:
                        print(f'New best individual found!')
                    self.current_best = population[0]
            else:
                if population[0].fitness > self.current_best.fitness:
                    if verbose:
                        print(f'New best individual found!')
                    self.current_best = population[0]
            history.append(self.current_best.fitness)
            best_generation_history.append(population[0].fitness)
            fitness = 0
            for individual in population:
                fitness += individual.fitness
            avg_history.append(fitness / len(population))
            if not feasible and self.current_best.feasible:
                print(f'Found first feasible solution!')
                feasible_gen = generation
                feasible = True
            generation += 1
        return self.current_best, history, avg_history, best_generation_history, feasible_gen
