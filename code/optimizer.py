import random
import copy
from re import I
import sys

from models import SimulationEnvironment
from optimizer_components import BaseInputGenerator, Individual, NoCrossover, Particle, OrderCountEvaluator, SameLengthAlternativesInputGenerator, TardinessEvaluator, OnePointCrossover, RouletteWheelSelection, RandomizeMutation, TwoPointCroosover, OnlyFeasibleTimeSlotMutation, OrderChangeMutation
from agent import Agent, AgentSimulator

class Optimizer:

    def __init__(self):
        pass

    def optimize(self, assignments, jobs, simulation_environment, last_timeslot):
        pass

    def set_minimize(self):
        self.minimize = True

    def set_maximize(self):
        self.minimize = False

class Randomizer(Optimizer):

    def __init__(self):
        super().__init__()
        self.name = "Randomizer"
    
    def optimize(self, assignments, jobs, simulation_environment, last_timeslot):
        for i in range(len(assignments)):
            job = jobs[i]
            assignment = assignments[i]
            workstations = simulation_environment.get_valid_workstations(job.task_id)
            assignment[0] = workstations[random.randint(0, len(workstations) - 1)].external_id
            assignment[1] = random.randint(0, last_timeslot)
        return assignments


class GA(Optimizer):

    def __init__(self, simulation_environment : SimulationEnvironment):
        self.recipes = simulation_environment.recipes
        self.workstations = simulation_environment.workstations
        self.resources = simulation_environment.resources
        self.tasks = simulation_environment.tasks
        self.environment = simulation_environment
        self.current_best = None
        self.minimize = True
        self.evaluation_method = None
        self.recombination_method = None
        self.selection_method = None
        self.mutation_method = None
        self.input_generator = None

    def evaluate(self, individuals, orders, earliest_slot, last_slot):
        self.evaluation_method.evaluate(individuals, orders, self.environment, earliest_slot, last_slot)

    def select(self, individuals):
        return self.selection_method.select(individuals, self.minimize)

    def recombine(self, individuals):
        parent1 = self.select(individuals)
        parent2 = self.select(individuals)
        while parent1 == parent2: # making sure 2 different parents are selected
            parent2 = self.select(individuals)
        return self.recombination_method.recombine(parent1, parent2)

    def mutate(self, individuals, orders, earliest_slot, last_slot):
        self.mutation_method.mutate(individuals, orders, self.environment, earliest_slot, last_slot)

    def configure(self, evaluation : str, recombination : str, selection : str, mutation : str):
        # evaluation method
        if evaluation.lower() == 'tardiness':
            self.evaluation_method = TardinessEvaluator()
        elif evaluation.lower() == 'ordercount':
            self.evaluation_method = OrderCountEvaluator()
        # recombination method
        if recombination.lower() == 'onepointcrossover':
            self.recombination_method = OnePointCrossover()
        elif recombination.lower() == 'twopointcrossover':
            self.recombination_method = TwoPointCroosover()
        elif recombination.lower() == 'nocrossover':
            self.recombination_method = NoCrossover()
        # selection method
        if selection.lower() == 'roulettewheel':
            self.selection_method = RouletteWheelSelection()
        # mutation method
        if mutation.lower() == 'randomize':
            self.mutation_method = RandomizeMutation()
        elif mutation.lower() == 'onlyfeasibletimeslot':
            self.mutation_method = OnlyFeasibleTimeSlotMutation()
        elif mutation.lower() == 'orderchange':
            self.mutation_method = OrderChangeMutation()
    
    def set_input_generator(self, generator : str):
        if generator.lower() == 'baseinputgenerator':
            self.input_generator = BaseInputGenerator()
        elif generator.lower() == 'samelengthalternativesgenerator':
            self.input_generator = SameLengthAlternativesInputGenerator()

