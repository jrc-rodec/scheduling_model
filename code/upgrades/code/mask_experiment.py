ops = [3, 2, 4]
d = [
    [0, 7, 8, 3, 5],
    [5, 5, 6, 4, 0],
    [0, 0, 7, 8, 0],
    [4, 3, 0, 0, 6],
    [7, 0, 4, 0, 5],
    [5, 8, 5, 6, 8],
    [9, 4, 0, 5, 4],
    [6, 5, 5, 0, 5],
    [5, 6, 4, 4, 7]
     ]

linewidth = sum(ops)

j_repair = [
    0, 1, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 1, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 1, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 1, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 1, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 1,
    0, 0, 0, 0, 0, 0, 0, 0, 0,
]

negative_mask = [ # make sure no dependency on self or previous operations in job sequence
    0, 1, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 1, 1, 1, 1, 1, 1, 1,
    0, 0, 0, 1, 1, 1, 1, 1, 1,
    1, 1, 1, 0, 1, 1, 1, 1, 1,
    1, 1, 1, 0, 0, 1, 1, 1, 1,
    1, 1, 1, 1, 1, 0, 1, 1, 1,
    1, 1, 1, 1, 1, 0, 0, 1, 1,
    1, 1, 1, 1, 1, 0, 0, 0, 1,
    1, 1, 1, 1, 1, 0, 0, 0, 0,
]
def get_line(n, x):
    return x[n*linewidth:n*linewidth+linewidth]

def print_as_matrix(x):
    for i in range(int(len(x)/linewidth)):
        print(get_line(i, x))

for i in range(int(len(negative_mask)/linewidth)):
    print(get_line(i, negative_mask))
for i in range(0, len(j_repair), linewidth):
    print(j_repair[i:i+linewidth])

print(1 & 0)
print(1 | 0)
test_individual = [
    1, 1, 1, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 1, 0, 0, 0,
    1, 1, 1, 0, 0, 0, 0, 0, 0,
    1, 1, 1, 0, 0, 1, 0, 1, 0,
    1, 1, 1, 0, 0, 0, 0, 1, 0,
    1, 1, 1, 0, 1, 1, 0, 1, 0,
    1, 1, 1, 0, 0, 0, 0, 1, 0,
    1, 1, 1, 0, 0, 0, 0, 1, 0,
]

r1 = [test_individual[i] | j_repair[i] for i in range(len(test_individual))]#test_individual | j_repair
print_as_matrix(r1)
r2 = [r1[i] & negative_mask[i] for i in range(len(r1))]
print()
print_as_matrix(r2)