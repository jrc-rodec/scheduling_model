from pulp import LpProblem, LpMinimize, LpVariable, LpInteger, lpSum, LpStatus, PULP_CBC_CMD
import random

# SETUP
random.seed(1)

workstations = 10
tasks = 100
recipes = 10
orders = 10
min_duration = 10 # min duration of a task on a workstation
max_duration = 100 # max duration of a task on a workstation
min_time = 0 # start time slot for planning
max_time = 1000 # last time slot for planning

# GENERATE ENVIRONMENT
w = [] # workstations
t = [] # tasks
r = [] # recipes
o = [] # orders

d = dict()
for i in range(workstations):
    w.append(i)
for i in range(tasks):
    t.append(i)
for i in range(recipes):
    r.append([i, []])
for i in range(orders):
    o.append([i, random.randint(0, len(r)-1), random.randint(min_time, max_time)]) # choose a random recipe for each order

p = 2 * len(w)/len(t)
for i in range(len(t)):
    d[i] = []
    while len(d[i]) == 0 or all(x == 0 for x in d[i]): # making sure every task has at least one workstation attached
        d[i] = []
        for j in range(len(w)):
            if random.uniform(0, 1) < p:
                d[i].append(random.randint(min_duration, max_duration))
            else:
                d[i].append(0)
#just reuse p for now
p = len(r)/len(t)
for i in range(len(r)): # add random tasks to each recipe
    while len(r[i][1]) == 0: # make sure every recipe has at least one task in it
        r[i][1] = []
        for j in range(len(t)):
            if random.uniform(0, 1) < p:
                r[i][1].append(t[j])

# CREATE VARIABLES
jobs = [] # just for lookups
lp_assignments = []
lp_start_times = []
j = 0
"""assignments = []
starttimes = []"""
for i in range(len(o)):
    recipe = r[o[i][1]]
    tasks = recipe[1]
    for task in tasks:
        jobs.append([task, o[i]]) # match task id to order
        """assignments.append(0)
        starttimes.append(0)"""
        lp_start_times.append(LpVariable(f's{j}', lowBound=min_time, upBound=max_time, cat=LpInteger))
        lp_assignments.append(LpVariable(f'a{j}', lowBound=min(w), upBound=max(w), cat=LpInteger))
        j += 1
"""assignments_needed = len(jobs)
assignments = list(range(assignments_needed-1))#[random.choice(w) for _ in range(assignments_needed-1)]#
for i in range(len(assignments)):
    assignments[i] = i#random.choice(w)
#start_times = list(range(assignments_needed-1))

lp_assignments = LpVariable.dicts('assignments', assignments, lowBound=min(w), upBound=max(w), cat=LpInteger) # doesn't work -> reduces assignments to amount of workstations"""
#lp_start_times = LpVariable.dicts('starttimes', start_times, lowBound=min_time, upBound=max_time, cat=LpInteger)
# CREATE PROBLEM
problem = LpProblem('SchedulingProblem', LpMinimize)
print([s for s in lp_start_times])
print([a for a in lp_assignments])
# ADD OBJECTIVE
problem += (lpSum([lp_start_times[i] + d[jobs[i][0]][random.choice(w)] - jobs[i][1][2] for i in range(len(jobs))]), 'Minimize_tardy_jobs')
#problem += (lpSum([lp_start_times[i] + d[jobs[i][0]][lp_assignments[i]] - jobs[i][1][2] for i in range(len(jobs)-1)]), 'Minimize_tardy_jobs')

# ADD CONSTRAINTS
"""for i in range(len(jobs)):
    problem += d[jobs[i][0]][assignments[i]] > 0"""
"""for i in range(len(lp_assignments)):
    problem += assignments[i] in w"""

# Solve
#problem.writeLP('SchedulingProblem.lp') # in case problem should be exported
solver = PULP_CBC_CMD(msg=1, mip_start=1)
problem.solve(solver)
#problem.solve()
print(f'Status: {LpStatus[problem.status]}')
# print result
for i in range(len(lp_assignments)):
    print(f'Scheduled job {i} on workstation {lp_assignments[i].value()} with start time {lp_start_times[i].value()}')
