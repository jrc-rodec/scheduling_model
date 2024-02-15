import matplotlib
import pylab
from distinctipy import distinctipy

def get_colors_distinctipy(n):
    return distinctipy.get_colors(n)

def get_operation_index(i, required_operations):
    idx = 0
    for j in range(len(required_operations)):
        if required_operations[j] == required_operations[i] and j < i:
            idx+=1
        if j>=i:
            break
    return idx
def visualizer_for_schedule(start_times, end_times, sequence, assignments, durations, required_operations, makespan, idle_time, queue_time, source, instance, pre_colors, title_prefix = ''):

    schedule_width = 10#6 #must be inches???
    schedule_height = 6#3.5
    # initialize plot & set basic elements
    fig = pylab.figure(figsize=[schedule_width, schedule_height], dpi=80) # 80 dots per inch
    ax = fig.gca()

    #colors = matplotlib.cm.Dark2.colors

    # gather jobs and workstations
    machines = [i for i in range(len(durations[0]))]
    jobs = []
    for i in range(len(required_operations)):
        if i not in jobs:
            jobs.append(required_operations[i])

    if not pre_colors:
        colors = get_colors_distinctipy(len(jobs))
    else:
        colors = pre_colors
    for i in machines:
        for j in range(len(assignments)):
            if assignments[j] == machines[i]:
                machine = assignments[j]
                start_time = start_times[j]
                end_time = end_times[j]
                job = required_operations[j]
                duration = durations[j][machine]
                ax.broken_barh([(start_time, duration)], (machine + 0.5, 0.9), facecolors=colors[job % len(jobs)], edgecolor='k', alpha=1)
                # add product name to center of bar
                ax.text((start_time + start_time + duration)/2, machine + 0.9, f'J{job}-{get_operation_index(j, required_operations)}', {'ha':'center', 'va':'center', 'weight':'bold'})
    ax.set_title(f'{title_prefix} | {source}-{instance} Result Schedule - Makespan: {makespan}, Idle-Time: {idle_time}, Queue-Time: {queue_time}')
    ax.set_xlabel("Time")
    ax.set_ylabel("Machine")


    ax.set_yticks(range(1, 1+len(machines)), labels=[f'm{w}' for w in machines]) # set workstation names as ticks on y axis

    ax.grid(True, linewidth=0.1)
    matplotlib.pyplot.rcParams['hatch.linewidth'] = 0.2 # lower line width of hatch

    # remove margins around plot
    fig.tight_layout()

    #fig.canvas.mpl_connect("motion_notify_event", hover)

    #pylab.show()