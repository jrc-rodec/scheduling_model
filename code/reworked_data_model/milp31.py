# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 08:19:17 2023

@author: tst
"""

#import numpy as np
#import matplotlib.pyplot as plt
import gurobipy as gp # Import des Gurobi-Pythonpakets
#from gurobipy import GRB
# sequence based MILP for FJSSP

#read and arrange Data
f = open(r'C:\Users\dhutt\Desktop\SCHEDULING_MODEL\code\external_test_data\FJSSPinstances\0_BehnkeGeiger\Behnke58.fjs')
lines = f.readlines()
first_line = lines[0].split()
# Number of jobs
nb_jobs = int(first_line[0])
# Number of machines
nb_machines = int(first_line[1])
# Number of operations for each job
nb_operations = [int(lines[j + 1].split()[0]) for j in range(nb_jobs)]

# Constant for incompatible machines
INFINITE = 1000000

# Number of tasks
nb_tasks = sum(nb_operations[j] for j in range(nb_jobs))
        
# Processing time for each task, for each machine

task_processing_time = [[[INFINITE for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]

job_op_dur_helper = {}
job_op_suitable = {}
for j in range(nb_jobs):
    line = lines[j + 1].split()
    tmp = 0
    for o in range(nb_operations[j]):
        nb_machines_operation = int(line[tmp + o + 1])
        suitable_helper =[]
        for i in range(nb_machines_operation):
            machine = int(line[tmp + o + 2 * i + 2]) - 1
            time = int(line[tmp + o + 2 * i + 3])
            #task_processing_time[id][machine] = time
            task_processing_time[j][o][machine] = time
            suitable_helper +=[machine+1]
            job_op_dur_helper[j+1,o+1,machine+1] = time
            
        job_op_suitable[j+1,o+1] = suitable_helper
        tmp = tmp + 2 * nb_machines_operation

job_ops_machs, duration = gp.multidict(job_op_dur_helper)

# Trivial upper bound for the start times of the tasks
L = sum(
    max(task_processing_time[j][o][m] for m in range(nb_machines) if task_processing_time[j][o][m] != INFINITE)
    for o in range(nb_operations[j]) for j in range(nb_jobs))

#initialize optimization    
m = gp.Model('milp32')

#list of jobs for creating Variables
jobs = [j for j in range(1,nb_jobs+1)]

#list of Job Operations for creating Variables
job_ops = [(j+1,k+1) for j in range(nb_jobs) for k in range(nb_operations[j])] 

#list of machines for creating Variables
machines = [m for m in range(1,nb_machines+1)]

#list for creating x Variables list_X_var=[(0,0,0,0)]
list_X_var = []
for j, k in job_ops :
    if j < nb_jobs :
        for jp, kp in job_ops:
            if jp > j:
                list_X_var.append((j,k,jp,kp))
    
# Variables
Y = m.addVars(job_ops_machs, obj = 0.0, vtype=gp.GRB.BINARY, name ="Y")
X = m.addVars(list_X_var, obj = 0.0, vtype=gp.GRB.BINARY, name ="X")
"""
for j, k in job_ops : 
    for jp, kp in job_ops:
        if jp > j:
            X = m.addVar(vtype=gp.GRB.BINARY, name="X[%s,%s,%s,%s]" % (j,k,jp,kp))
"""
C = m.addVars(job_ops,  obj = 0.0, lb = 0.0, vtype=gp.GRB.CONTINUOUS, name ="C")
Cmax = m.addVar(obj = 1.0, name="Cmax")

#Constraints
m.addConstrs((Y.sum(j,k,'*') == 1 for j, k in job_ops), "Y_const")

m.addConstrs((Y.prod(duration,j,k,'*') <= C[j,k] for j, k in job_ops if k == 1),"C_time")

m.addConstrs((Y.prod(duration,j,k,'*') + C[j,k-1] <= C[j,k] for j, k in job_ops if k != 1), "C_time")

m.addConstrs((C[j,k] >= C[jp,kp] + duration[j,k,i] - L*(3 - X[j,k,jp,kp] - Y[j,k,i] - Y[jp,kp,i]) 
                for j, k in job_ops if j < nb_jobs
                for jp, kp in job_ops if jp > j 
                for i in machines if i in job_op_suitable[j,k] if i in job_op_suitable[jp,kp]), "l1")
"""
for j, k in job_ops:
    for jp, kp in job_ops:
        if jp > j:
            for i in machines:
                if i in job_op_suitable[j,k] and i in job_op_suitable[jp,kp]:
                    m.addConstr(C[j,k] >= C[jp,kp] + duration[j,k,i] - L*(3-X[j,k,jp,kp]-Y[j,k,i]-Y[jp,kp,i]), "l1[%s,%s,%s,%s,%s]" % (j,k,jp,kp,i))
                    
"""
m.addConstrs((C[jp,kp] >= C[j,k] + duration[jp,kp,i] - L*(X[j,k,jp,kp] + 2 - Y[j,k,i] - Y[jp,kp,i]) 
                for j, k in job_ops if j < nb_jobs
                for jp, kp in job_ops if jp > j 
                for i in machines if i in job_op_suitable[j,k] if i in job_op_suitable[jp,kp]), "l2")

m.addConstrs((Cmax>=C[j,nb_operations[j-1]] for j in jobs),"Cmax")
#Optimization   
m.update()
m.display()
m.optimize()
#Output

if m.Status == gp.GRB.OPTIMAL:
    xsol = m.getAttr('X', X)
    ysol = m.getAttr('X', Y)
    csol = m.getAttr('X', C)
    """
    for j,k,jp,kp in list_X_var:
        print('\nX [%s,%s,%s,%s] = %s'% (j,k,jp,kp,xsol[j,k,jp,kp]))
    """    
    for j, k, i in job_ops_machs:
        if ysol[j,k,i] > 0:
            print('\nStarting time for Job %s Operation %s on machine %s is %s' % (j,k,i,csol[j,k]-duration[j,k,i]) )
            print('Completion time for Job %s Operation %s: %s' % (j,k,csol[j,k]))
else:
    print("status = {}\n".format(m.status)) 
