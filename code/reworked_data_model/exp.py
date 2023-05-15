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

import random
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
print(len(offspring))