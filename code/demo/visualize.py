import plotly.figure_factory as ff
import random
from solver import GASolver # temporary
from models import Schedule, SimulationEnvironment
from distinctipy import distinctipy

def get_colors_distinctipy(n):
    return distinctipy.get_colors(n)

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

"""def visualize(data, orders):
    # data format: 0 - workstation, 1 - job id, 2 - start time, 3 - duration
    colors = {}
    rgb_values = get_colors(len(orders))
    for i in range(len(orders)):
        colors[str(f'Order {i}')] = f'rgb({rgb_values[i][0]}, {rgb_values[i][1]}, {rgb_values[i][2]})' # just ignore colors for now
    composed_data = []
    
    for i in range(len(data)):
        label = f'W{data[i][0]}'
        start = data[i][2]
        end = start + data[i][3]
        composed_data.append(
                    dict(Task=label, Start=start, Finish=end, Resource=f'Order {order_for_index[i]}')
                )
        #print(composed_data)
    fig = ff.create_gantt(composed_data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True, showgrid_x=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()
"""
def visualize_schedule_demo(schedule : Schedule, environment : SimulationEnvironment, orders):
    data = []
    tasks = []
    workstations = schedule.assignments.keys()
    for workstation in workstations:
        label = f'w{workstation}'
        for assignment in schedule.assignments_for(workstation):
            duration = environment.get_duration(assignment[0], workstation)
            data.append(
                dict(Task=label, Start=assignment[1], Finish=assignment[1] + duration, Resource=f'Order {assignment[2].id}') # not last part should be replaced with order id
            )
            if assignment[0] not in tasks:
                tasks.append(assignment[0])
    colors = {}
    #rgb_values = get_colors(len(orders))
    rgb_values = get_colors_distinctipy(len(orders))
    for i in range(len(orders)):
        colors[str(f'Order {i}')] = f'rgb({rgb_values[i][0] * 255}, {rgb_values[i][1] * 255}, {rgb_values[i][2] * 255})'
    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()

def get_order(index, env, orders):
    job_index = int(index/2)
    #job = instance.jobs[int(index/2)]
    sum = 0
    for order in orders:
        recipe = env.get_recipe_by_id(order.resources[0]) # currently where the recipe is stored, temporary
        if job_index < sum + len(recipe.tasks):
            return order
        sum += len(recipe.tasks)
    return orders[len(orders)-1]

def visualize_schedule_comparison(schedule : Schedule, environment : SimulationEnvironment, orders):
    data = []
    tasks = []
    workstations = schedule.assignments.keys()
    for workstation in workstations:
        label = f'w{workstation}'
        for assignment in schedule.assignments_for(workstation):
            duration = environment.get_duration(assignment[0], workstation)
            data.append(
                dict(Task=label, Start=assignment[1], Finish=assignment[1] + duration, Resource=f'Order {assignment[2]["id"]}') # not last part should be replaced with order id
            )
            if assignment[0] not in tasks:
                tasks.append(assignment[0])
    colors = {}
    rgb_values = get_colors(len(orders))
    for i in range(len(orders)):
        colors[str(f'Order {i}')] = f'rgb({rgb_values[i][0]}, {rgb_values[i][1]}, {rgb_values[i][2]})'
    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    fig.show()