class BaseGA(GA):

    def create_individual(self, input_format, orders, earliest_slot, last_slot):
        genes = copy.deepcopy(input_format)
        if self.minimize:
            individual = Individual(genes, sys.float_info.max)
        else:
            individual = Individual(genes, sys.float_info.min)
        #self.mutate([individual], orders, earliest_slot, last_slot)
        for i in range(len(genes)):
            self.mutation_method.mutate_gene(individual, orders, self.environment, i, earliest_slot, last_slot)
        return individual

    def optimize(self, orders, max_generation : int, earliest_time_slot : int, last_time_slot : int, population_size : int, offspring_amount : int, verbose=False):
        if self.evaluation_method == None or self.recombination_method == None or self.selection_method == None or self.mutation_method == None:
            self.configure('tardiness', 'onepointcrossover', 'roulettewheel', 'randomize')
        if not self.input_generator:
            self.input_generator = BaseInputGenerator()
        input = self.input_generator.generate_input(orders, self.environment, earliest_time_slot, last_time_slot)
        population = []
        offsprings = []
        # create starting population
        for _ in range(population_size):
            population.append(self.create_individual(input, orders, earliest_time_slot, last_time_slot))
        # evaluate starting population
        self.evaluate(population, orders, earliest_time_slot, last_time_slot)
        # select current best
        self.current_best = population[0]
        for individual in population[1:]:
            if self.minimize:
                if individual.fitness < self.current_best.fitness:
                    self.current_best = copy.deepcopy(individual)
            else:
                if individual.fitness > self.current_best.fitness:
                    self.current_best = copy.deepcopy(individual)
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
            i = 0
            while i < offspring_amount:
                # recombine
                offspring1, offspring2 = self.recombine(population)
                offsprings.append(offspring1)
                i += 1
                if len(offsprings) + 1 < offspring_amount:
                    offsprings.append(offspring2) # discard offspring 2 if too many offsprings were created
                    i += 1
            # mutation
            self.mutate(offsprings, orders, earliest_time_slot, last_time_slot)
            # evaluate offsprings
            self.evaluate(offsprings, orders, earliest_time_slot, last_time_slot)
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
                    self.current_best = copy.deepcopy(population[0])
            else:
                if population[0].fitness > self.current_best.fitness:
                    if verbose:
                        print(f'New best individual found!')
                    self.current_best = copy.deepcopy(population[0])
            history.append(self.current_best.fitness)
            best_generation_history.append(population[0].fitness)
            fitness = 0
            for individual in population:
                fitness += individual.fitness
            avg_history.append(fitness / len(population))
            if not feasible and self.current_best.feasible:
                if verbose:
                    print(f'Found first feasible solution!')
                feasible_gen = generation
                feasible = True
            generation += 1
        return self.current_best, history, avg_history, best_generation_history, feasible_gen


class SimpleAgentGA(GA):
    
    def __init__(self, simulation_environment : SimulationEnvironment, agent : Agent, simulator : AgentSimulator):
        self.simulator = simulator
        self.agent = agent
        super().__init__(simulation_environment)
    
    def create_individual(self, input_format, orders, earliest_slot, last_slot):
        return Individual(input_format, 0)

    def optimize(self, orders, max_generation : int, earliest_time_slot : int, last_time_slot : int, population_size : int, offspring_amount : int, verbose=False):
        history = [] # fitness history (current best)
        best_generation_history = [] # fitness history (generation best) (same as history with elitism)
        avg_history = [] # fitness history (average of each generation)
        feasible_gen = max_generation # the generation in which the first feasible solution was found
        
        if self.evaluation_method == None or self.recombination_method == None or self.selection_method == None or self.mutation_method == None:
            self.configure('ordercount', 'nocrossover', 'roulettewheel', 'orderchange')
            self.set_maximize()
        # create starting population
        population = []
        for _ in range(population_size):
            population.append(self.create_individual(copy.deepcopy(orders), orders, earliest_time_slot, last_time_slot))
        self.evaluate(population, orders, earliest_time_slot, last_time_slot)
        self.current_best = population[0]
        for individual in population[1:]:
            if self.minimize:
                if individual.fitness < self.current_best.fitness:
                    self.current_best = copy.deepcopy(individual)
            else:
                if individual.fitness > self.current_best.fitness:
                    self.current_best = copy.deepcopy(individual)
        feasible = self.current_best.feasible
        offsprings = []
        for generation in range(max_generation):
            if verbose:
                if feasible:
                    print(f'Current generation: {generation}, Current Best: {self.current_best.fitness}')
                else:
                    print(f'Current generation: {generation}, Current Best: {self.current_best.fitness}, not feasible')
            # create offsprings
            i = 0
            while i < offspring_amount:
                # recombine
                offspring1, offspring2 = self.recombine(population)
                offsprings.append(offspring1)
                i += 1
                if len(offsprings) + 1 < offspring_amount:
                    offsprings.append(offspring2) # discard offspring 2 if too many offsprings were created
                    i += 1
            # evaluate offsprings
            self.evaluate(offsprings, orders, earliest_time_slot, last_time_slot)
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
                    self.current_best = copy.deepcopy(population[0])
            else:
                if population[0].fitness > self.current_best.fitness:
                    if verbose:
                        print(f'New best individual found!')
                    self.current_best = copy.deepcopy(population[0])
            history.append(self.current_best.fitness)
            best_generation_history.append(population[0].fitness)
            fitness = 0
            for individual in population:
                fitness += individual.fitness
            avg_history.append(fitness / len(population))
            if not feasible and self.current_best.feasible:
                if verbose:
                    print(f'Found first feasible solution!')
                feasible_gen = generation
                feasible = True
        return self.current_best, history, avg_history, best_generation_history, feasible_gen


