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

import matplotlib
import pylab
def visualizer(solution, job_operations):
    # assumed solution format:
    # <workstation, start_time, worker, duration>
    schedule_width = 6 #must be inches???
    schedule_height = 3.5
    # initialize plot & set basic elements
    fig = pylab.figure(figsize=[schedule_width, schedule_height], dpi=80) # 80 dots per inch
    ax = fig.gca()

    colors = matplotlib.cm.Dark2.colors

    jobs = []
    workstations = []
    # gather jobs and workstations
    for w in range(0, len(solution), 4):
        if w not in workstations:
            workstations.append(w)
    for j in range(0, len(job_operations)):
        if j not in jobs:
            jobs.append(j)
    for i in range(0, len(solution), 4):
        workstation = solution[i]
        start_time = solution[i+1]
        duration = solution[i+3]
        job = job_operations[int(i/4)]
        ax.broken_barh([(start_time, duration)], (workstation + 0.5, 0.9), facecolors=colors[job % len(jobs)], alpha=1)
        operation = 0
        j = i
        while job_operations[int(j/4)] == job_operations[int((j-1)/4)]:
            operation += 1
            j -= 1
        # add product name to center of bar
        ax.text((start_time + start_time + duration)/2, workstation + 0.9, f'J{job}O{operation}', {'ha':'center', 'va':'center', 'weight':'bold'})
    # set axis ticks, labels and grid
    ax.set_title("Schedule")
    ax.set_xlabel("Time",)
    ax.set_ylabel("Workstation")

    ax.set_yticks(range(1, 1+len(workstations)), labels=[f'w{i}' for w in workstations]) # set workstation names as ticks on y axis

    ax.grid(True, linewidth=0.1)
    matplotlib.pyplot.rcParams['hatch.linewidth'] = 0.2 # lower line width of hatch

    # remove margins around plot
    fig.tight_layout()

    fig.show()