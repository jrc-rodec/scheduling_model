import matplotlib.pyplot as plt
import plotly.figure_factory as ff
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
    shades = 255 / len(orders)
    shade = 0
    for order in orders:
        colors[str(order)] = f'rgb({shade}, 0, 0)'
        shade += shades
    
    """    colors = {'None': 'rgb(220, 0, 0)',
            'Incomplete': (1, 0.9, 0.16),
            'Complete': 'rgb(0, 255, 100)'}"""

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