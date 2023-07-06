import igraph
#jobs = [0, 0, 1, 1]
#values = [0, 1, 1, 0, 1, 1, 0, 0] # should contain a cycle, can't find a starting vertex = infeasible
#values = [0, 0, 1, 0, 0, 1, 1, 1] # should be acyclic = feasible
#workstations = [0, 1]
# contains a cycle, with possible starting vertex = infeasible
#values = [0, 0, 1, 1, 2, 0, 2, 2, 1, 0, 0, 1, 0, 2]
#jobs = [0, 0, 0, 1, 1, 2, 2]
#workstations = [0, 1, 2]
# Fattahi10 (Optimal Solution), acyclic = feasible solution
#values = [0, 1, 3, 0, 3, 2, 2, 0, 1, 2, 4, 1, 1, 1, 2, 2, 4, 2, 1, 0, 4, 0, 2, 4]
#workstations = [0, 1, 2, 3, 4]
#jobs = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]
# Fattahi 1
#values = [1, 0, 1, 1, 0, 0, 0, 1]
#jobs = [0, 0, 1, 1]
#workstations = [0, 1]
# ChambersBarnes 6
#values = [0, 0, 1, 0, 2, 0, 3, 1, 4, 5, 5, 5, 6, 4, 7, 2, 8, 0, 9, 0, 10, 1, 2, 5, 4, 3, 9, 3, 3, 4, 1, 6, 6, 0, 5, 0, 7, 4, 8, 1, 1, 3, 10, 2, 3, 0, 2, 1, 8, 2, 5, 4, 7, 2, 6, 4, 9, 3, 4, 5, 1, 7, 2, 5, 0, 3, 4, 6, 6, 2, 8, 3, 7, 4, 3, 4, 9, 5, 5, 7, 2, 4, 10, 0, 1, 6, 5, 3, 3, 7, 4, 1, 8, 6, 7, 6, 9, 3, 6, 5, 2, 7, 1, 4, 5, 2, 3, 5, 8, 6, 9, 4, 10, 3, 6, 4, 4, 3, 7, 5, 1, 5, 10, 4, 3, 3, 2, 6, 6, 1, 5, 5, 9, 1, 8, 7, 7, 1, 4, 0, 2, 3, 0, 3, 1, 1, 5, 7, 4, 7, 6, 6, 8, 5, 9, 6, 7, 7, 3, 6, 0, 2, 1, 2, 3, 8, 5, 6, 2, 2, 9, 2, 6, 3, 7, 0, 4, 4, 8, 8, 1, 8, 0, 1, 2, 8, 6, 7, 8, 4, 9, 7, 5, 1, 3, 2, 4, 2, 7, 3]   
#workstations = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#jobs = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
# Fattahi 20
values = [0, 87, 3, 8, 4, 16, 7, 21, 0, 88, 1, 23, 4, 20, 4, 23, 0, 71, 6, 4, 5, 8, 5, 30, 0, 68, 2, 12, 3, 12, 5, 53, 0, 92, 3, 13, 1, 26, 7, 22, 2, 9, 2, 10, 6, 7, 3, 20, 1, 7, 2, 11, 6, 9, 7, 20, 3, 6, 5, 31, 5, 54, 6, 22, 1, 24, 2, 25, 6, 17, 7, 23, 3, 3, 4, 3, 4, 12, 6, 11, 1, 11, 3, 19, 6, 15, 5, 56, 1, 9, 2, 13, 6, 14, 4, 24]
workstations = [0, 1, 2, 3, 4, 5, 6, 7]
jobs = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11]

starter_indices = [0] * len(workstations)
for i in range(len(workstations)):
    min = float('inf')
    for j in range(0, len(values), 2):
        if values[j] == workstations[i]:
            if min == float('inf') or values[j+1] < values[min+1]:
                min = j
    starter_indices[i] = min

open_list = []
edges = []
nodes = []
for index in starter_indices:
    if index != float('inf'):
        job_index = int(index/2)
        if job_index == 0 or jobs[job_index] != jobs[job_index-1] and index not in open_list:
            open_list.append(index)
closed_list = []
feasible = False
if len(open_list) > 0:
    feasible = True
    while len(open_list) > 0:
        current = open_list.pop(0)
        # add current node to closed list
        closed_list.append(current)
        job_index = int(current/2)
        if job_index < len(jobs)-1 and jobs[job_index] == jobs[job_index+1]:
            # a follow up operation exists
            edges.append((job_index, job_index+1))
            if current+2 not in closed_list:
                if current+2 not in open_list:
                    #open_list.insert(0, current+2) #DFS
                    open_list.append(current+2) #BFS

        # find smallest sequence number bigger than current's sequence number on the same workstation
        min = float('inf')
        for i in range(0, len(values), 2):
            if i != current and (values[current] == values[i] and values[i+1] > values[current+1] and (min == float('inf') or values[i+1] < values[min+1])):
                min = i
        if min != float('inf'):
            edges.append((job_index, int(min/2)))
            if min not in closed_list:
                if min not in open_list:
                    #open_list.insert(0, min) #DFS
                    open_list.append(min) #BFS

graph = igraph.Graph(directed=True, n=len(jobs), edges=edges)
feasible = feasible and graph.is_acyclic()

# visualize
import matplotlib.pyplot as plt

visual_style = {}
visual_style["vertex_label"] = [f'{i}' for i in range(len(jobs))]
print(graph.get_adjacency())
fig, ax = plt.subplots()

ax.set_title("Full Graph")
layout = graph.layout('kamada_kawai')
igraph.plot(graph, target=ax, layout=layout, **visual_style)

#print(graph.is_acyclic())
print(feasible)
plt.show()
