# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 07:51:39 2024

@author: tst
"""
#  FJSP mit Cplex MILP solver
from docplex.mp.model import Model


#Beispiel für Progress Listener siehe: https://github.com/IBMDecisionOptimization/docplex-examples/blob/master/examples/mp/jupyter/progress.ipynb

from docplex.mp.progress import ProgressListener, ProgressClock

class SolutionPrinter(ProgressListener):
    
    def __init__(self):
        ProgressListener.__init__(self, ProgressClock.Objective)
        self.solution_count = 0 
        
    def notify_progress(self, pdata):
        #Called at each new solution (better objective).
        objective = pdata.current_objective
        time = pdata.time
        print(
            "Solution %i, time = %f s, objective = %i"
            % (self.solution_count, time, objective)
        )
        self.solution_count += 1

#read and arrange Data
filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\0_BehnkeGeiger\Behnke6.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\1_Brandimarte\BrandimarteMk4.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\2a_Hurink_sdata\HurinkSdata1.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\4_ChambersBarnes\ChambersBarnes17.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\5_Kacem\Kacem4.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\6_Fattahi\Fattahi18.fjs'
f = open(filename)

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

duration = {}
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
            task_processing_time[j][o][machine] = time
            suitable_helper += [machine+1]
            duration[j+1,o+1,machine+1] = time
            
        job_op_suitable[j+1,o+1] = suitable_helper
        tmp = tmp + 2 * nb_machines_operation

# Trivial upper bound for the start times of the tasks
L=0
for j in range(nb_jobs):
    for o in range(nb_operations[j]):
        L += max(task_processing_time[j][o][m] for m in range(nb_machines) if task_processing_time[j][o][m] != INFINITE)

#initialize the model
mdl = Model('FJSP MILP Cplex')

#list of jobs for creating Variables
jobs = [j for j in range(1,nb_jobs+1)]

#list of Job Operations for creating Variables
job_ops = [(j+1,k+1) for j in range(nb_jobs) for k in range(nb_operations[j])] 

#list of machines for creating Variables
machines = [m for m in range(1,nb_machines+1)]

#list for creating X Variables list_X_var=[(0,0,0,0)]
list_X_var = []
for j, k in job_ops :
    if j < nb_jobs :
        for jp, kp in job_ops:
            if jp > j:
                list_X_var.append((j,k,jp,kp))
                
#list for creating Y Variables list_Y_var=[(0,0,0)]
list_Y_var = []
for j, o in job_ops :
    for m in job_op_suitable[j,o] :
        list_Y_var.append((j,o,m))
        
# Variables
Y = mdl.binary_var_dict(list_Y_var, name=lambda y: 'Y_%s_%s_%s' % y)
mdl.Y = Y
X = mdl.binary_var_dict(list_X_var, name=lambda x: 'X_%s_%s_%s_%s' % x)
mdl.X = X
C = mdl.continuous_var_dict(job_ops, lb = 0, ub = L, name=lambda c: 'C_%s_%s' % c)
mdl.C = C
Cmax = mdl.continuous_var(lb = 0, ub = L, name = "Cmax")
mdl.Cmax = Cmax

#Constraints
mdl.add_constraints((mdl.sum(mdl.Y[j,o,m] for m in job_op_suitable[j,o]) == 1, 'Y_const__%s_%s' %(j,o)) for j, o in job_ops)

mdl.add_constraints((mdl.sum(mdl.Y[j,o,m] * duration[j,o,m] for m in job_op_suitable[j,o]) <= mdl.C[j,o], 'C_time_%s_%s' %(j,o))  
                    for j, o in job_ops 
                    if o == 1)

mdl.add_constraints((mdl.sum(mdl.Y[j,o,m] * duration[j,o,m] for m in job_op_suitable[j,o]) + mdl.C[j,o-1] <= mdl.C[j,o], 'C_time_%s_%s' %(j,o)) 
                    for j, o in job_ops 
                    if o != 1)

mdl.add_constraints((mdl.C[j,o] >= mdl.C[jp,op] + duration[j,o,m] - L*(3 - mdl.X[j,o,jp,op] - mdl.Y[j,o,m] - mdl.Y[jp,op,m]), 'NO1_%s_%s_%s_%s_%s' %(j,o,jp,op,m)) 
              for j, o in job_ops if j < nb_jobs
              for jp, op in job_ops if jp > j 
              for m in machines if m in job_op_suitable[j,o] if m in job_op_suitable[jp,op])

mdl.add_constraints((mdl.C[jp,op] >= mdl.C[j,o] + duration[jp,op,m] - L*(mdl.X[j,o,jp,op] + 2 - mdl.Y[j,o,m] - mdl.Y[jp,op,m]), 'NO2_%s_%s_%s_%s_%s' %(j,o,jp,op,m)) 
              for j, o in job_ops if j < nb_jobs
              for jp, op in job_ops if jp > j 
              for m in machines if m in job_op_suitable[j,o] if m in job_op_suitable[jp,op])


mdl.add_constraints((mdl.Cmax >= mdl.C[j,nb_operations[j-1]] for j in jobs),"Cmax")

mdl.minimize(mdl.Cmax)

#Print model information
#mdl.print_information()

#-----------------------------------------------------------------------------
# Solve the model and display the result
#-----------------------------------------------------------------------------

# Solve model
print('Solving model...')
mdl.parameters.timelimit = 30;
#mdl.log_output = True
mdl.add_progress_listener(SolutionPrinter())
#res = mdl.solve(execfile = r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cplex\bin\x64_win64\cplex.exe")
res = mdl.solve()

#Print Solution
print('Solution:')
#print('mdl.report:')
#mdl.report()

#print('res.display:')
#res.display()

xsol = res.get_value_dict(X)
#ysol = res.get_value_dict(Y) #Bug in res.get_value_dict: wenn Y[i,j,m] negativ ist
csol = res.get_value_dict(C)
#Output
ysol={}
for j, k, i in list_Y_var:
    ysol[j,k,i] = res.get_value(Y[j,k,i])
    if ysol[j,k,i] > 0:
        #print('\nStarting time for Job %s Operation %s on machine %s is %s' % (j,k,i,csol[j,k]-duration[j,k,i]) )
        #print('Completion time for Job %s Operation %s: %s' % (j,k,csol[j,k]))
        print('Job %i Operation %i on Maschine %i starts at %i ends at %i (duration %i)' 
              %(j,k,i,round(csol[j,k]-duration[j,k,i]),round(csol[j,k]),duration[j,k,i]))
print("solve status: %s" % res.solve_status)
print("solve status: %s" % res.solve_details.status) 
print("solve status code: %i" % res.solve_details.status_code) #101...integer optimal, 107...time limit exceed
print("Best objective value: %f" % res.objective_value)
print('Objektive lower bound: %f' % res.solve_details.best_bound)
print("Wall time : %f s" % res.solve_details.time)

mdl.end()

# Draw solution
import docplex.cp.utils_visu as visu
if res and visu.is_visu_enabled():
# Draw solution
    visu.timeline('MIP-Cplex Solution for flexible job-shop problem ' + filename)
    visu.panel('Machines')
    for m in machines:
        visu.sequence(name='M' + str(m))
        for j, k, i in list_Y_var:
            if ysol[j,k,i] > 0 and i == m:
                start_value = round(csol[j,k]-duration[j,k,i])
                end_value = round(csol[j,k])
                visu.interval(start_value, end_value, j, 'J{}_O{}'.format(j,k))
    visu.show()