class PSO(Optimizer):
    
    def __init__(self, simulation_environment : SimulationEnvironment):
        self.environment = simulation_environment
        self.minimize = True

    def create_individual(self, input_format, orders, earliest_slot, last_slot):
        genes = copy.deepcopy(input_format)
        if self.minimize:
            individual = Individual(genes, sys.float_info.max)
        else:
            individual = Individual(genes, sys.float_info.min)
        for i in range(len(genes)):
            self.mutation_method.mutate_gene(individual, orders, self.environment, i, earliest_slot, last_slot)
        return individual

    def create_particle(self, input_format, orders, erliest, latest):
        individual : Individual = self.create_individual(input_format, orders, erliest, latest)
        return Particle(individual)

    def to_individuals(self, particles):
        individuals = []
        for particle in particles:
            individuals.append(particle.individual)
        return individuals

    def evaluate(self, population, orders, latest):
        self.evaluation_method.evaluate(self.to_individuals(population), orders, self.environment, latest)
        for particle in population:
            if self.minimize:
                if particle.individual.fitness < particle.best_fitness:
                    particle.best_fitness = particle.individual.fitness
                    particle.best_genes = copy.deepcopy(particle.individual.genes)
                    particle.feasible = particle.individual.feasible
                elif particle.individual.fitness > particle.best_fitness:
                    particle.best_fitness = particle.individual.fitness
                    particle.best_genes = copy.deepcopy(particle.individual.genes)
                    particle.feasible = particle.individual.feasible

    def optimize(self, orders, max_generation : int, earliest_time_slot : int, last_time_slot : int, particle_amount : int, inertia : float, personal_weight : float, global_weight : float, v_max : float, v_min : float, upper_bounds, lower_bounds, verbose = True):
        self.evaluation_method = TardinessEvaluator() # for now
        # initialize population
        generator = BaseInputGenerator()
        input = generator.generate_input(orders, self.environment, earliest_time_slot, last_time_slot)
        population = []
        # create starting population
        for _ in range(particle_amount):
            population.append(self.create_particle(input, orders, earliest_time_slot, last_time_slot))
        population = []
        # evaluate current state
        self.evaluate(population, orders, last_time_slot)
        # note, particles start with 0 velocity in each dim right now
        current_best = population[0]        
        for gen in range(max_generation):
            if verbose:
                print(f'Current generation: {gen}, with best fitness: {current_best.best_fitness}')
                if not current_best.feasible:
                    print('Current best particle is not feasible')
            for particle in population:
                if self.minimize:
                    if particle.best_fitness < current_best.best_fitness:
                        current_best = particle
                else:
                    if particle.best_fitness > current_best.best_fitness:
                        current_best = particle
            for particle in population:
                for dim in len(particle.individual.genes):
                    r_personal = random.uniform(0, 1)
                    r_global = random.uniform(0, 1)
                    v = inertia * particle.velocities[dim] + personal_weight * r_personal * (particle.best_genes[dim] - particle.individual.genes[dim]) + global_weight * r_global * (current_best.best_genes[dim] - particle.individual.genes[dim])
                    if v > v_max:
                        v = v_max
                    elif v < v_min:
                        v = v_min
                    particle.individual.genes[dim] += v
                    if particle.individual.genes[dim] > upper_bounds[dim]:
                        particle.individual.genes[dim] = upper_bounds[dim]
                    elif particle.individual.genes[dim] < lower_bounds[dim]:
                        particle.individual.genes[dim] = lower_bounds[dim]
            self.evaluate(orders, orders, last_time_slot)
        current_best.individual.genes = copy.deepcopy(current_best.best_genes)
        current_best.individual.fitness = copy.deepcopy(current_best.best_fitness)

        return current_best.individual