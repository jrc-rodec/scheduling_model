import matplotlib.pyplot as plt
import plotly.figure_factory as ff

import random
     
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

def visualize(workstations, history):

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
    plt.xlabel = 'Generation'
    plt.ylabel = 'Fitness'
    plt.show()
    """df = [dict(Task="Job-1", Start='2017-01-01', Finish='2017-02-02', Resource='Complete'),
        dict(Task="Job-1", Start='2017-02-15', Finish='2017-03-15', Resource='Incomplete'),
        dict(Task="Job-2", Start='2017-01-17', Finish='2017-02-17', Resource='Not Started'),
        dict(Task="Job-2", Start='2017-01-17', Finish='2017-02-17', Resource='Complete'),
        dict(Task="Job-3", Start='2017-03-10', Finish='2017-03-20', Resource='Not Started'),
        dict(Task="Job-3", Start='2017-04-01', Finish='2017-04-20', Resource='Not Started'),
        dict(Task="Job-3", Start='2017-05-18', Finish='2017-06-18', Resource='Not Started'),
        dict(Task="Job-4", Start='2017-01-14', Finish='2017-03-14', Resource='Complete')]"""