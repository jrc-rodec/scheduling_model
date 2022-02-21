import matplotlib.pyplot as plt
import plotly.figure_factory as ff
def visualize(workstations):
    """start_times = []
    durations = []
    operations = []
    for i in range(len(result.genes)):
        machine = result.genes[0]
        worker = result.genes[1]
        operation_id, order = map_index_to_operation(i, orders, jobs)
        start_times.append(result.genes[i][2])
        durations.append(get_duration(machine, worker, operation_id, order[0], jobs))
        operations.append(f'Operation {i}')"""

    """fig, ax = plt.subplots(1, figsize=(16,6))
    labels = []
    durations = []
    start_times = []
    i = 0
    for workstation in workstations.keys():
        labels.append(f'w{i}')
        w_durations = []
        w_start_times = []
        for entry  in workstations[workstation]:
            w_durations.append(entry[2])
            w_start_times.append(entry[1])
        durations.append(w_durations)
        start_times.append(w_start_times)
        i+=1
    ax.barh(labels, durations, left=start_times)
    plt.show()"""

    data = []
    for workstation in workstations.keys():
        label = f'w{workstation}'
        for operation in workstations[workstation]:
            data.append(
                dict(Task=label, Start=operation[1], Finish=operation[1] + operation[2], Resource='None')
            )
    colors = {'None': 'rgb(220, 0, 0)',
            'Incomplete': (1, 0.9, 0.16),
            'Complete': 'rgb(0, 255, 100)'}

    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.show()
    """df = [dict(Task="Job-1", Start='2017-01-01', Finish='2017-02-02', Resource='Complete'),
        dict(Task="Job-1", Start='2017-02-15', Finish='2017-03-15', Resource='Incomplete'),
        dict(Task="Job-2", Start='2017-01-17', Finish='2017-02-17', Resource='Not Started'),
        dict(Task="Job-2", Start='2017-01-17', Finish='2017-02-17', Resource='Complete'),
        dict(Task="Job-3", Start='2017-03-10', Finish='2017-03-20', Resource='Not Started'),
        dict(Task="Job-3", Start='2017-04-01', Finish='2017-04-20', Resource='Not Started'),
        dict(Task="Job-3", Start='2017-05-18', Finish='2017-06-18', Resource='Not Started'),
        dict(Task="Job-4", Start='2017-01-14', Finish='2017-03-14', Resource='Complete')]"""