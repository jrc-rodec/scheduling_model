from solver import Solver
from model import ProductionEnvironment, Schedule
from translation import Encoder
import random

class TimeWindowSequenceGA(Solver):

    def __init__(self, production_environment : ProductionEnvironment, encoder : Encoder = None):
        super().__init__('Time Window Sequence GA', production_environment, encoder)

        self.max_generations = 0
        self.max_function_evaluations = 0

    def initialize(self):
        self.jobs = []
        self.mutate_workers = False
        self.mutate_duration = False
        self.allow_overlap = False
        self.split_genes = True
        self.elitism = True
        self.recombination_method = self.uniform_crossover
        #self.recombination_method = self.one_point_crossover

    def mutate(self, individual):
        if not self.split_genes:
            p = 1 / (len(individual)/4)
            for i in range(0, len(individual), 4):
                if random.random() < p:
                    workstations = self.production_environment.get_available_workstations_for_task(self.jobs[int(i/4)])
                    individual[i] = int(random.choice(workstations).id)
                    workstation = individual[i]

                    indices = []
                    for j in range(0, len(individual), 4):
                        if individual[j] == workstation and j != i:
                            indices.append(j+1)
                    if len(indices) > 0:
                        swap = random.choice(indices)
                        temp = individual[i+1]
                        individual[i+1] = individual[swap]
                        individual[swap] = temp
                    
                    # mutate workers
                    if self.mutate_workers:
                        # individual[i+2]
                        pass
                    # mutate duration
                    if self.mutate_duration:
                        # individual[i+3]
                        pass
        else:
            p = 1 / len(individual)
            # mutate workstation assignments
            for i in range(0, len(individual), 4):
                if random.random() < p:
                    workstations = self.production_environment.get_available_workstations_for_task(self.jobs[int(i/4)])
                    individual[i] = int(random.choice(workstations).id)
                
            # mutate sequence order
            for i in range(1, len(individual), 4):
                if random.random() < p:
                    workstation = individual[i-1]
                    indices = []
                    for j in range(0, len(individual), 4):
                        if individual[j] == workstation and j != i-1:
                            indices.append(j+1)
                    if len(indices) > 0:
                        swap = random.choice(indices)
                        temp = individual[i]
                        individual[i] = individual[swap]
                        individual[swap] = temp

            if self.mutate_workers:
                for i in range(2, len(individual), 4):
                    if random.random() < p:
                        pass # TODO
            # if time windows enabled, mutate time window size
            if self.mutate_duration:
                for i in range(3, len(individual), 4):
                    if random.random() < p:
                        pass # TODO - upper bound?

    def one_point_crossover(self, parent_a, parent_b):
        crossover_point = random.randint(0, len(parent_a)-2)
        if not self.split_genes:
            crossover_point %= 4
            crossover_point = max(3, crossover_point-1) # NOTE: review
        offspring = []
        offspring.extend(parent_a[:crossover_point])
        offspring.extend(parent_b[crossover_point+1:])
        self.repair(offspring)
        return offspring

    def uniform_crossover(self, parent_a, parent_b):
        selection_values = [0 if random.random() < 0.5 else 1 for _ in range(len(parent_a))]
        offspring = []
        for i in range(len(selection_values)):
            if not self.split_genes:
                if i % 4 == 0: # a little inefficient but ok for now
                    for j in range(i, i+4):
                        offspring.append(parent_a[j] if selection_values[i] == 1 else parent_b[j])
            else:
                offspring.append(parent_a[i] if selection_values[i] == 1 else parent_b[i])
        # repair
        for i in range(0, len(offspring), 4):
            workstation = offspring[i]
            conflicts_found = True
            while conflicts_found:
                conflicts_found = False
                for j in range(0, len(offspring), 4):
                    if i != j and offspring[j] == workstation:
                        # check if sequence has a conflict
                        if offspring[i+1] == offspring[j+1]:
                            conflicts_found = True
                            if (selection_values[i+1] == 1 and selection_values[j+1] == 1) or (selection_values[i+1] == 0 and selection_values[j+1] == 0):
                                if random.random() < 0.5:
                                    offspring[j+1] += 1
                                else:
                                    offspring[i+1] += 1
                            elif selection_values[i+1] == 1:
                                offspring[j+1] += 1
                            else:
                                offspring[i+1] += 1
        return offspring

    def recombine(self):
        # for testing, just single point crossover
        parent_a = self.select()
        parent_b = self.select()
        while parent_a == parent_b:
            parent_b = self.select() # NOTE: maybe needs changing
        offspring = self.recombination_method(parent_a, parent_b)
        #offspring = self.one_point_crossover(parent_a, parent_b)
        return offspring

    def repair(self, offspring):
        for i in range(0, len(offspring), 4):
            workstation = offspring[i]
            conflicts_found = True
            while conflicts_found:
                conflicts_found = False
                for j in range(0, len(offspring), 4):
                    if i != j and offspring[j] == workstation:
                        # check if sequence has a conflict
                        if offspring[i+1] == offspring[j+1]:
                            conflicts_found = True
                            if random.random() < 0.5:
                                offspring[j+1] += 1
                            else:
                                offspring[i+1] += 1
        return offspring

    def select(self):
        # tournament selection
        participant_amount = int(self.population_size / 4) # TODO
        participants = []
        for _ in participant_amount:
            participants.append(random.randint(0, len(self.population)-1))
        winner = participants[0]
        for i in range(1, len(participants)):
            if self.population_fitness[participants[i]] < self.population_fitness[winner]:
                winner = participants[i]
        return self.population[winner]

    def evaluate(self, solution : list[int]):
        if solution in self.memory:
            self.memory_access += 1
            return self.memory[solution][0] # NOTE: just use the first values for now
        feasible = False # TODO
        if self.allow_overlap:
            pass
        else:
            pass
        if self.mutate_workers:
            pass
        if not feasible:
            return float('inf')
        schedule : Schedule = self.encoder.decode(solution, self.jobs, self.production_environment, [], self)
        result = self.evaluator.evaluate(schedule, self.jobs)
        self.memory[solution] = result
        self.function_evaluations += 1
        return result[0] # NOTE: just using the first value for now

    def evaluate_population(self, population) -> list[float]:
        population_fitness = []
        for i in range(len(population)):
            population_fitness.append(self.evaluate(population[i]))
        return population_fitness

    def create_population(self) -> list[list[int]]:
        population :list[list[int]] = []
        for i in range(self.population_size):
            individual : list[int] = []
            for j in range(self.jobs):
                workstation = int(random.choice(self.production_environment.get_available_workstations_for_task(self.jobs[j].task)))
                tasks_on_workstation = 0
                for k in range(0, len(individual), 4):
                    if individual[k] == workstation:
                        tasks_on_workstation += 1
                sequence = random.randint(0, tasks_on_workstation)
                worker = 0
                if self.mutate_workers:
                    # TODO choose available worker
                    pass
                duration = self.production_environment.get_workstation(workstation).get_duration(self.jobs[j].task)
                if self.mutate_duration:
                    # TODO randomly select duration
                    pass
                individual.extend([workstation, sequence, worker, duration])
            self.repair(individual)
            population.append(individual)
        return population

    def should_stop(self) -> bool:
        if self.max_generations > 0 and self.generation >= self.max_generations:
            return True
        if self.max_function_evaluations > 0 and self.function_evaluations >= self.max_function_evaluations:
            return True
        return False

    def run(self, population_size : int = 25, offspring_amount : int = 50, start_population : list[list[int]] = None):
        self.memory : dict(list[int], list[int]) = []
        self.history = {"best": [], "average": []}
        self.function_evaluations = 0
        self.memory_access = 0
        self.population_size = population_size
        self.offspring_amount = offspring_amount
        if start_population:
            self.population = start_population
        else:
            self.population : list[list[int]] = self.create_population()
        self.population_fitness = self.evaluate_population(self.population)
        min_index = self.population_fitness.index(min(self.population_fitness))
        self.current_best = self.population[min_index]
        self.current_best_fitness = self.population_fitness[min_index]
        self.generation = 0
        if self.max_generations == 0 and self.max_function_evaluations == 0:
            print('No stopping criteria set, abort')
            return False
        while not self.should_stop():
            #create offsprings
            offsprings : list[list[int]] = []
            for _ in range(len(self.offspring_amount)):
                offspring = self.recombine()
                #self.repair(offspring) # done at the end of recombination instead
                offsprings.append(offspring)
            #mutate offsprings
            for offspring in offsprings:
                self.mutate(offspring)
            #evaluate offsprings
            offspring_fitness : list[float] = self.evaluate_population(offsprings)
            #select new population
            selection_pool = offsprings
            selection_pool_fitness = offspring_fitness
            if self.elitism:
                selection_pool.extend(self.population)
                selection_pool_fitness.extend(self.population_fitness)
            selection_pool.sort(key=lambda x: selection_pool_fitness[selection_pool.index(x)])
            selection_pool_fitness.sort()
            self.population = selection_pool[:self.population_size]
            self.population_fitness = selection_pool_fitness[:self.population_size]

            if self.population_fitness[0] < self.current_best_fitness:
                self.current_best = self.population[0]
                self.current_best_fitness = self.population_fitness[0]
            self.history["best"].append(self.current_best_fitness)
            self.history["average"].append(sum(self.population_fitness) / len(self.population_fitness))

            self.generation += 1
        