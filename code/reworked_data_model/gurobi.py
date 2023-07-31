import gurobipy as gp

#Unfold Schedule
def unfold_schedule(x, nb_jobs, nb_machines, job_op__tuple, job_op__suitablemachines, job_op_mach__duration, nb_operations):
    
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

#calculate fitness
def get_fitness(x):
    fitness = 1/x['Cmax']
    return fitness


#Exact optimisation when machine vector is fixed
def run_gurobi(mach,timelimit, job_op__suitablemachines, nb_jobs, nb_operations, job_op__tuple, job_op_mach__duration, nb_tasks, nb_machines):
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
    for j, k in job_ops : # get workstation for each operation, get duration for every operation
        h = job_op__tuple.index((j,k))
        #machine = job_op__suitablemachines[j,k][mach[h]]
        #job_op__mach[j,k] = machine
        job_op__mach[j,k] = mach[h]
        job_op__duration[j,k] = job_op_mach__duration[j,k,mach[h]]
    
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
        #visualize_schedule(result, orders, nb_machines)

    helper = sorted(sorted(ssol.items(), key = lambda item : item[0]), key = lambda item : item[1])
    sequence = [helper[k][0][0] for k in range(len(helper))]
    schedule = list((sequence,mach))  
    
    opt_schedule, Cmax, job_op__mach, job_op__starttime = unfold_schedule(schedule, nb_jobs, nb_machines, job_op__tuple, job_op__suitablemachines, job_op_mach__duration, nb_operations)
    indiv ={'schedule': opt_schedule, 
             'Cmax': Cmax,
             'job_op__mach': job_op__mach,
             'job_op__starttime': job_op__starttime}
    indiv['fitness'] = get_fitness(indiv)
    return indiv
