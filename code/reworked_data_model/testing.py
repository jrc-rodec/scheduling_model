# -*- coding: utf-8 -*-
"""
Created on Mon May 15 15:41:32 2023

@author: tst
"""

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Ubersetzer für Gantchart plotten von David
def prep_visualize_schedule(indiv):
    
    result = [0 for t in range(4*nb_tasks)]
    orders =  [0 for t in range(nb_tasks)]
    idx_r = 0
    idx_o = 0
    for j in range(nb_jobs):
        for o in range(nb_operations[j]):
            orders[idx_o] = j
            idx_o += 1
            mach = indiv['job_op__mach'][(j+1,o+1)]
            result[idx_r] = mach-1
            result[idx_r+1] = indiv['job_op__starttime'][(j+1,o+1)]
            result[idx_r+2] = 0
            result[idx_r+3] = job_op_mach__duration[(j+1,o+1,mach)]
            idx_r += 4
            
    """#TEST
    if 1==1:
        schedule_sorted_t, Cmax_t, job_op__mach_t, job_op__starttime_t = unfold_schedule(indiv["schedule"])
        #for debuging
        result_t = [0 for t in range(4*nb_tasks)]
        orders_t =  [0 for t in range(nb_tasks)]
        endtimes_t = [0 for t in range(nb_tasks)]
        idx_r_t = 0
        idx_o_t = 0
        
        for j in range(nb_jobs):
            for o in range(nb_operations[j]):
                orders_t[idx_o_t] = j
                mach_t = job_op__mach_t[(j+1,o+1)]
                result_t[idx_r_t] = mach_t-1
                result_t[idx_r_t+1] = job_op__starttime_t[(j+1,o+1)]
                result_t[idx_r_t+2] = 0
                result_t[idx_r_t+3] = job_op_mach__duration[(j+1,o+1,mach_t)]
                idx_r_t += 4
                endtimes_t[idx_o_t] = job_op__starttime_t[(j+1,o+1)] + job_op_mach__duration[(j+1,o+1,mach_t)]
                idx_o_t += 1
        
        if indiv["Cmax"] != Cmax_t:
            visualize_schedule(result_t, orders_t, nb_machines)
            visualize_schedule(result, orders, nb_machines)
            sfdgshgfgth = 0
            schedule_sorted_t, Cmax_t, job_op__mach_t, job_op__starttime_t = unfold_schedule(indiv["schedule"])
    """        
    visualize_schedule(result, orders, nb_machines)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Gantchart plotten von David
import plotly.figure_factory as ff # pip install plotly
import plotly.io as pio
pio.renderers.default = "browser"
from distinctipy import distinctipy # pip install distinctipy
def get_colors_distinctipy(n):
    return distinctipy.get_colors(n)

def get_indices_for_workstation(values, workstation):
    on_workstation = []
    for i in range(0, len(values), 4):
        if values[i] == workstation:
            on_workstation.append(i)
    return on_workstation

def visualize_schedule(values, job_orders, workstations):
    data = []
    #tasks = []
    for workstation in range(workstations):
        label = f'w{workstation}'
        on_workstation = get_indices_for_workstation(values, workstation)
        for idx in on_workstation:
            data.append(
                dict(Task=label, Start=values[idx+1], Finish=values[idx+1]+values[idx+3], Resource=f'Order {job_orders[int(idx/4)]}')
            )
    colors = {}
    #rgb_values = get_colors(len(job_orders))
    rgb_values = get_colors_distinctipy(len(job_orders))
    for i in range(len(job_orders)):
        colors[str(f'Order {i}')] = f'rgb({rgb_values[i][0] * 255}, {rgb_values[i][1] * 255}, {rgb_values[i][2] * 255})'
    fig = ff.create_gantt(data, colors=colors, index_col='Resource', show_colorbar=True,
                        group_tasks=True)
    fig.update_layout(xaxis_type='linear')
    
    fig.show()


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Obsolet wenn der Machine Array immer in der selben Reihenfolge
def get_nb_suitablemachs(schedule,job_op__nb_machines):
    nb_suitablemachs = [0 for k in range(len(schedule))]
    op_h = [1 for k in range(max(schedule))]
    for k in range(len(schedule)):
        jh = schedule[k]
        nb_suitablemachs[k] = job_op__nb_machines[jh,op_h[jh-1]]
        op_h[jh-1] += 1
        
    return nb_suitablemachs
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Roulette Weel Selection
def selection_roulette(x):
    intmax = len(x)
    w = [x[k]['fitness'] for k in range(intmax)]
    wmax = max(w)
    w[:] = [x/wmax for x in w]
    notaccepted = True
    while notaccepted:
        int = rng.integers(0,intmax)
        
        if rng.random() < w[int]:
            notaccepted = False
            return x[int], int
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Rankbased Selection
def selection_rankbased(x):
    intmax = len(x)
    w = [(intmax-k)/intmax for k in range(intmax)]
    notaccepted = True
    
    while notaccepted:
        int = rng.integers(0,intmax)
        
        if rng.random() < w[int]:
            notaccepted = False
            return x[int], int
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    
#Tournament selection
def selection_tournament(x,ts):
    #x...population
    #ts...tournament size
    intmax = len(x)
    ints = list(rng.integers(0,intmax,ts))
    ints.sort(key = lambda k : x[k]['Cmax'])
    
    return x[ints[0]], ints[0]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#calculate fitness
