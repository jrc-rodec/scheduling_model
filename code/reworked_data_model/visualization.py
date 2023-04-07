import plotly.figure_factory as ff
import random
from distinctipy import distinctipy
from model import ProductionEnvironment, Schedule, Assignment

def get_colors_distinctipy(n):
    return distinctipy.get_colors(n)

def get_colors(n): 
    ret = [] 
    r = int(random.random() * 256) 
    g = int(random.random() * 256) 
    b = int(random.random() * 256) 
    step = 256 / n 
    for _ in range(n): 
        r += step 
        g += step 
        b += step 
        r = int(r) % 256 
        g = int(g) % 256 
        b = int(b) % 256 
        ret.append((r,g,b))  
    return ret

def visualize_schedule(schedule : Schedule, environment : ProductionEnvironment, orders):
    data = []
    tasks = []
    workstations = schedule.assignments.keys()
    for workstation in workstations:
        label = f'w{workstation}'
        assignments : list[Assignment] = schedule.get_assignments_on_workstation(workstation)
        for assignment in assignments:
            data.append(
                dict(Task=label, Start=assignment.start_time, Finish=assignment.end_time, Resource=f'Order {assignment.job.order.id}') # not last part should be replaced with order id
            )
            if assignment.job.task not in tasks:
                tasks.append(assignment.job.task)
    colors = {}
    #rgb_values = get_colors(len(orders))
    rgb_values = get_colors_distinctipy(len(orders))
    for i in range(len(orders)):
        colors[str(f'Order {i}')] = f'rgb({rgb_values[i][0] * 255}, {rgb_values[i][1] * 255}, {rgb_values[i][2] * 255})'
    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()