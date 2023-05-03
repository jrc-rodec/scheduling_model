solution = [1,7367,    1, 7592,    3, 7732,    7, 7882,    0, 7111,    2, 7520,    6, 7757,
    4, 7907,    0, 6961,    3, 7107,    4, 7212,    7, 7312,    0, 6629,    4, 6743,
    5, 6956,    5, 7857,    0, 6805,    6, 7004,    4, 7312,    5, 7677,    1, 7189,
    2, 7651,    4, 7787,    6, 7941,    2, 6770,    2, 6919,    6, 7091,    4, 7647,
    3, 6617,    4, 6923,    6, 7271,    6, 7455,    2, 6620,    2, 7084,    4, 7422,
    7, 7477,    3, 6862,    5, 7136,   5, 7361,    6, 7605,    1, 7039,    3, 7212,
    4, 7462,    5, 7526,    1, 6620,    2, 7264,    4, 7502,    7, 7652]

print(solution)

w_sorting : list[list[int]] = []
for workstation in [0,1,2,3,4,5,6,7]:
    w_sorting.append([])
    for i in range(0, len(solution), 2):
        if solution[i] == int(workstation):
            w_sorting[-1].append(i)
            """if len(w_sorting) == 0:
                w_sorting.append(i)
            else:
                for j in w_sorting[-1]:
                    if solution[w_sorting[-1][j]] < solution[i]:"""
    w_sorting[-1].sort(key= lambda x: solution[x+1])
print(w_sorting)
for sorting in w_sorting:
    print([solution[x+1] for x in sorting])
