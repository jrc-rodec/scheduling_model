solution = [1,7367,    1, 7592,    3, 7732,    7, 7882,    0, 7111,    2, 7520,    6, 7757,
    4, 7907,    0, 6961,    3, 7107,    4, 7212,    7, 7312,    0, 6629,    4, 6743,
    5, 6956,    5, 7857,    0, 6805,    6, 7004,    4, 7312,    5, 7677,    1, 7189,
    2, 7651,    4, 7787,    6, 7941,    2, 6770,    2, 6919,    6, 7091,    4, 7647,
    3, 6617,    4, 6923,    6, 7271,    6, 7455,    2, 6620,    2, 7084,    4, 7422,
    7, 7477,    3, 6862,    5, 7136,   5, 7361,    6, 7605,    1, 7039,    3, 7212,
    4, 7462,    5, 7526,    1, 6620,    2, 7264,    4, 7502,    7, 7652]

#print(solution)

"""w_sorting : list[list[int]] = []
for workstation in [0,1,2,3,4,5,6,7]:
    w_sorting.append([])
    for i in range(0, len(solution), 2):
        if solution[i] == int(workstation):
            w_sorting[-1].append(i)
    w_sorting[-1].sort(key= lambda x: solution[x+1])
print(w_sorting)
for sorting in w_sorting:
    print([solution[x+1] for x in sorting])"""

"""on_workstations = [[i for i in range(0, len(solution), 2) if i == j] for j in [0,1,2,3,4,5,6,7]] # all indices for each workstation
for workstation in [0,1,2,3,4,5,6,7]:
    on_workstations[workstation] = []
    for i in range(0, len(solution), 2):
        if solution[i] == workstation:
            on_workstations[workstation].append(i)
for workstation in on_workstations:
    workstation.sort(key=lambda x: solution[x+1]) # sort indices by sequence
print(on_workstations)"""

"""values = [0, 0, 10, 0, 1, 5, 1, 1, 5, 1, 0, 10]
jobs = [0, 0, 0, 1]
result = values.copy()
on_workstations = []
for workstation in [0, 1]:
    on_workstations.append([])
    for i in range(0,len(result), 3):
        if result[i] == workstation:
            on_workstations[workstation].append(i)
print(on_workstations)
for workstation in on_workstations:
    workstation.sort(key=lambda x: values[x+1])
    for i in range(len(workstation)):
        if i == 0:
            result[workstation[i]+1] = 0
        else:
            result[workstation[i]+1] = result[workstation[i-1]+1] + result[workstation[i-1]+2]
print(on_workstations)
print(result)
for i in range(0,len(result),3):
    if i > 0 and jobs[int(i/3)] == jobs[int(i/3)-1]:
        #on_workstation = [x for x in on_workstations if result[i] in x][0]
        for w in on_workstations:
            if i in w:
                on_workstation = w
                break
        for j in range(on_workstation.index(i), len(on_workstation)):
            prev_end = result[i-2] + result[i-1]
            result[on_workstation[j]+1] = max(result[on_workstation[j]+1], prev_end)
print(values)
print(result)"""


"""test = [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]
l = [x for x in test if 0 in x]
print(l[0])
for i in range(l[0].index(2), len(l[0])):
    print(l[0][i])"""

"""import random
offspring = [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 2, 0, 3]
loop_count = 0
on_workstations = [(offspring[i], offspring[i+1]) for i in range(0, len(offspring), 2)]
for i in range(0, len(offspring), 2):
    workstation = offspring[i]
    conflicts_found = True
    while conflicts_found:
        loop_count += 1
        conflicts_found = False
        for j in range(0, len(offspring), 2):
            if i != j and offspring[j] == workstation:
                # check if sequence has a conflict
                if offspring[i+1] == offspring[j+1]:
                    conflicts_found = True
                    if random.random() < 0.5:
                        offspring[j+1] += 1
                    else:
                        offspring[i+1] += 1
on_workstations = [(offspring[i], offspring[i+1]) for i in range(0, len(offspring), 2)]
print(on_workstations)
on_zero = [x for x in on_workstations if x[0] == 0]
on_zero.sort(key=lambda x: x[1])
on_one = [x for x in on_workstations if x[0] == 1]
on_one.sort(key=lambda x: x[1])
print(on_zero)
print(on_one)
print(loop_count)
print(len(offspring))"""