def get_fitness(x):
    fitness = 1/x['Cmax']
    return fitness
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Crossover nach Nouri, Driss, Ghedira 2018
def crossover(parent1,parent2):
    
    parent1_sequence = parent1['schedule'][0]
    parent1_mach = parent1['schedule'][1]
    
    parent2_sequence = parent2['schedule'][0]
    parent2_mach = parent2['schedule'][1]
    
    #uniform machine crossover
    child1_mach = [0] * nb_tasks
    child2_mach = [0] * nb_tasks
    child1_mach[:] = parent1_mach
    child2_mach[:] = parent2_mach
    
    choice = rng.integers(2, size=len(parent1_mach))
    
    for k in range(len(choice)):
        if choice[k] == 1:
            child1_mach[k] = parent2_mach[k]
            child2_mach[k] = parent1_mach[k]
            
    #iPOX Crossover for sequence 
    nb_jobs1 = rng.integers(1,nb_jobs)
    jobset1 = set(rng.integers(1,nb_jobs+1,size = nb_jobs1))
    
    nb_jobs2 = rng.integers(1,nb_jobs)
    jobset2 = set(rng.integers(1,nb_jobs+1,size = nb_jobs2))
    
    child1_sequence = [0] * nb_tasks
    child2_sequence = [0] * nb_tasks
    child1_sequence[:] = parent1_sequence
    child2_sequence[:] = parent2_sequence
    
    parent2_minus_jobset1 = [ j for j in parent2_sequence if j not in jobset1 ]
    parent1_minus_jobset2 = [ j for j in parent1_sequence if j not in jobset2 ]
    for k in range(len(child1_sequence)):
        if child1_sequence[k] not in jobset1:
            child1_sequence[k] = parent2_minus_jobset1[0]
            parent2_minus_jobset1.pop(0)
        if child2_sequence[k] not in jobset2:
            child2_sequence[k] = parent1_minus_jobset2[0]
            parent1_minus_jobset2.pop(0)
            
    child1_schedule, Cmax1, job_op__mach1, job_op__starttime1 = unfold_schedule([child1_sequence,child1_mach])
    child2_schedule, Cmax2, job_op__mach2, job_op__starttime2 = unfold_schedule([child2_sequence,child2_mach])
    
    child1 ={'schedule': child1_schedule, 
             'Cmax': Cmax1,
             'job_op__mach': job_op__mach1,
             'job_op__starttime': job_op__starttime1}
    child1['fitness'] = get_fitness(child1)
    
    child2 ={'schedule': child2_schedule, 
             'Cmax': Cmax2,
             'job_op__mach': job_op__mach2,
             'job_op__starttime': job_op__starttime2}
    child2['fitness'] = get_fitness(child2)
    return child1, child2

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#HyperMutation nach Rhoshanaei e.a. 2013: Simulated annealing
def hypermutation(x):
    # x ... individual
    
    nb_machs_local = 10 #10
    #nb_schedules_at_T = 5 #15
    nb_iterations = 2
    
    #parameter for SA
    ini_T = 20
    alpha = 0.8
    n_T = 7
    
    T = ini_T
    best_indiv = x.copy()
    for n in range(nb_iterations):
        y = mutation(x, 1)
        for t in range(n_T):
            y_temp = y.copy()
            for k in range(nb_machs_local):
                indiv = mutation(y, 0)
                if indiv['Cmax'] < y_temp['Cmax']:
                    y_temp = indiv.copy()
            if y_temp['Cmax'] <= y['Cmax'] or rng.random() < np.exp(-(y_temp['Cmax'] - y['Cmax'])/T):
                y = y_temp.copy()
            
            if y['Cmax'] <= best_indiv['Cmax']:
                best_indiv = y.copy()
                
            T = alpha*T
        T = ini_T
            
    return best_indiv

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Exact optimisation when machine vector is fixed
def milp_opt(mach,timelimit):
    # mach: machine vector, job_op__suitablemachines, nb_jobs, nb_operations, job_op__tuple als globale var notwendig
    # initialize optimization    
    
    m = gp.Model('milp_opt')
    
    #list of jobs for creating Variables
    jobs = [j for j in range(1,nb_jobs+1)]
    
    #list of Job Operations for creating Variables
    job_ops = [(j+1,k+1) for j in range(nb_jobs) for k in range(nb_operations[j])] 
    
    #dict of selected machines
    job_op__mach = {}
    job_op__duration = {}
    for j, k in job_ops :
        h = job_op__tuple.index((j,k))
        machine = job_op__suitablemachines[j,k][mach[h]]
        job_op__mach[j,k] = machine
        job_op__duration[j,k] = job_op_mach__duration[j,k,machine]
    
    #big M
    L = sum(job_op__duration[j,k] for j, k in job_ops)
    
    #list for creating x Variables list_X_var=[(0,0,0,0)]
    list_X_var = []
    for j, k in job_ops :
        if j < nb_jobs :
            for jp, kp in job_ops:
                if jp > j:
                    if job_op__mach[j,k] == job_op__mach[jp,kp] :
                        list_X_var.append((j,k,jp,kp))
      
    # Variables
    X = m.addVars(list_X_var, obj = 0.0, vtype=gp.GRB.BINARY, name ="X")
    S = m.addVars(job_ops,  obj = 0.0, lb = 0.0, vtype=gp.GRB.CONTINUOUS, name ="S")
    Cmax = m.addVar(obj = 1.0, name="Cmax")
    
    #Constraints
    
    m.addConstrs((S[j,k] >= S[j,k-1] + job_op__duration[j,k-1] 
                  for j, k in job_ops if k >= 2)
                 ,"Order")
    m.addConstrs((S[jp,kp] + job_op__duration[jp,kp] <= S[j,k] + L*(1 - X[j,k,jp,kp]) 
                  for j, k in job_ops if j < nb_jobs
                  for jp, kp in job_ops if jp > j 
                  if job_op__mach[j,k] == job_op__mach[jp,kp])
                 , "Mach1")
    m.addConstrs((S[j,k] + job_op__duration[j,k] <= S[jp,kp] + L*X[j,k,jp,kp]
                  for j, k in job_ops if j < nb_jobs
                  for jp, kp in job_ops if jp > j 
                  if job_op__mach[j,k] == job_op__mach[jp,kp])
                 , "Mach2")
    """m.addConstrs((X[j,k,jp,kp] + X[jp,kp,j,k] == 1 
                  for j, k in job_ops if j < nb_jobs
                  for jp, kp in job_ops if jp > j
                  if job_op__mach[j,k] == job_op__mach[jp,kp])
                 , "Mach2alt")"""
    m.addConstrs((Cmax >= S[j,nb_operations[j-1]] + job_op__duration[j,nb_operations[j-1]] 
                  for j in jobs)
                 ,"Cmax")

    #Optimization  
    m.Params.TimeLimit = timelimit
    m.Params.LogToConsole = 0
    m.update()
    #m.display()
    m.optimize()
        
    #Output
    ssol = m.getAttr('X', S)  
    print("status = {}\n".format(m.status)) 
    
    if 1==0 :
        result = [0 for t in range(4*nb_tasks)]
        orders =  [0 for t in range(nb_tasks)]
        idx_r = 0
        idx_o = 0
        for j in range(nb_jobs):
            for o in range(nb_operations[j]):
                orders[idx_o] = j
                idx_o += 1
                
                result[idx_r] = job_op__mach[(j+1,o+1)]-1
                result[idx_r+1] = ssol[(j+1,o+1)]
                result[idx_r+2] = 0
                result[idx_r+3] = job_op__duration[(j+1,o+1)]
                idx_r += 4        
        visualize_schedule(result, orders, nb_machines)

    helper = sorted(sorted(ssol.items(), key = lambda item : item[0]), key = lambda item : item[1])
    sequence = [helper[k][0][0] for k in range(len(helper))]
    schedule = list((sequence,mach))  
    
    opt_schedule, Cmax, job_op__mach, job_op__starttime = unfold_schedule(schedule)
    indiv ={'schedule': opt_schedule, 
             'Cmax': Cmax,
             'job_op__mach': job_op__mach,
             'job_op__starttime': job_op__starttime}
    indiv['fitness'] = get_fitness(indiv)
    return indiv

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Mutation nach Nouri, Driss, Ghedira 2018
def mutation(indiv,typ):
    # indiv ... individual
    # typ ... = 0 Machine Vektor Mutation ... = 1 Sequence Vektor Mutation  ...= Both   
    if typ == 0: #machine vector mutation
        mach = [0] * nb_tasks
        mach[:] = indiv['schedule'][1]
        
        helper = [job_op__tuple.index((j+1,o+1)) 
             for j in range(nb_jobs) for o in range(nb_operations[j]) 
             if job_op__nb_machines[j+1,o+1] > 1]
        
        int1 = rng.integers(0,len(helper))
        idx_helper = helper[int1]
        
        mach_helper = [m for m in range(nb_suitablemachs[idx_helper]) if m != mach[idx_helper]]
        
        int2 = rng.integers(0,len(mach_helper))
        
        mach[idx_helper] = mach_helper[int2] #rng.integers(0,nb_suitablemachs[idx_helper])
        indiv_mut_schedule, Cmax, job_op__mach, job_op__starttime = unfold_schedule([indiv['schedule'][0],mach])
        
    elif typ == 2: #sequence vector mutation
        sequ = [0] * nb_tasks
        sequ[:] = indiv['schedule'][0]
        intmax = len(sequ)
        int1 = rng.integers(0,intmax)
        int2 = rng.integers(0,intmax)
        while int1 == int2:
            int2 = rng.integers(0,intmax)
        h = sequ[int1]
        sequ[int1] = sequ[int2]
        sequ[int2] = h
        indiv_mut_schedule, Cmax, job_op__mach, job_op__starttime = unfold_schedule([sequ,indiv['schedule'][1]])
        
    else: #typ = 3
        mach = [0] * nb_tasks
        mach[:] = indiv['schedule'][1]
        
        helper = [job_op__tuple.index((j+1,o+1)) 
             for j in range(nb_jobs) for o in range(nb_operations[j]) 
             if job_op__nb_machines[j+1,o+1] > 1]
        
        int1 = rng.integers(0,len(helper))
        idx_helper = helper[int1]
        mach_helper = [m for m in range(nb_suitablemachs[idx_helper]) if m != mach[idx_helper]]
        int2 = rng.integers(0,len(mach_helper))
        mach[idx_helper] = mach_helper[int2]
        
        sequ = [0] * nb_tasks
        sequ[:] = indiv['schedule'][0]
        intmax = len(sequ)
        int1 = rng.integers(0,intmax)
        int2 = rng.integers(0,intmax)
        while int1 == int2:
            int2 = rng.integers(0,intmax)
        h = sequ[int1]
        sequ[int1] = sequ[int2]
        sequ[int2] = h
        indiv_mut_schedule, Cmax, job_op__mach, job_op__starttime = unfold_schedule([sequ,mach])
    
    indiv_mut ={'schedule': indiv_mut_schedule, 
                'Cmax': Cmax,
                'job_op__mach': job_op__mach,
                'job_op__starttime': job_op__starttime}
    indiv_mut['fitness'] = get_fitness(indiv_mut)
      
    return indiv_mut
     
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Compute the dissimlarity;siehe Nouri, Driss, Ghedira 2018
def get_dissimilarity(x1,x2):
    sequence1 = x1[0]
    mach1 = x1[1]
    
    sequence2 = x2[0]
    mach2 = x2[1]
    
    dissimilarity = 0
    
    for k in range(len(sequence1)):
        if mach1[k] != mach2[k]:
            dissimilarity += nb_suitablemachs[k]
            
        if sequence1[k] != sequence2[k]:
            dissimilarity += 1
    return dissimilarity
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Unfold Schedule
def unfold_schedule(x):
    
    sequence = x[0]
    mach = x[1]
    
    Cmax = 0
    
    job_op__mach = {}
    #job_op__mach_idx = {} # Obsolet wenn der Machine Array immer in der selben Reihenfolge
    job_op__starttime = {}
    job_op__endtime = {}
    
    akt_op = [1 for k in range(nb_jobs)]
    
    #machine idle intervalls
    mach__idle_times = {}
    
    for k in range(nb_machines):
        mach__idle_times[k+1] = [[0, L]]
        
    for k in range(len(sequence)):
        job = sequence[k]
        operation = akt_op[job-1]
        
        h = job_op__tuple.index((job,operation))
        machine = job_op__suitablemachines[job,operation][mach[h]]
        job_op__mach[job,operation] = machine
        #job_op__mach_idx[job,operation] = mach[k] # Obsolet wenn der Machine Array immer in der selben Reihenfolge
        
        for l in range(len(mach__idle_times[machine])):
            idle_start = mach__idle_times[machine][l][0]
            idle_end = mach__idle_times[machine][l][1]
            
            if operation == 1:
                akt_start = idle_start
                akt_end = akt_start + job_op_mach__duration[job,operation,machine]
                
                if  akt_end < idle_end:
                    job_op__starttime[job,operation] = akt_start
                    job_op__endtime[job,operation] = akt_end
                    mach__idle_times[machine][l] = [akt_end,idle_end]
                    akt_op[job-1] += 1
                    break
                elif akt_end == idle_end:
                    job_op__starttime[job,operation] = akt_start
                    job_op__endtime[job,operation] = akt_end
                    mach__idle_times[machine].pop(l)
                    akt_op[job-1] += 1
                    break
            
            else : #operation > 1
                akt_start = max(idle_start,job_op__endtime[job,operation-1])
                akt_end = akt_start + job_op_mach__duration[job,operation,machine]
            
                if akt_start == idle_start and akt_end == idle_end:
                    job_op__starttime[job,operation] = akt_start
                    job_op__endtime[job,operation] = akt_end
                    mach__idle_times[machine].pop(l)
                    akt_op[job-1] += 1
                    break
                if  akt_start == idle_start and akt_end < idle_end:
                    job_op__starttime[job,operation] = akt_start
                    job_op__endtime[job,operation] = akt_end
                    mach__idle_times[machine][l] = [akt_end,idle_end]
                    akt_op[job-1] += 1
                    break
                if  akt_start > idle_start and akt_end == idle_end:
                    job_op__starttime[job,operation] = akt_start
                    job_op__endtime[job,operation] = akt_end
                    mach__idle_times[machine][l] = [idle_start,akt_start]
                    akt_op[job-1] += 1
                    break
                if  akt_start > idle_start and akt_end < idle_end:
                    job_op__starttime[job,operation] = akt_start
                    job_op__endtime[job,operation] = akt_end
                    mach__idle_times[machine][l] = [idle_start,akt_start]
                    mach__idle_times[machine].insert(l+1,[akt_end,idle_end])
                    akt_op[job-1] += 1
                    break
    Cmax = max(job_op__endtime[j+1,o+1] for j in range(nb_jobs) for o in range(nb_operations[j])) 
    
    helper = sorted(sorted(job_op__starttime.items(), key = lambda item : item[0]), key = lambda item : item[1])
    sequence_sorted = [helper[k][0][0] for k in range(len(helper))]
    #mach_sorted = [job_op__mach_idx[helper[k][0]] for k in range(len(helper))] #Obsolet wenn der Machine Array immer in der selben Reihenfolge
    schedule_sorted = list((sequence_sorted,mach))
        
    
    return schedule_sorted, Cmax, job_op__mach, job_op__starttime#, job_op__endtime

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
#Erzeuge neue Generation
def get_new_generation(population):
    
    offspring = []
    offspring[:] = population[0:anzbest]
    while len(offspring) < offspringsize:
        parent1, _ = selection_tournament(population,2)
        parent2, _ = selection_rankbased(population)
        #parent1, _ = selection_roulette(population)
        #parent2, _ = selection_roulette(population)
        #parent1, _ = selection_tournament(population,2)
        #parent2, _ = selection_tournament(population,2)
        
        counter = 0
        while parent2 == parent1 and counter < popsize:
            parent2, _ = selection_rankbased(population)
            #parent2, _ = selection_roulette(population)
            #parent2, _ = selection_tournament(population,2)
            counter += 1
            
        child1, child2 = crossover(parent1, parent2)
        #typ = rng.integers(2)
        #child3 = mutation(child1,typ)
        #child4 = mutation(child2, not typ)
        #child3 = mutation(child1, 3)
        #child4 = mutation(child2, 3)
        
        child3 = hypermutation(child1)
        child4 = hypermutation(child2)
        child1 = hypermutation(parent1)
        child2 = hypermutation(parent2)
        offspring.extend([child1, child2, child3, child4])

    offspring.sort(key = lambda x: x['Cmax']) 
    
    if 1==0:
        for k in range(popsize-1,1,-1):
            for i in range(k):
                if offspring[k]['schedule'] == offspring[i]['schedule']:
                    offspring.pop(k)
        k = len(offspring)
        while k < popsize:
            sequ = [i+1 for i in range(nb_jobs) for j in range(nb_operations[i])]
            rng.shuffle(sequ)
            mach = [rng.integers(0,nb_suitablemachs[k]) for k in range(nb_tasks)]
            schedule = list((sequ,mach))
            schedule_sorted, Cmax, job_op__mach, job_op__starttime = unfold_schedule(schedule)
            indiv = {"schedule": schedule_sorted,
                     "Cmax": Cmax,
                     'job_op__mach': job_op__mach,
                     'job_op__starttime': job_op__starttime}
            indiv["fitness"] = get_fitness(indiv)
            offspring[k] = hypermutation(indiv)
            k += 1
        offspring.sort(key = lambda x: x['Cmax'])
    
    
    return offspring[0:popsize]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%   
