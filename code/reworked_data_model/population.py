import random
import math
import matplotlib.pyplot as plt

"""max_values = [100, 100]

def get_max_dissimilarity():
    return sum(max_values)#len(self.sequence) + sum([len(x) for x in Individual.available_workstations])

def get_dissimilarity(self, other):
    dissimilarity = 0
    for i in range(len(self)):
        if self[i] != other[i]:
            dissimilarity += abs(self[i] - other[i])
    return dissimilarity

def create_random_solution():
    individual = []
    for j in range(len(max_values)):
        individual.append(random.randint(0, max_values[j]))
    return individual

min_distance_success = []

max_attempts = 100
distance_adjustment_rate = 0.75
population = []
population_size = 10
population.append(create_random_solution())

while len(population) < population_size:
    attempts = 0
    dissimilarity = []
    min_distance = get_max_dissimilarity()
    while len(dissimilarity) == 0 or (sum(dissimilarity)/len(dissimilarity)) < min_distance:
        if attempts > max_attempts:
            min_distance = int(min_distance * distance_adjustment_rate)
            attempts = 0
        individual = create_random_solution()
        for other in population:
            dissimilarity.append(get_dissimilarity(individual, other))
        attempts += 1
    population.append(individual)
    min_distance_success.append(min_distance)

x_values = [x[0] for x in population]
y_values = [x[1] for x in population]
print(min_distance_success)
print(population)



plt.scatter(x_values, y_values)
plt.show()
"""
class Individual:

    def __init__(self, population_size, gene_values, evaluation_method):
        self.population = []
        self.gene_values = gene_values
        for _ in range(population_size):
            individual = self.randomize_individual()
            while individual in self.population:
                individual = self.randomize_individual()
            self.population.append(individual)
        self.evaluation_method = evaluation_method
        self.fitness = 0

    def __eq__(self, other):
        return self.population == other.population

    def randomize_individual(self):
        individual = []
        for j in range(len(self.gene_values)):
            individual.append(random.choice(self.gene_values[j]))
        return individual
    
    def get_dissimilarity(self, a, b):
        dissimilarity = 0
        for i in range(len(a)):
            if a[i] != b[i]:
                dissimilarity += len(self.gene_values[i])
        return dissimilarity

    def feasible(self):
        for i in range(len(self.population)):
            for j in range(len(self.population)):
                if i != j and self.population[i] == self.population[j]:
                    return False
        return True

    def evaluate_variance(self):
        avg_dissimilarities = []
        for i in range(len(self.population)):
            dissimilarity = []
            for j in range(len(self.population)):
                if i != j:
                    dissimilarity.append(self.get_dissimilarity(self.population[i], self.population[j]))
            avg_dissimilarities.append(sum(dissimilarity) / len(dissimilarity))
        average_dissimilarity = sum(avg_dissimilarities)/len(avg_dissimilarities)
        variance = sum([((x - average_dissimilarity) ** 2) for x in avg_dissimilarities]) / len(avg_dissimilarities)
        self.fitness = variance
    
    def evaluate_average(self):
        avg_dissimilarities = []
        for i in range(len(self.population)):
            dissimilarity = []
            for j in range(len(self.population)):
                if i != j:
                    dissimilarity.append(self.get_dissimilarity(self.population[i], self.population[j]))
            avg_dissimilarities.append(sum(dissimilarity) / len(dissimilarity))
        average_dissimilarity = sum(avg_dissimilarities)/len(avg_dissimilarities)
        self.fitness = average_dissimilarity
    
    def evaluate_min(self):
        min_dissimilarities = []
        for i in range(len(self.population)):
            dissimilarity = []
            for j in range(len(self.population)):
                if i != j:
                    dissimilarity.append(self.get_dissimilarity(self.population[i], self.population[j]))
            min_dissimilarities.append(min(dissimilarity))
        self.fitness = min(min_dissimilarities)

    def evaluate(self):
        if not self.feasible():
            return 0
        if self.evaluation_method == 'variance':
            self.evaluate_variance()
        elif self.evaluation_method == 'average':
            self.evaluate_average()
        else:
            self.evaluate_min()

    def mutate(self):
        p = 1 / len(self.population)
        for i in range(len(self.population)):
            if random.random() < p:
                self.population[i] = self.randomize_individual()

    def recombine(self, parent_a, parent_b):
        #split_point = random.randint(0, len(parent_a.population))
        #self.population = parent_a.population[:split_point]
        #self.population.extend(parent_b.population[split_point:])
        self.population = []
        for i in range(len(parent_a.population)):
            if random.random() < 0.5:
                self.population.append(parent_a.population[i])
            else:
                self.population.append(parent_b.population[i])