"""def select_next_generation(population, population_fitness, offsprings, offspring_fitness):
    elitism_rate = int(len(population)/4)
    population_size = 10
    next_generation = []
    sorted_population = sorted(population, key=lambda x: population_fitness[population.index(x)])
    sorted_offsprings = sorted(offsprings, key=lambda x: offspring_fitness[offsprings.index(x)])
    population_fitness.sort()
    offspring_fitness.sort()
    next_generation = sorted_offsprings[:population_size]
    next_generation_fitness = offspring_fitness[:population_size]
    for i in range(elitism_rate):
        if population_fitness[i] >= next_generation_fitness[-i-1]:
            break
        next_generation[-i-1] = sorted_population[i]
        next_generation_fitness[-i-1] = population_fitness[i]
    return next_generation, next_generation_fitness

population = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
population_fitness = [18, 16, 14, 12, 10, 8, 6, 4, 2, 0]
offsprings = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]
offspring_fitness = [39, 37, 35, 33, 31, 29, 27, 25, 23, 21, 19, 17, 15, 13, 11, 9, 7, 5, 3, 1]
next_population, next_population_fitness = select_next_generation(population, population_fitness, offsprings, offspring_fitness)
print(next_population)
print(next_population_fitness)"""

#result = [0, 36, 0, 223, 1, 55, 0, 140, 3, 39, 0, 160, 7, 10, 0, 145, 0, 38, 0, 214, 1, 54, 0, 87, 4, 12, 0, 178, 4, 54, 0, 120, 0, 13, 0, 87, 6, 8, 0, 105, 5, 23, 0, 153, 7, 5, 0, 165, 0, 40, 0, 87, 2, 57, 0, 173, 3, 38, 0, 136, 5, 35, 0, 170, 0, 16, 0, 145, 4, 5, 0, 65, 1, 61, 0, 85, 5, 34, 0, 165, 3, 6, 0, 145, 3, 7, 0, 150, 6, 10, 0, 180, 3, 40, 0, 50, 2, 3, 0, 145, 4, 4, 0, 124, 6, 9, 0, 178, 7, 6, 0, 230, 3, 5, 0, 245, 5, 24, 0, 224, 4, 11, 0, 178, 6, 25, 0, 150, 2, 40, 0, 150, 2, 42, 0, 180, 6, 17, 0, 50, 7, 9, 0, 170, 2, 41, 0, 257, 5, 26, 0, 224, 6, 22, 0, 178, 7, 12, 0, 150, 1, 37, 0, 150, 3, 9, 0, 180, 6, 15, 0, 40, 5, 32, 0, 170, 1, 0, 0, 357, 4, 7, 0, 268, 6, 20, 0, 178, 4, 56, 0, 230]
#result = [0, 1, 0 10, 0, 0, 0, 15, 0, 2, 0, 10, 1, 4, 0, 10, 1, 0, 0, 5, 1, 2, 0, 10, 1, 3, 0, 15, 1, 1, 0, 10]
import random
def create_random_result(jobs : int = 10, workstations : int = 4):
    result = []
    count = [0] * workstations
    for i in range(jobs):
        w = random.randint(0, workstations-1)
        idx = 0
        if i > 0:
            idx = random.choice(range(0, len(result), 4))#int(random.randint(0, len(result)) / 4)
        #result.extend([w, count[w], 0, random.randint(10, 30)])
        result.insert(idx, w)
        result.insert(idx+1, count[w])
        result.insert(idx+2, 0)
        result.insert(idx+3, random.randint(10, 30))
        count[w] += 1
    return result

def get_indices_for_workstation(values, workstation):
    on_workstation = []
    for i in range(0, len(values), 4):
        if values[i] == workstation:
            on_workstation.append(i)
    return on_workstation

def right_shift(values : list[int], sequence_values : list[int], job_orders : list[int], workstation):
    on_workstation = get_indices_for_workstation(values, workstation)
    on_workstation.sort(key=lambda x: sequence_values[x+1])
    for i in range(len(on_workstation)):
        if i > 0:
            idx = on_workstation[i]
            prev_idx = on_workstation[i-1]
            values[idx+1] = max(values[idx+1], values[prev_idx+1]+values[prev_idx+3])
            # find and resolve sequence dependencies
            