#Erzeuge neue Generation Versuch 1
def get_new_generation_1(population):
    
    offspring = []
    offspring[:] = population[0:anzbest]
    while len(offspring) < offspringsize:
        parent1, _ = selection_tournament(population,10)
        parent2, _ = selection_rankbased(population)
        #parent1, _ = selection_roulette(population)
        #parent2, _ = selection_roulette(population)
        #parent1, _ = selection_tournament(population,2)
        #parent2, _ = selection_tournament(population,2)
        
        counter = 0
        while parent2 == parent1 and counter < popsize:
            parent2, _ = selection_rankbased(population)
            #parent2, _ = selection_roulette(population)
            #parent2, _ = selection_tournament(population,2)
            counter += 1
            
        parent1_mach = parent1['schedule'][1]
        parent2_mach = parent2['schedule'][1]
        
        #uniform machine crossover
        child1_mach = [0] * nb_tasks
        child2_mach = [0] * nb_tasks
        child1_mach[:] = parent1_mach
        child2_mach[:] = parent2_mach
        
        choice = rng.integers(2, size=len(parent1_mach))
        
        for k in range(len(choice)):
            if choice[k] == 1:
                child1_mach[k] = parent2_mach[k]
                child2_mach[k] = parent1_mach[k]
        
        #machine vector mutation child1_mach
        helper = [job_op__tuple.index((j+1,o+1)) 
             for j in range(nb_jobs) for o in range(nb_operations[j]) 
             if job_op__nb_machines[j+1,o+1] > 1]
        
        child3_mach = [0] * nb_tasks
        child3_mach[:] = parent1_mach
        #child3_mach[:] = child1_mach
        int1 = rng.integers(0,len(helper))
        idx_helper1 = helper[int1]
        mach_helper1 = [m for m in range(nb_suitablemachs[idx_helper1]) if m != child3_mach[idx_helper1]]
        int1_1 = rng.integers(0,len(mach_helper1))
        child3_mach[idx_helper1] = mach_helper1[int1_1]
        
        #machine vector mutation child2_mach
        child4_mach = [0] * nb_tasks
        child4_mach[:] = parent2_mach
        #child4_mach[:] = child2_mach
        int2 = rng.integers(0,len(helper))
        idx_helper2 = helper[int2]
        mach_helper2 = [m for m in range(nb_suitablemachs[idx_helper2]) if m != child4_mach[idx_helper2]]
        int2_1 = rng.integers(0,len(mach_helper2))
        child4_mach[idx_helper2] = mach_helper2[int2_1]
        
        child1 = milp_opt(child1_mach,timelimit)
        child2 = milp_opt(child2_mach,timelimit)
        child3 = milp_opt(child3_mach,timelimit)
        child4 = milp_opt(child4_mach,timelimit)
        
        offspring.extend([child1, child2, child3, child4])

    offspring.sort(key = lambda x: x['Cmax']) 
    
    return offspring[0:popsize]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Heuristic nach Roshanaei e.a.: Matematical modelling and a meta-heuristic for F-JJSP und teilweise siehe Nouri, Driss, Ghedira 2018
