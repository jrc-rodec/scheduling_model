import matplotlib.pyplot as plt
import plotly.figure_factory as ff
import random
from optimizer_components import get_duration, map_index_to_operation
     
def get_colors(n): 
    ret = [] 
    r = int(random.random() * 256) 
    g = int(random.random() * 256) 
    b = int(random.random() * 256) 
    step = 256 / n 
    for i in range(n): 
        r += step 
        g += step 
        b += step 
        r = int(r) % 256 
        g = int(g) % 256 
        b = int(b) % 256 
        ret.append((r,g,b))  
    return ret 

def reformat_result(result, orders, workstations, recipes, tasks):
    workstation_assignments = dict()
    for i in range(len(result.genes)):
        operation = result.genes[i]
        if operation[1] not in workstation_assignments:
            workstation_assignments[operation[1]] = []
        _, order = map_index_to_operation(i, orders, recipes, tasks)
        workstation_assignments[operation[1]].append([order[2], order[0], i, operation[0], operation[2], get_duration(operation[0], operation[1], workstations)])
    return workstation_assignments

def visualize(workstations, history, avg_history, best_generation_history, feasible_gen):
    data = []
    orders = []
    for workstation in workstations.keys():
        label = f'w{workstation}'
        for operation in workstations[workstation]:
            data.append(
                dict(Task=label, Start=operation[4], Finish=operation[4] + operation[5], Resource=f'{operation[0]}')
            )
            if operation[0] not in orders:
                orders.append(operation[0])
    colors = {}
    rgb_values = get_colors(len(orders))
    for i in range(len(orders)):
        colors[str(orders[i])] = f'rgb({rgb_values[i][0]}, {rgb_values[i][1]}, {rgb_values[i][2]})'

    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.show()
    x = list(range(0, len(history)))
    plt.plot(x, history)
    plt.plot(x, avg_history, 'r')
    plt.axvline(x=feasible_gen, color='g')
    #plt.plot(x, best_generation_history, 'r+') # with elitism, current best is always part of current generation
    plt.legend(['Best Known Fitness', 'Average Generation Fitness', 'First Feasible Solution', 'Best Generation Fitness'])
    plt.xlabel = 'Generation'
    plt.ylabel = 'Fitness'
    plt.show()
