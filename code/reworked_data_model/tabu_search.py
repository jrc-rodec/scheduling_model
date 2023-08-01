class Individual:

    AVAILABLE_WORKSTATIONS = []

    def __init__(self):
        self.fitness = float('inf')
        self.workstations = []
        self.sequence = []

    def get_dissimilarity(self, other):
        dissimilarity = 0
        for i in range(len(self.workstations)):
            if other.workstations[i] != self.workstations[i]:
                dissimilarity += len(Individual.AVAILABLE_WORKSTATIONS[i])
            if other.sequence[i] != self.sequence[i]:
                dissimilarity += 1
        return dissimilarity
    
class TabuSearch:

    def __init__(self):
        pass

    def get_neighbours(self, individual):
        pass

    def initialize_population(self):
        pass

    def run(self, max_tabu_size : int = 10, max_iteration = 100):
        #NOTE: short term memory
        self.tabu_list = []
        population : list[Individual] = self.initialize_population(self)
        population.sort(key=lambda x: x.fitness)
        best = bestCandidate = population[0]
        self.tabu_list.append(best)
        iteration = 0
        while iteration < max_iteration:
            neighborhood = self.get_neighbours(bestCandidate)
            for neighbor in neighborhood:
                if neighbor.fitness < bestCandidate.fitness and not neighbor in self.tabu_list:
                    bestCandidate = neighbor
            if(bestCandidate.fitness < best.fitness):
                best = bestCandidate
            self.tabu_list.append(bestCandidate)
            if len(self.tabu_list) > max_tabu_size:
                self.tabu_list.pop(0)
            iteration += 1
        return best