import numpy as np
rng = np.random.default_rng()
import gurobipy as gp # Import des Gurobi-Pythonpakets
#import matplotlib.pyplot as plt
import datetime
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Einlesen von FJSSP without workers
if 1==1:
#read and arrange Data

    f = open(r'C:\Users\huda\Documents\GitHub\scheduling_model\code\external_test_data\FJSSPinstances\6_Fattahi\Fattahi20.fjs')
    lines = f.readlines()
    first_line = lines[0].split()
    # Number of jobs
    nb_jobs = int(first_line[0])
    
    # Number of machines
    nb_machines = int(first_line[1])
    
    # Number of operations for each job
    nb_operations = [int(lines[j + 1].split()[0]) for j in range(nb_jobs)] 
    
    # Number of tasks
    nb_tasks = sum(nb_operations[j] for j in range(nb_jobs))
    
    #Duration
    job_op_mach__duration = {}
    #Suitable machines
    job_op__suitablemachines = {}
    #nb of Machines
    job_op__nb_machines = {}
    #Indexdarstellung der Job_Ops
    job_op__idx ={}
    
    # Constant for incompatible machines
    INFINITE = 1000000
    # Processing time for each task, for each machine
    task_processing_time = [[[INFINITE for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]
    idx = 0
    
    for j in range(nb_jobs):
        line = lines[j + 1].split()
        tmp = 0
        for o in range(nb_operations[j]):
            nb_machines_operation = int(line[tmp + o + 1])
            suitable_helper =[]
            for i in range(nb_machines_operation):
                machine = int(line[tmp + o + 2 * i + 2])
                time = int(line[tmp + o + 2 * i + 3])
                task_processing_time[j][o][machine-1] = time
                suitable_helper += [machine]
                job_op_mach__duration[j+1,o+1,machine] = time
                
            job_op__suitablemachines[j+1,o+1] = suitable_helper
            job_op__nb_machines[j+1,o+1] = nb_machines_operation
            job_op__tuple = tuple(job_op__nb_machines.keys())
            tmp = tmp + 2 * nb_machines_operation
    # Trivial upper bound for the start times of the tasks
    L=0
    for j in range(nb_jobs):
        for o in range(nb_operations[j]):
            L += max(task_processing_time[j][o][m] for m in range(nb_machines) if task_processing_time[j][o][m] != INFINITE)
            
    #Max Distance of schedules
    distmax = nb_tasks + sum(job_op__nb_machines[job_ops] for job_ops in job_op__tuple)
    
    #Anzahl der einsetzbaren Maschinen für jede job_op in schedule Schreibweise
    nb_suitablemachs = [job_op__nb_machines[job_op__tuple[k]] for k in range(nb_tasks)]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Einlesen von FJSSP with workers   
if 1==0:
#read and arrange Data
    #Small Size Data: SFJW-01.txt to SFJW-10.txt
    #f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\MO-FJSPW_BenchmarkDataInstances\SFJW\SFJW-10.txt')
    #Medium size Data: MFJW-01.txt to MFJW-07.txt
    f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\MO-FJSPW_BenchmarkDataInstances\MFJW\MFJW-02.txt')
    
    lines = f.readlines()
    first_line = lines[0].split()
    # Number of jobs
    nb_jobs = int(first_line[0])
    # Number of machines
    nb_machines = int(first_line[1])
    # Number of workers
    nb_workers = int(first_line[2])
    # Number of operations for each job
    nb_operations = [int(lines[j + 1].split()[0]) for j in range(nb_jobs)]
    
    
    # Number of tasks
    nb_tasks = sum(nb_operations[j] for j in range(nb_jobs))
    
    #Duration
    job_op_mach_worker__duration = {}
    #Suitable machines
    job_op__suitablemachines = {}
    #nb of Machines
    job_op__nb_machines = {}
    #Suitable workers
    job_op_mach__suitableworkers = {}
    #nb_workers
    job_op_mach__nb_workers = {}
    
    for j in range(nb_jobs):
        line = lines[j + 1].split()
        tmp_idx = 1
        for o in range(nb_operations[j]):
            nb_machines_operation = int(line[tmp_idx])
            tmp_idx += 1
            suitable_machine_helper = []
            for i in range(nb_machines_operation):
                machine = int(line[tmp_idx])
                suitable_machine_helper += [machine]
                nb_m_workers = int(line[tmp_idx + 1])
                tmp_idx += 2
                suitable_worker_helper = []
                for s in range(nb_m_workers):
                    worker = int(line[tmp_idx])
                    time = int(line[tmp_idx + 1])
                    tmp_idx += 2
                    suitable_worker_helper += [worker]
                    job_op_mach_worker__duration[j+1,o+1,machine,worker] = time
                
                job_op_mach__suitableworkers[j+1,o+1,machine] = suitable_worker_helper
                job_op_mach__nb_workers[j+1,o+1,machine] = nb_m_workers
                
            job_op__suitablemachines[j+1,o+1] = suitable_machine_helper
            job_op__nb_machines[j+1,o+1] = nb_machines_operation
            job_op__tuple = tuple(job_op__nb_machines.keys())

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Heuristic Algo

#Anzahl Indiv in Population
popsize = 20 * nb_jobs
#Minimale Distanz der Startpopulation (Anteil von maxdist)
minstartdist = 1
maxstartiter = 1 * popsize
#Einstellungen für Offspring 
offspringsize = 1 * popsize
anzbest = 1

timelimit = nb_tasks

#Erzeuge Startpopulation %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
print(datetime.datetime.now())
sequ = [i+1 for i in range(nb_jobs) for j in range(nb_operations[i])]
rng.shuffle(sequ)
mach = [rng.integers(0,nb_suitablemachs[k]) for k in range(nb_tasks)]
schedule = list((sequ,mach))
schedule_sorted, Cmax, job_op__mach, job_op__starttime = unfold_schedule(schedule)
indiv = {"schedule": schedule_sorted,
         "Cmax": Cmax,
         'job_op__mach': job_op__mach,
         'job_op__starttime': job_op__starttime}
indiv["fitness"] = get_fitness(indiv)

population = [indiv]
popsize_act = len(population)
iteration = 0

while popsize_act < popsize:
    if iteration < maxstartiter:
        iteration +=1
    else:
        iteration = 0
        minstartdist /= 2
    sequ = [i+1 for i in range(nb_jobs) for j in range(nb_operations[i])]
    rng.shuffle(sequ)
    mach = [rng.integers(0,nb_suitablemachs[k]) for k in range(nb_tasks)]
    
    schedule = list((sequ,mach))
    schedule_sorted, Cmax, job_op__mach, job_op__starttime = unfold_schedule(schedule)
    
    dist = [0] * popsize_act
    for k in range(popsize_act):
        dist[k] = get_dissimilarity(schedule_sorted,population[k]['schedule'])
    if min(dist)/distmax >= minstartdist:
        indiv = {"schedule": schedule_sorted,
                 "Cmax": Cmax,
                 'job_op__mach': job_op__mach,
                 'job_op__starttime': job_op__starttime}
        indiv["fitness"] = get_fitness(indiv)
        population.append(indiv)
        popsize_act = len(population)
    
#population = sorted(population, key = lambda x: x['Cmax'])  
population.sort(key = lambda x: x['Cmax'])
minold=L
print(datetime.datetime.now())

t = 0
while t < 50:
    
    minnew = population[0]['Cmax']
    #minnew = min(population[k]['Cmax'] for k in range(len(population)))
    
    if minnew < minold:
        #idx = [i for i,item in enumerate(population) if item['Cmax'] == minnew][0]
        prep_visualize_schedule(population[0])
        print( minnew )
        minold = minnew
    
    #population = get_new_generation(population)
    population = get_new_generation_1(population)
    t += 1
    print(t)
    print(datetime.datetime.now())
ghrfuzhrurzu=0

    
