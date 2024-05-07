# -*- coding: utf-8 -*-
"""
Created on Wed Apr 17 15:42:47 2024

@author: tst
"""

from docplex.cp.model import *

import docplex.cp.utils_visu as visu

from docplex.cp.solver.solver_listener import *

#Work in progress
class SolutionPrinter(CpoSolverListener):
    
    def __init__(self):
        #super(SolutionPrinter, self).__init__()
        self.solution_count = 0 
    
    def solver_created(self, solver):
        """ Notify the listener that the solver object has been created.

        Args:
            solver: Originator CPO solver (object of class :class:`~docplex.cp.solver.solver.CpoSolver`)
        """
        print("Solver created")
        
    def new_result(self, solver, msol):
            #Called at each new solution (better objective).
            self.solution_count += 1
            if msol:
                # Update objective value
                time = msol.get_solve_time()
                objective = msol.get_objective_value()
                print(
                    "Solution %i, time = %f s, objective = %i"
                    % (self.solution_count, time, objective)
                    )
       
            
           
    '''
    def new_log_data(self, solver, data):
        #Called at each new solution (better objective).
        time = 0
        objective = 0
        for line in data.splitlines():
                if line.startswith(" ! Time = "):
                    
                    ex = line.find("s,", 10)
                    if ex > 0:
                        time = float(line[10:ex])
                    elif line.startswith(" ! Current objective is "):
                        objective =  line[24:]
                    
                        print(
                            "Solution %i, time = %i s, objective = %i"
                            % (self.solution_count, time, objective)
                            )
        self.solution_count += 1
        '''




#read and arrange Data
filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\0_BehnkeGeiger\Behnke1.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\1_Brandimarte\BrandimarteMk4.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\2a_Hurink_sdata\HurinkSdata1.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\4_ChambersBarnes\ChambersBarnes17.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\5_Kacem\Kacem4.fjs'
#filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\6_Fattahi\Fattahi20.fjs'
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

# not needed for CP solver of CPLEX
#task_processing_time = [[[INFINITE for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]

JOBS =  [[[(INFINITE,INFINITE) for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]

for j in range(nb_jobs):
    line = lines[j + 1].split()
    tmp = 0
    for o in range(nb_operations[j]):
        nb_machines_operation = int(line[tmp + o + 1])
        machine_helper =[]
        for i in range(nb_machines_operation):
            machine = int(line[tmp + o + 2 * i + 2]) - 1
            time = int(line[tmp + o + 2 * i + 3])
            machine_helper += [(machine,time)]
            #task_processing_time[j][o][machine] = time # not needed for CP solver of CPLEX
        JOBS[j][o] = machine_helper
        tmp = tmp + 2 * nb_machines_operation

# not needed for CP solver of CPLEX
'''# Trivial upper bound for the start times of the tasks
L=0
for j in range(nb_jobs):
    for o in range(nb_operations[j]):
        L += max(task_processing_time[j][o][m] for m in range(nb_machines) if task_processing_time[j][o][m] != INFINITE)
'''        
#-----------------------------------------------------------------------------
# Build the model
#-----------------------------------------------------------------------------

# Create model
mdl = CpoModel()

# Following code creates:
# - creates one interval variable 'ops' for each possible operation choice
# - creates one interval variable mops' for each operation, as an alternative of all operation choices
# - setup precedence constraints between operations of each job
# - creates a no_overlap constraint an the operations of each machine

ops  = { (j,o) : interval_var(name='J{}_O{}'.format(j,o))
         for j,J in enumerate(JOBS) for o,O in enumerate(J)}
mops = { (j,o,k,m) : interval_var(name='J{}_O{}_C{}_M{}'.format(j,o,k,m), optional=True, size=d)
         for j,J in enumerate(JOBS) for o,O in enumerate(J) for k, (m, d) in enumerate(O)}

# Precedence constraints between operations of a job
mdl.add(end_before_start(ops[j,o-1], ops[j,o]) for j,o in ops if 0<o)

# Alternative constraints
mdl.add(alternative(ops[j,o], [mops[a] for a in mops if a[0:2]==(j,o)]) for j,o in ops)

# Add no_overlap constraint between operations executed on the same machine
mdl.add(no_overlap(mops[a] for a in mops if a[3]==m) for m in range(nb_machines))

# Minimize termination date
mdl.add(minimize(max(end_of(ops[j,o]) for j,o in ops)))


#-----------------------------------------------------------------------------
# Solve the model and display the result
#-----------------------------------------------------------------------------

''' work in progress
mdl.add_solver_listener(SolutionPrinter())
'''

# Solve model
print('Solving model...')
#res = mdl.solve(FailLimit=1000000,TimeLimit=10)
res = mdl.solve(execfile=r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cpoptimizer\bin\x64_win64\cpoptimizer.exe", TimeLimit = 30, LogVerbosity = 'Quiet')
print('Solution:')
#res.print_solution()

for a in mops:
    itv = res.get_var_solution(mops[a])
    for m in range(nb_machines):
        if a[3]==m and itv.is_present():
            print('Job %i Operation %i on Mashine %i starts at %i ends at %i (duration %i)' %(a[0],a[1],a[3],itv.start,itv.end,itv.size))

print("solve status: " + res.solve_status)  
print("Best objective value: %i" % res.solution.objective_values[0])
print('Objektive lower bound: %i' % res.solution.objective_bounds[0])
print("  - wall time : %f s" % res.get_solve_time())
        
# Draw solution

if res and visu.is_visu_enabled():

# Draw solution
    visu.timeline('CP-Cplex Solution for flexible job-shop problem ' + filename)
    visu.panel('Machines')
    for m in range(nb_machines):
        visu.sequence(name='M' + str(m))
        for a in mops:
            if a[3]==m:
                itv = res.get_var_solution(mops[a])
                if itv.is_present():
                    visu.interval(itv, a[0], 'J{}_O{}'.format(a[0],a[1]))
    visu.show()