def update_idx(values, job_orders, workstation, idx):
    w_prev = result[workstation[idx-1]+1] + result[workstation[idx-1]+3] if idx > 0 else 0 # end of previous operation on workstation
    job_idx = int(workstation[idx] / 4)
    s_prev = result[workstation[idx] - 3] + result[workstation[idx]-1] if job_idx > 0 and job_orders[job_idx] == job_orders[job_idx-1] else 0 # end of previous operation in sequence
    result[workstation[idx]+1] = max(w_prev, s_prev)


def determine_start_times(values : list[int], job_orders : list[int], workstations_amount):
    #repair 

    changes = True
    while changes:
        changes = False
        for i in range(4, len(values), 4):
            j = i
            while j >= 0 and job_orders[int(j/4)] == job_orders[int(i/4)]:
                if values[j] == values[i] and values[j+1] > values[i+1]:
                    tmp = values[i+1]
                    values[i+1] = values[j+1]
                    values[j+1] = tmp
                    changes = True
                    print('repaired')
                j -= 4
    result = values.copy()
    """
        Option 1:
            insert first on each workstation, resolve sequence dependencies
            insert second on each workstation, ...
    """
    """workstations = []
    for w in range(workstations_amount):
        on_workstation = get_indices_for_workstation(result, w)
        on_workstation.sort(key=lambda x: values[x+1])
        workstations.append(on_workstation)
    idx = 0
    while any(len(w) > idx for w in workstations):
        for i in range(len(workstations)):
            if len(workstations[i]) > idx:
                w_prev = result[workstations[i][idx-1]+1] + result[workstations[i][idx-1]+3] if idx > 0 else 0 # end of previous operation on workstation
                job_idx = int(workstations[i][idx] / 4)
                s_prev = result[workstations[i][idx] - 3] + result[workstations[i][idx]-1] if job_idx > 0 and job_orders[job_idx] == job_orders[job_idx-1] else 0 # end of previous operation in sequence
                result[workstations[i][idx]+1] = max(w_prev, s_prev)
        idx += 1
    
    return result"""
    """
        Option 2:
            insert first operation of first job, insert all jobs before on workstation
            ...
    """
    """
        Option 3:
            insert all to workstation
            resolve all dependencies starting from first on each workstation, right shift all on workstation after adjustments, move on to second on each workstation, ...
    """
    changes = True
    while changes:
        changes = False
        # workstation dependencies
        
        for w in range(workstations):
            on_workstation = get_indices_for_workstation(result, w)
            on_workstation.sort(key=lambda x: result[x+1])
            for i in range(len(on_workstation)):
                if i == 0:
                    result[on_workstation[i]+1] = 0
                else:
                    result[on_workstation[i]+1] = max(result[on_workstation[i]+1], result[on_workstation[i-1]+1] + result[on_workstation[i-1]+3])
        # job sequence dependencies
        for i in range(len(job_orders)):
            if i > 0:
                if job_orders[i] == job_orders[i-1]:
                    idx = i * 4
                    before = result[idx+1]
                    prev_idx = (i-1) * 4
                    result[idx+1] = max(result[idx+1], result[prev_idx+1] + result[prev_idx+3])
                    if before != result[idx+1]:
                        # right shift all on workstation
                        right_shift(result, values, job_orders, result[idx]) # NOTE: only shifting after sequence number would be more efficient, ignore for now
                        #changes = True
                    changes = before != result[idx+1]
    return result

orders = [0, 0, 0, 1, 1, 2, 2, 2, 2, 3]
workstations = 4
values = create_random_result(len(orders), workstations)
result = determine_start_times(values, orders, workstations)
print(values)
print(result)

import plotly.figure_factory as ff
from visualization import get_colors_distinctipy
def visualize_schedule(values, job_orders, workstations):
    data = []
    tasks = []
    for workstation in range(workstations):
        label = f'w{workstation}'
        on_workstation = get_indices_for_workstation(values, workstation)
        for idx in on_workstation:
            data.append(
                dict(Task=label, Start=values[idx+1], Finish=values[idx+1]+values[idx+3], Resource=f'Order {job_orders[int(idx/4)]}')
            )
    colors = {}
    #rgb_values = get_colors(len(orders))
    rgb_values = get_colors_distinctipy(len(orders))
    for i in range(len(orders)):
        colors[str(f'Order {i}')] = f'rgb({rgb_values[i][0] * 255}, {rgb_values[i][1] * 255}, {rgb_values[i][2] * 255})'
    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()

visualize_schedule(result, orders, workstations)