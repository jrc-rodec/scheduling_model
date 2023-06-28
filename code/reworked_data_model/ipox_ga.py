import random

class IPOXGA:

    def __init__(self, job_orders : list[int], workstation_options : list[list[int]]):
        self.job_orders = job_orders
        self.workstation_options = workstation_options
        self.jobs = list(set(self.job_orders))

    def create_individual(self) -> list[int]:
        # encoding: <job id, workstation id>
        used = [False] * len(self.job_orders)
        individual = [0] * 2 * len(self.job_orders)
        for i in range(len(self.job_orders)):
            free_slots = [j for j in range(len(used)) if not used[j]]
            index = random.choice(free_slots) * 2
            individual[index] = self.job_orders[i]
            individual[index+1] = random.choice(self.workstation_options[i])
            used[index] = True
        return individual
    
    def create_population(self, population_size : int) -> list[list[int]]:
        population :list[list[int]] = []
        for _ in range(population_size):
            population.append(self.create_individual())
        return population
    
    def recombine(self, parent_a, parent_b) -> tuple[list[int], list[int]]:
        child_a = [0] * 2 * len(self.job_orders)
        child_b = [0] * 2 * len(self.job_orders)

        workstation_crossover = [0 if random.random() < 0.5 else 1 for _ in range(len(self.job_orders))]
        for i in range(1, len(parent_a), 2):
            if workstation_crossover[int(i/2)] == 0:
                child_a[i] = parent_a[i]
                child_b[i] = parent_b[i]
            else:
                child_a[i] = parent_b[i]
                child_b[i] = parent_a[i]

        split = [0 if random.random() < 0.5 else 1 for _ in range(len(self.jobs))]
        set_a = [self.jobs[j] for j in range(len(self.jobs)) if split[self.jobs[j]] == 0]
        set_b = [self.jobs[j] for j in range(len(self.jobs)) if split[self.jobs[j]] == 1]
        alt_index = 0
        for i in range(0, len(parent_a), 2):
            if parent_a[i] in set_a:
                child_a[i] = parent_a[i]
            else:
                # else fill with parent b
                for j in range(alt_index, len(parent_b), 2):
                    alt_index = j
                    if parent_b[j] in set_b:
                        child_a[i] = parent_b[j]
        alt_index = 0
        for i in range(0, len(parent_b), 2):
            if parent_b[i] in set_b:
                child_b[i] = parent_b[i]
            else:
                # else fill with parent a
                for j in range(alt_index, len(parent_a), 2):
                    alt_index = j
                    if parent_a[j] in set_a:
                        child_b[i] = parent_a[j]

    def run(self, population_size : int, offspring_amount : int, generations : int):
        population = self.create_population(population_size)

a = [0, 1, 1, 2, 2, 3, 4, 4, 4]
b = list(set(a))
print(b)
print(len(b))

split = [0 if random.random() < 0.5 else 1 for _ in range(len(b))]
set_a = [b[j] for j in range(len(b)) if split[b[j]] == 0]
set_b = [b[j] for j in range(len(b)) if split[b[j]] == 1]
print(set_a)
print(set_b)
parent_a = [1, 0, 1, 4, 3, 4, 2, 2, 4]
parent_b = [4, 3, 1, 1, 0, 2, 4, 2, 4]
child_a = [0] * len(parent_a)
child_b = [0] * len(parent_a)
split = [0 if random.random() < 0.5 else 1 for _ in range(len(b))]
set_a = [b[j] for j in range(len(b)) if split[b[j]] == 0]
set_b = [b[j] for j in range(len(b)) if split[b[j]] == 1]
alt_index = 0
for i in range(0, len(parent_a)):
    if parent_a[i] in set_a:
        child_a[i] = parent_a[i]
    else:
        # else fill with parent b
        for j in range(alt_index, len(parent_b)):
            alt_index = j
            if parent_b[j] in set_b:
                child_a[i] = parent_b[j]
                break
alt_index = 0
for i in range(0, len(parent_b)):
    if parent_b[i] in set_b:
        child_b[i] = parent_b[i]
    else:
        # else fill with parent a
        for j in range(alt_index, len(parent_a)):
            alt_index = j
            if parent_a[j] in set_a:
                child_b[i] = parent_a[j]
                break

print(parent_a)
print(child_a)
print(child_b)
print(parent_b)