class PopulationGenerator:

    def __init__(self, population_size, gene_values : list[list[int]] = [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]]): # values just for testing
        self.population_size = population_size
        self.gene_values = gene_values
        self.population = []
    
    def max_dissimilarity(self):
        max_dissimilarity = 0
        for i in range(len(self.gene_values)):
            max_dissimilarity += len(self.gene_values[i])
        return max_dissimilarity

    def tournament_selection(self, population, tournament_size = 0):
        # tournament selection
        if tournament_size == 0:
            tournament_size = max(int(len(population) / 10), 2)
        participants = random.choices(range(0, len(population)), k=tournament_size)
        winner = sorted(participants, key=lambda x: population[x].fitness, reverse=True)[0]
        return population[winner]

    def run(self, population_size, offspring_amount, max_generations, elitism : int = 0, evaluation_method : str = 'variance'):
        self.population : list[Individual] = []
        for _ in range(population_size):
            individual = Individual(self.population_size, self.gene_values, evaluation_method)
            while individual in self.population:
                individual = Individual(self.population_size, self.gene_values, evaluation_method)
            individual.evaluate()
            self.population.append(individual)
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        overall_best = self.population[0]
        history = [overall_best.fitness]
        overall_best_history = [overall_best.fitness]
        for i in range(max_generations):
            if i % int(max_generations/10) == 0:
                print(f'Generation {i}: {overall_best.fitness}')
            offsprings = []
            for _ in range(offspring_amount):
                # TODO: selection method
                parent_a = self.tournament_selection(self.population)#random.choice(self.population)
                parent_b = self.tournament_selection(self.population)#random.choice(self.population)
                
                offspring = Individual(self.population_size, self.gene_values, evaluation_method)
                offspring.recombine(parent_a, parent_b)
                offspring.mutate()
                offspring.evaluate()
                offsprings.append(offspring)
            offsprings.sort(key=lambda x: x.fitness, reverse=True)
            if offsprings[0].fitness > overall_best.fitness:
                overall_best = offsprings[0]
            selection_pool = offsprings
            self.population.sort(key=lambda x: x.fitness, reverse=True)
            if elitism > 0:
                selection_pool.extend(self.population[:elitism])
            self.population = selection_pool[:population_size]
            history.append(sorted(self.population, key=lambda x: x.fitness, reverse=True)[0].fitness)
            overall_best_history.append(overall_best.fitness)
        return overall_best, history, overall_best_history

population_size = 40
values = [[0, 1, 2], [3, 4, 5], [2, 4, 5], [0, 2, 5, 6], [1, 3], [4, 5, 6], [0, 1, 2, 3, 4], [5, 6], [3, 4, 6]]
#values = [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]]
population_generator = PopulationGenerator(population_size, values)
max_dissimilarity = population_generator.max_dissimilarity()
print(f' Max Dissimilarity: {max_dissimilarity}')
result, history, best_history = population_generator.run(50, 100, 10 * population_size, 10, 'min')

print(result.population)
print('Variance:')
result.evaluate_variance()
print(result.fitness)
print('Average:')
result.evaluate_average()
print(result.fitness)
print('Min. Distance:')
result.evaluate_min()
print(result.fitness)
plt.plot(history)
plt.plot(best_history)
plt.show()

#x_values = [data[0] for data in result.population]
#y_values = [data[1] for data in result.population]
#print(x_values)
#print(y_values)
#plt.scatter(x_values, y_values)
#plt.show()