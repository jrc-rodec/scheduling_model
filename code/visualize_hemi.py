import matplotlib.pyplot as plt
import plotly.figure_factory as ff


import plotly.io as pio
pio.renderers.default='browser'

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
                dict(Task=label, Start=operation[4], Finish=operation[4] + operation[5], Resource='None', Order=str(operation[0]))
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
    
  ########### alternative gantt approach ########################
    
  
    from matplotlib.patches import Patch
 
    ws=list()
    st=list()
    du=list()
    co=list()
    c_dict = {'1':'#E64646', '2':'#631646', '3':'#34D05C', '4':'#34D0C3', '5':'#3475D0',\
                            '6':'#E64777', '7':'#E99646', '8':'#F1D11C', '9':'#E8D1C3', '0':'#6661D5'}
    for t in data:
        if t['Finish']-t['Start'] > 0:
            ws.append(t['Task'])
            du.append(t['Finish']-t['Start'])
            st.append(t['Start'])
            co.append(c_dict[t['Order']])
            
    
    fig, ax = plt.subplots(1, figsize=(16,6))
    ax.barh(ws,du,left=st,color=co)
    legend_elements = [Patch(facecolor=c_dict[i], label=i)  for i in c_dict]
    plt.legend(handles=legend_elements)
    plt.show()
    
    print([ws,st,du])