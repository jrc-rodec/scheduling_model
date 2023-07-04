import igraph
#jobs = [0, 0, 1, 1]
#values = [0, 1, 1, 0, 1, 1, 0, 0] # should contain a cycle, can't find a starting vertex = infeasible
#values = [0, 0, 1, 0, 0, 1, 1, 1] # should be acyclic = feasible
#workstations = [0, 1]
# contains a cycle, with possible starting vertex = infeasible
values = [0, 0, 1, 1, 2, 0, 2, 2, 1, 0, 0, 1, 0, 2]
jobs = [0, 0, 0, 1, 1, 2, 2]
workstations = [0, 1, 2]
# Fattahi10 (Optimal Solution), acyclic = feasible solution
#values = [0, 1, 3, 0, 3, 2, 2, 0, 1, 2, 4, 1, 1, 1, 2, 2, 4, 2, 1, 0, 4, 0, 2, 4]
#workstations = [0, 1, 2, 3, 4]
#jobs = [0, 0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3]

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
igraph.plot(graph, target=ax, **visual_style)

#print(graph.is_acyclic())
print(feasible)
plt.show()
