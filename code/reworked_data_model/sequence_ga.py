from solver import Solver
from model import ProductionEnvironment, Schedule, Job, Order
from translation import Encoder
import random
import copy

class TimeWindowSequenceGA(Solver):

    def __init__(self, production_environment : ProductionEnvironment, encoder : Encoder = None):
        super().__init__('Time Window Sequence GA', production_environment, encoder)

        self.max_generations = 0
        self.max_function_evaluations = 0

    def initialize(self, jobs : list[Job]):
        self.jobs = jobs
        self.mutate_workers = False
        self.mutate_duration = False
        self.allow_overlap = False
        self.split_genes = True
        self.elitism = False
        self.include_random_individuals = 0
        self.tournament_size = 0
        self.replace_duplicates = False
        self.recombination_method = self.uniform_crossover
        #self.recombination_method = self.one_point_crossover

    def mutate(self, individual):
        if not self.split_genes:
            p = 1 / (len(individual)/4)
            for i in range(0, len(individual), 4):
                if random.random() < p:
                    workstations = self.production_environment.get_available_workstations_for_task(self.jobs[int(i/4)].task)
                    # TODO: workstation other than the current one, except if only 1 is available
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
                        alternatives = self.production_environment.get_alternative_tasks(self.jobs[int(i/4)].task)
                        task = random.choice(alternatives)
                        individual[i+2] = int(task.id)
                        self.jobs[int(i/4)].task = task
                        if not self.mutate_duration:
                            individual[i+1] = self.production_environment.get_workstation(individual[i-2]).get_duration(task) # set new duration NOTE: all of the alternative tasks should be able to be processed on the same workstations
                    # mutate duration
                    if self.mutate_duration:
                        # individual[i+3]
                        pass
        else:
            p = 1 / len(individual)
            # mutate workstation assignments
            for i in range(0, len(individual), 4):
                if random.random() < p:
                    workstations = self.production_environment.get_available_workstations_for_task(self.jobs[int(i/4)].task)
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
                        alternatives = self.production_environment.get_alternative_tasks(self.jobs[int((i-2)/4)].task)
                        task = random.choice(alternatives)
                        individual[i] = int(task.id)
                        self.jobs[int((i-2)/4)].task = task
                        if not self.mutate_duration:
                            individual[i+1] = self.production_environment.get_workstation(individual[i-2]).get_duration(task)
            # if time windows enabled, mutate time window size
            if self.mutate_duration:
                for i in range(3, len(individual), 4):
                    if random.random() < p:
                        pass # TODO - upper bound?

    def one_point_crossover(self, parent_a, parent_b):
        crossover_point = random.randint(0, len(parent_a)-2)
        if not self.split_genes:
            #crossover_point %= 4
            #crossover_point = max(3, crossover_point-1) # NOTE: review
            crossover_point = random.randint(1, int(len(parent_a)/4)-1)
            crossover_point *= 4
        offspring = []
        offspring.extend(parent_a[:crossover_point])
        offspring.extend(parent_b[crossover_point:])
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
        #parent_a = self.select()
        parent_a = self.select_roulette()
        #parent_b = self.select()
        parent_b = self.select_roulette()
        while parent_a == parent_b:
            #parent_b = self.select() # NOTE: maybe needs changing
            parent_b = self.select_roulette() # NOTE: maybe needs changing
        #offspring = self.recombination_method(parent_a, parent_b)
        offspring = self.one_point_crossover(parent_a, parent_b)
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
        if self.tournament_size == 0:
            participant_amount = int(self.population_size / 10) # TODO
        else:
            participant_amount = int(self.tournament_size)
        participants = random.choices(range(0, len(self.population)), k=participant_amount)
        winner = sorted(participants, key=lambda x: self.population_fitness[x])[0]
        return self.population[winner]

    def select_roulette(self) -> list[int]:
        fitness_sum = 0
        for fitness in self.population_fitness:
            fitness_sum += fitness # NOTE: only use first
        probabilities = [0.0] * len(self.population_fitness)
        previous_probability = 0.0
        for i in range(len(probabilities)):
            probabilities[i] = previous_probability + (self.population_fitness[i] / fitness_sum)
            previous_probability = probabilities[i]
        n = random.random()
        for i in range(len(probabilities)):
            if n < probabilities[i]:
                return self.population[i]
        return self.population[-1]

    def evaluate(self, solution : list[int]):
        if str(solution) in self.memory:
            self.memory_access += 1
            return self.memory[str(solution)][0] # NOTE: just use the first values for now
        feasible = True # TODO 
        # check for circular dependencies
        
        if self.allow_overlap:
            pass
        else:
            pass
        if self.mutate_workers:
            pass
        if not feasible:
            self.memory[str(solution)] = [float('inf')]
            return float('inf')
        schedule : Schedule = self.encoder.decode(solution, self.jobs, self.production_environment, [], self)
        result = self.evaluator.evaluate(schedule, self.jobs)
        self.memory[str(solution)] = result
        self.function_evaluations += 1
        return result[0] # NOTE: just using the first value for now

    def evaluate_population(self, population) -> list[float]:
        population_fitness = []
        for i in range(len(population)):
            population_fitness.append(self.evaluate(population[i]))
        return population_fitness

    def create_individual(self) -> list[int]:
        individual : list[int] = []
        for j in range(len(self.jobs)):
            workstation = int(random.choice(self.production_environment.get_available_workstations_for_task(self.jobs[j].task)).id)
            tasks_on_workstation = 0
            for k in range(0, len(individual), 4):
                if individual[k] == workstation:
                    tasks_on_workstation += 1
            sequence = random.randint(0, tasks_on_workstation)
            worker = 0
            if self.mutate_workers:
                alternatives = production_environment.get_alternative_tasks(self.jobs[j].task)
                task = random.choice(alternatives)
                worker = int(task.id)
                self.jobs[j].task = task
            duration = self.production_environment.get_workstation(workstation).get_duration(self.jobs[j].task)
            if self.mutate_duration:
                # TODO randomly select duration
                pass
            individual.extend([workstation, sequence, worker, duration])
        self.repair(individual)
        return individual

    def create_population(self) -> list[list[int]]:
        population :list[list[int]] = []
        for i in range(self.population_size):
            individual = self.create_individual()
            population.append(individual)
        return population

    def should_stop(self) -> bool:
        if self.max_generations > 0 and self.generation >= self.max_generations:
            return True
        if self.max_function_evaluations > 0 and self.function_evaluations >= self.max_function_evaluations:
            return True
        return False
    
    def select_next_generation(self, population, population_fitness, offsprings, offspring_fitness):
        elitism_rate = int(len(population)/len(population)) # only keep the best for now
        next_generation = []
        next_generation_fitness = []
        sorted_population = sorted(population, key=lambda x: population_fitness[population.index(x)])
        sorted_offsprings = sorted(offsprings, key=lambda x: offspring_fitness[offsprings.index(x)])
        population_fitness.sort()
        offspring_fitness.sort()
        if self.include_random_individuals > 0:
            for i in range(int(self.include_random_individuals)):
                individual = self.create_individual()
                next_generation.append(individual)
                next_generation_fitness.append(self.evaluate(individual))
        if self.replace_duplicates:
            for i in range(self.population_size - len(next_generation)):
                duplicate = False
                if len(next_generation) > 0:
                    for individual in next_generation:
                        if individual == sorted_offsprings[i]:
                            duplicate = True
                            break
                if duplicate:
                    individual = self.create_individual()
                    next_generation.append(individual)
                    next_generation_fitness.append(self.evaluate(individual))
                else:
                    next_generation.append(sorted_offsprings[i])
                    next_generation_fitness.append(offspring_fitness[i])
        else:
            next_generation.extend(sorted_offsprings[:self.population_size - len(next_generation)])
            next_generation_fitness.extend(offspring_fitness[:self.population_size - len(next_generation_fitness)])
        for i in range(elitism_rate):
            if population_fitness[i] >= next_generation_fitness[-i-1]:
                break
            next_generation[-i-1] = sorted_population[i]
            next_generation_fitness[-i-1] = population_fitness[i]
        next_generation = sorted(next_generation, key=lambda x: next_generation_fitness[next_generation.index(x)])
        next_generation_fitness.sort()
        return next_generation, next_generation_fitness

    def run(self, population_size : int = 25, offspring_amount : int = 50, start_population : list[list[int]] = None):
        self.memory : dict(str, list[int]) = dict()
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
            if self.generation > 0 and self.generation % 100 == 0:
                print(f'Currently at Generation {self.generation} with best fitness: {self.history["best"][-1]} and average fitness of {self.history["average"][-1]}')
            #create offsprings
            offsprings : list[list[int]] = []
            for _ in range(self.offspring_amount):
                offspring = self.recombine()
                #self.repair(offspring) # done at the end of recombination instead
                offsprings.append(offspring)
            #mutate offsprings
            for offspring in offsprings:
                self.mutate(offspring)
            #evaluate offsprings
            offspring_fitness : list[float] = self.evaluate_population(offsprings)
            #select new population
            self.population, self.population_fitness = self.select_next_generation(self.population, self.population_fitness, offsprings, offspring_fitness)

            if self.population_fitness[0] < self.current_best_fitness:
                self.current_best = self.population[0]
                self.current_best_fitness = self.population_fitness[0]
            self.history["best"].append(self.current_best_fitness)
            self.history["average"].append(sum(self.population_fitness) / len(self.population_fitness))

            self.generation += 1

