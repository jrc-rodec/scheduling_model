import plotly.figure_factory as ff
import random
import matplotlib.pyplot as plt
from solver import GASolver # temporary
from models import Schedule, SimulationEnvironment
from distinctipy import distinctipy
from itertools import permutations

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

def remap(value, from_lb, from_ub, to_lb, to_ub):
    oldRange = from_ub - from_lb
    newRange = to_ub - to_lb
    mapped = (((value - from_lb) * newRange) / oldRange) + to_lb
    return mapped

def plot_values_2D(x, y, x_label, y_label):
    ax = plt.figure().add_subplot()
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.scatter(x, y)
    plt.title(f'{x_label} and {y_label}')

def compare_2D(values, function_names, ignore):
    compared = []
    for i in range(len(values)):
        if ignore is not None and not i in ignore:
            for j in range(len(values)):
                if i != j and ignore is not None and not j in ignore and not (i, j) in compared and not (j, i) in compared:
                    plot_values_2D(values[i][0], values[j][0], function_names[i], function_names[j])
                    compared.append((i, j))

def plot_values_3D(x, y, z, x_label, y_label, z_label):
    ax = plt.figure().add_subplot(projection='3d')
    ax.scatter(x, y, z)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_zlabel(z_label)
    plt.title(f'{x_label} and {y_label} and {z_label}')

def compare_3D(values, function_names, ignore, results):
    compared = []
    for i in range(len(values)):
        if i not in ignore:
            for j in range(len(values)):
                if i != j and j not in ignore:
                    for k in range(len(values)):
                        if i != k and j != k and k not in ignore and not any([p in compared for p in permutations([i, j, k])]):
                            x = []
                            y = []
                            z = []
                            for _ in results:
                                x.append(values[i][0])
                                y.append(values[j][0])
                                z.append(values[k][0])
                            plot_values_3D(x, y, z, function_names[i], function_names[j], function_names[k])
                            compared.append((i, j, k))

def compare_results(results : list[tuple], function_names : list[str], remap_lb : int = 0, remap_ub : int = 10, ignore : list[int] = [], remap_values : bool = True) -> None:
    values : list[tuple[list[int],int,int]]= []
    f_values = []
    for i in range(len(function_names)):
        f_values.append([])
    min = len(function_names) * [float('inf')]
    max = len(function_names) * [-float('inf')]
    for i in range(len(results)): # for every solver result
        for j in range(len(function_names)):
            f_values[j].append(results[i][1][j])
            if results[i][1][j] > max[j]:
                max[j] = results[i][1][j]
            if results[i][1][j] < min[j]:
                min[j] = results[i][1][j]
    for i in range(len(f_values)):
        values.append((f_values[i], min[i], max[i]))
    
    #2D
    compare_2D(values, function_names, ignore)
    plt.show()

    if remap_values:
        remapped_values = []
        for i in range(len(values)):
            if i not in ignore:
                r_values = []
                for j in range(len(values[i][0])):
                    r_values.append(remap(values[i][0][j], values[i][1], values[i][2], remap_lb, remap_ub))
                remapped_values.append(r_values)
            else:
                remapped_values.append(values[i])
        remapped_names = [f'{name} (Remapped)' for name in function_names]
        compare_2D(remapped_values, remapped_names, ignore)
        plt.show()

    #3D
    compare_3D(values, function_names, ignore, results)
    plt.show()