from translation import TimeWindowSequenceEncoder, FJSSPInstancesTranslator
from evaluation import Makespan
from visualization import visualize_schedule
def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders

encoder = TimeWindowSequenceEncoder()
source = '6_Fattahi'
benchmark_id = 20
production_environment : ProductionEnvironment = FJSSPInstancesTranslator().translate(source, benchmark_id)
orders = generate_one_order_per_recipe(production_environment)
solver = TimeWindowSequenceGA(production_environment, encoder)
values, jobs = encoder.encode(production_environment, orders)
solver.initialize(jobs)

solver.max_generations = 30000
solver.add_objective(Makespan())
population_size = 50
offspring_amount = 100

solver.mutate_workers = False
solver.mutate_duration = False
solver.allow_overlap = False
solver.split_genes = True
solver.elitism = False
solver.include_random_individuals = 0#population_size / 10
solver.replace_duplicates = True
solver.tournament_size = population_size / 8

solver.run(population_size, offspring_amount)

result = solver.current_best
fitness = solver.current_best_fitness
print(result)
print(fitness)
schedule = encoder.decode(result, jobs, production_environment, [], solver)
visualize_schedule(schedule, production_environment, orders)

import matplotlib.pyplot as plt
best_history = solver.history["best"]
generation_average_history = solver.history["average"]

plt.plot(best_history)
plt.plot(generation_average_history)
plt.show()

from evaluation import * 
evaluator = Evaluator(production_environment)
evaluator.add_objective(Makespan())
evaluator.add_objective(IdleTime())
evaluator.add_objective(TimeDeviation())
evaluator.add_objective(Tardiness())
evaluator.add_objective(Profit())
evaluator.add_objective(UnfulfilledOrders())
objective_values = evaluator.evaluate(schedule, jobs)
parameters = f'max_generations:{solver.max_generations},population_size:{population_size},offspring_amount:{offspring_amount}'


from result_writer import write_result
write_result(schedule, f'{source}_{benchmark_id}', solver.name, objective_values, parameters, result)
