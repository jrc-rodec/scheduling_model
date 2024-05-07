from ga import GA
from history import History
from translation import SequenceGAEncoder, FJSSPInstancesTranslator
from model import Order, ProductionEnvironment
import time
import os
import inspect
import collections

from ortools.sat.python import cp_model

def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders

def run_experiment(source, instance, parameters : dict):
    production_environment = FJSSPInstancesTranslator().translate(source, instance)
    orders = generate_one_order_per_recipe(production_environment)
    production_environment.orders = orders
    workstations_per_operation, base_durations, job_operations = SequenceGAEncoder().encode(production_environment, orders)
    ga = GA(job_operations, workstations_per_operation, base_durations)
    population_size = parameters['population_size'] if 'population_size' in parameters else 100
    offspring_amount = parameters['offspring_amount'] if 'offspring_amount' in parameters else population_size
    max_generations = parameters['max_generations'] if 'max_generations' in parameters else None
    run_for = parameters['time_limit'] if 'time_limit' in parameters else None
    stop_at = parameters['target_fitness'] if 'target_fitness' in parameters else None
    random_initialization = parameters['random_initialization'] if 'random_initialization' in parameters else False
    elitism = parameters['elitism'] if 'elitism' in parameters else 0
    allow_duplicate_parents = parameters['duplicate_parents'] if 'duplicate_parents' in parameters else False
    fill_gaps = parameters['fill_gaps'] if 'fill_gaps' in parameters else False
    adjust_individuals = parameters['adjust_individuals'] if 'adjust_individuals' in parameters else False
    adjust_parameters = parameters['adjust_mutation'] if 'adjust_mutation' in parameters else False
    restart_generations = parameters['restart_generations'] if adjust_parameters else 0
    max_p = parameters['max_mutation_rate'] if adjust_parameters else 0
    restart_at_max_p = parameters['restart_at_max_mutation_rate'] if adjust_parameters else False
    sequence_mutation = parameters['sequence_mutation'] if 'sequence_mutation' in parameters else 'mix'
    selection = parameters['selection'] if 'selection' in parameters else 'tournament'
    tournament_size = parameters['tournament_size'] if selection == 'tournament' else 0
    random_individual_per_generation_amount = parameters['random_individuals'] if 'random_individuals' in parameters else 0
    output_interval = parameters['output_interval'] if 'output_interval' in parameters else 1000
    start_time = time.time()
    history = ga.run(population_size, offspring_amount, max_generations, run_for, stop_at, None, tournament_size, adjust_parameters, restart_generations=restart_generations, max_p=max_p, restart_at_max_p=restart_at_max_p, elitism=elitism, sequence_mutation=sequence_mutation, fill_gaps=fill_gaps, adjust_optimized_individuals=adjust_individuals, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, random_initialization=random_initialization, output_interval=output_interval)
    run_time = time.time() - start_time
    return history, run_time

def run(source, instance, target_fitness, time_limit):
    parameters = {
        'population_size': 5,
        'offspring_amount': 20,
        'max_generations': None,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': 1,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': True,
        'adjust_individuals': True,
        'adjust_mutation': True,
        'restart_generations': 50,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'swap',
        'selection': 'tournament',
        'tournament_size': 2,
        'random_individuals': 0,
        'output_interval': 1000
    }

    history, run_time = run_experiment(source, instance, parameters)
    return history, run_time


class SolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0

    def on_solution_callback(self):
        """Called at each new solution."""
        print(
            "Solution %i, time = %f s, objective = %i"
            % (self.__solution_count, self.wall_time, self.objective_value)
        )
        self.__solution_count += 1

def cp_wfjssp_experiment(path, instance):
    print(f'Currently Running: {instance}')
    f = open(path)
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

    # Constant for incompatible machines
    INFINITE = 1000000

    # Number of tasks
    nb_tasks = sum(nb_operations[j] for j in range(nb_jobs))
            
    # Processing time for each task, for each machine-worker combination

    task_processing_time = [[[[INFINITE for s in range(nb_workers)] 
                                        for m in range(nb_machines)] 
                                        for o in range(nb_operations[j])] 
                                        for j in range(nb_jobs)]

    jobs =  [[[INFINITE] for o in range(nb_operations[j])] for j in range(nb_jobs)]


    for j in range(nb_jobs):
        line = lines[j + 1].split()
        tmp_idx = 1
        for o in range(nb_operations[j]):
            nb_machines_operation = int(line[tmp_idx])
            tmp_idx += 1
            m_w_helper=[]
            for i in range(nb_machines_operation):
                machine = int(line[tmp_idx])-1
                nb_m_workers = int(line[tmp_idx + 1])
                tmp_idx += 2
            
                for s in range(nb_m_workers):
                    worker = int(line[tmp_idx])-1
                    time = int(line[tmp_idx + 1])
                    tmp_idx += 2
                    task_processing_time[j][o][machine][worker] = time
                    m_w_helper += [(time,machine,worker)]
                            
            jobs[j][o] = m_w_helper

    # Trivial upper bound for the completion times of the tasks
    horizon = 0
    for j in range(nb_jobs):
        for o in range(nb_operations[j]):
            horizon += max(task_processing_time[j][o][m][s] for m in range(nb_machines) for s in range(nb_workers) if task_processing_time[j][o][m][s] != INFINITE )

    all_jobs = range(nb_jobs)
    all_machines = range(nb_machines)
    all_workers = range(nb_workers)

    # Global storage of variables.
    intervals_per_machine = collections.defaultdict(list)
    intervals_per_worker = collections.defaultdict(list)

    starts = {}  # indexed by (job_id, task_id).
    presences = {}  # indexed by (job_id, task_id, alt_id).
    job_ends = [] 

    # Model the flexible jobshop problem with worker constraint.
    model = cp_model.CpModel()

    # Scan the jobs and create the relevant variables and intervals.
    for job_id in all_jobs:
        job = jobs[job_id]
        num_tasks = len(job)
        previous_end = None
        for task_id in range(num_tasks):
            task = job[task_id]
            
            #temporerary
            min_duration = task[0][0]
            max_duration = task[0][0]

            num_alternatives = len(task)
            all_alternatives = range(num_alternatives)

            for alt_id in range(1, num_alternatives):
                alt_duration = task[alt_id][0]
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)

            # Create main interval for the task.
            suffix_name = "_j%i_t%i" % (job_id, task_id)
            start = model.new_int_var(0, horizon, "start" + suffix_name)
            duration = model.new_int_var(
                min_duration, max_duration, "duration" + suffix_name
            )
            end = model.new_int_var(0, horizon, "end" + suffix_name)
            interval = model.new_interval_var(
                start, duration, end, "interval" + suffix_name
            )

            # Store the start for the solution.
            starts[(job_id, task_id)] = start

            # Add precedence with previous task in the same job.
            if previous_end is not None:
                model.add(start >= previous_end)
            previous_end = end

            # Create alternative intervals.
            if num_alternatives > 1:
                l_presences = []
                for alt_id in all_alternatives:
                    alt_suffix = "_j%i_t%i_a%i" % (job_id, task_id, alt_id)
                    l_presence = model.new_bool_var("presence" + alt_suffix)
                    l_start = model.new_int_var(0, horizon, "start" + alt_suffix)
                    l_duration = task[alt_id][0]
                    l_end = model.new_int_var(0, horizon, "end" + alt_suffix)
                    l_interval = model.new_optional_interval_var(
                        l_start, l_duration, l_end, l_presence, "interval" + alt_suffix
                    )
                    l_presences.append(l_presence)

                    # Link the primary/global variables with the local ones.
                    model.add(start == l_start).only_enforce_if(l_presence)
                    model.add(duration == l_duration).only_enforce_if(l_presence)
                    model.add(end == l_end).only_enforce_if(l_presence)

                    # Add the local interval to the right machine.
                    intervals_per_machine[task[alt_id][1]].append(l_interval)
                    
                    # Add the local interval to the right machine.
                    intervals_per_worker[task[alt_id][2]].append(l_interval)

                    # Store the presences for the solution.
                    presences[(job_id, task_id, alt_id)] = l_presence

                # Select exactly one presence variable.
                model.add_exactly_one(l_presences)
            else:
                intervals_per_machine[task[0][1]].append(interval)
                intervals_per_worker[task[0][2]].append(interval)
                presences[(job_id, task_id, 0)] = model.new_constant(1)

        job_ends.append(previous_end)

    # Create machines constraints.
    for machine_id in all_machines:
        intervals = intervals_per_machine[machine_id]
        if len(intervals) > 1:
            model.add_no_overlap(intervals)
            
    # Create worker constraints.
    for worker_id in all_workers:
        intervals = intervals_per_worker[worker_id]
        if len(intervals) > 1:
            model.add_no_overlap(intervals)

    # Makespan objective.
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, job_ends)
    model.minimize(makespan)

    # Solve model.
    solver = cp_model.CpSolver()
    #solution_printer = SolutionPrinter()
    # set time limit
    solver.parameters.max_time_in_seconds = 3600.0
    
    status = solver.solve(model)

    start_times = []
    assignments = []
    workers = []
    for job_id in all_jobs:
        for task_id in range(len(jobs[job_id])):
            start_value = solver.value(starts[(job_id, task_id)])
            start_times.append(start_value)
            machine = -1
            worker = -1
            duration = -1
            for alt_id in range(len(jobs[job_id][task_id])):
                if solver.value(presences[(job_id, task_id, alt_id)]):
                    duration = jobs[job_id][task_id][alt_id][0]
                    machine = jobs[job_id][task_id][alt_id][1]
                    worker = jobs[job_id][task_id][alt_id][2]
                    assignments.append(machine)
                    workers.append(worker)
                    # technically could break here

    return solver.status_name(status), solver.objective_value, solver.best_objective_bound, solver.wall_time, start_times, assignments, workers


def cp_experiment(path, instance):
    
    print(f'Currently Running: {instance}')
    #read and arrange Data
    f = open(path)
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
    
    task_processing_time = [[[INFINITE for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]
    
    jobs =  [[[(INFINITE,INFINITE) for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]
    
    for j in range(nb_jobs):
        line = lines[j + 1].split()
        tmp = 0
        for o in range(nb_operations[j]):
            nb_machines_operation = int(line[tmp + o + 1])
            machine_helper =[]
            for i in range(nb_machines_operation):
                machine = int(line[tmp + o + 2 * i + 2]) - 1
                time = int(line[tmp + o + 2 * i + 3])
                machine_helper += [(time,machine)]
                task_processing_time[j][o][machine] = time
            jobs[j][o] = machine_helper
            tmp = tmp + 2 * nb_machines_operation
    
    
     # Trivial upper bound for the start times of the tasks
    L=0
    for j in range(nb_jobs):
        for o in range(nb_operations[j]):
            L += max(task_processing_time[j][o][m] for m in range(nb_machines) if task_processing_time[j][o][m] != INFINITE)
           
    num_jobs = len(jobs)
    all_jobs = range(num_jobs)

    num_machines = nb_machines
    all_machines = range(num_machines)

    # Model the flexible jobshop problem.
    model = cp_model.CpModel()
    
    horizon = L

    # Global storage of variables.
    intervals_per_resources = collections.defaultdict(list)
    starts = {}  # indexed by (job_id, task_id).
    presences = {}  # indexed by (job_id, task_id, alt_id).
    job_ends = []

    # Scan the jobs and create the relevant variables and intervals.
    for job_id in all_jobs:
        job = jobs[job_id]
        num_tasks = len(job)
        previous_end = None
        for task_id in range(num_tasks):
            task = job[task_id]

            min_duration = task[0][0]
            max_duration = task[0][0]

            num_alternatives = len(task)
            all_alternatives = range(num_alternatives)

            for alt_id in range(1, num_alternatives):
                alt_duration = task[alt_id][0]
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)

            # Create main interval for the task.
            suffix_name = "_j%i_t%i" % (job_id, task_id)
            start = model.new_int_var(0, horizon, "start" + suffix_name)
            duration = model.new_int_var(
                min_duration, max_duration, "duration" + suffix_name
            )
            end = model.new_int_var(0, horizon, "end" + suffix_name)
            interval = model.new_interval_var(
                start, duration, end, "interval" + suffix_name
            )

            # Store the start for the solution.
            starts[(job_id, task_id)] = start

            # Add precedence with previous task in the same job.
            if previous_end is not None:
                model.add(start >= previous_end)
            previous_end = end

            # Create alternative intervals.
            if num_alternatives > 1:
                l_presences = []
                for alt_id in all_alternatives:
                    alt_suffix = "_j%i_t%i_a%i" % (job_id, task_id, alt_id)
                    l_presence = model.new_bool_var("presence" + alt_suffix)
                    l_start = model.new_int_var(0, horizon, "start" + alt_suffix)
                    l_duration = task[alt_id][0]
                    l_end = model.new_int_var(0, horizon, "end" + alt_suffix)
                    l_interval = model.new_optional_interval_var(
                        l_start, l_duration, l_end, l_presence, "interval" + alt_suffix
                    )
                    l_presences.append(l_presence)

                    # Link the primary/global variables with the local ones.
                    model.add(start == l_start).only_enforce_if(l_presence)
                    model.add(duration == l_duration).only_enforce_if(l_presence)
                    model.add(end == l_end).only_enforce_if(l_presence)

                    # Add the local interval to the right machine.
                    intervals_per_resources[task[alt_id][1]].append(l_interval)

                    # Store the presences for the solution.
                    presences[(job_id, task_id, alt_id)] = l_presence

                # Select exactly one presence variable.
                model.add_exactly_one(l_presences)
            else:
                intervals_per_resources[task[0][1]].append(interval)
                presences[(job_id, task_id, 0)] = model.new_constant(1)

        job_ends.append(previous_end)

    # Create machines constraints.
    for machine_id in all_machines:
        intervals = intervals_per_resources[machine_id]
        if len(intervals) > 1:
            model.add_no_overlap(intervals)

    # Makespan objective
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, job_ends)
    model.minimize(makespan)

    # Solve model.
    solver = cp_model.CpSolver()

    # set time limit
    solver.parameters.max_time_in_seconds = 3600.0
    
    status = solver.solve(model)

    start_times = []
    assignments = []
    for job_id in all_jobs:
        for task_id in range(len(jobs[job_id])):
            start_times.append(solver.value(starts[(job_id, task_id)]))
            machine = -1
            for alt_id in range(len(jobs[job_id][task_id])):
                if solver.value(presences[(job_id, task_id, alt_id)]):
                    assignments.append(jobs[job_id][task_id][alt_id][1])

    return solver.status_name(status), solver.objective_value, solver.wall_time, start_times, assignments


def run_cp_experiments(write_path, benchmark_path):
    sources = os.listdir(benchmark_path)
    for source in sources:
        instances = os.listdir(benchmark_path + '/' + source)
        for instance in instances:
            status, fitness, runtime, start_times, assignments = cp_experiment(benchmark_path + '/' + source + '/' + instance, instance)
            with open(write_path + '/results.txt', 'a') as f:
                f.write(f'{instance[:-4]};{status};{fitness};{runtime};{start_times};{assignments}\n')

def run_cp_wfjssp_experiments(write_path, benchmark_path):
    instances = os.listdir(benchmark_path)
    #for source in sources:
    #instances = os.listdir(benchmark_path + '/' + source)
    for instance in instances:
        try:
            status, fitness, lower_bound, runtime, start_times, assignments, workers = cp_wfjssp_experiment(benchmark_path + '/' + instance, instance)
            with open(write_path, 'a') as f:
                f.write(f'{instance};{status};{fitness};{lower_bound};{runtime};{start_times};{assignments};{workers}\n')
        except Exception as e:
            with open(write_path, 'a') as f:
                f.write(f'{instance};Error: {e}\n')


from docplex.cp.model import *

import docplex.cp.utils_visu as visu

from docplex.cp.solver.solver_listener import *

def cplex_cp_solve(filename, instance):
    print(f'Solving {instance}')
    #read and arrange Data
    #filename = r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\0_BehnkeGeiger\Behnke1.fjs'
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
    #print('Solving model...')
    #res = mdl.solve(FailLimit=1000000,TimeLimit=10)
    res = mdl.solve(execfile=r"C:\Program Files\IBM\ILOG\CPLEX_Studio2211\cpoptimizer\bin\x64_win64\cpoptimizer.exe", TimeLimit = 3600, LogVerbosity = 'Quiet')
    #print('Solution:')
    #res.print_solution()
    # not sure if results are sorted
    start_times = []
    assignments = []
    for a in mops:
        itv = res.get_var_solution(mops[a])
        for m in range(nb_machines):
            if a[3]==m and itv.is_present():
                start_times.append(itv.start)
                assignments.append(a[3])
                #print('Job %i Operation %i on Mashine %i starts at %i ends at %i (duration %i)' %(a[0],a[1],a[3],itv.start,itv.end,itv.size))

    #print("solve status: " + res.solve_status)  
    #print("Best objective value: %i" % res.solution.objective_values[0])
    #print('Objektive lower bound: %i' % res.solution.objective_bounds[0])
    #print("  - wall time : %f s" % res.get_solve_time())

    return res.solve_status, res.solution.objective_values[0], res.solution.objective_bounds[0], res.get_solve_time(), start_times, assignments

def run_cplex_cp_experiments(write_path, benchmark_path):
    sources = os.listdir(benchmark_path)
    for source in sources:
        instances = os.listdir(benchmark_path + '/' + source)
        for instance in instances:
            status, fitness, lower_bound, runtime, start_times, assignments = cplex_cp_solve(benchmark_path + '/' + source + '/' + instance, instance)
            with open(write_path + '/results.txt', 'a') as f:
                f.write(f'{instance[:-4]};{status};{fitness};{lower_bound};{runtime};{start_times};{assignments}\n')


from datetime import datetime
if __name__ == '__main__':
    #currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    #read_path = r'C:\Users\localadmin\Documents\GitHub\scheduling_model\code\upgrades\benchmarks\\'
    shutdown_when_finished = True
    write_path = r'C:\Users\localadmin\Desktop\experiments\cp_cplex_fjssp'
    BENCHMARK_PATH = r'C:\Users\localadmin\Documents\GitHub\scheduling_model\code\upgrades\benchmarks'
    #run_cp_wfjssp_experiments(write_path, BENCHMARK_PATH)
    run_cplex_cp_experiments(write_path, BENCHMARK_PATH)

    #shutdown_when_finished = False

    #import evaluation
    
    #time_limit = 3600
    #n_experiments = 1
    #selection = [('5_Kacem', 1, 0),('5_Kacem', 2, 0),('5_Kacem', 3, 0),('5_Kacem', 4, 0), ('1_Brandimarte', 1, 0), ('1_Brandimarte', 2, 0), ('1_Brandimarte', 3, 0), ('1_Brandimarte', 4, 0), ('1_Brandimarte', 5, 0), ('1_Brandimarte', 6, 0), ('1_Brandimarte', 7, 0), ('1_Brandimarte', 8, 0), ('1_Brandimarte', 9, 0), ('1_Brandimarte', 10, 0), ('1_Brandimarte', 11, 0), ('1_Brandimarte', 12, 0), ('1_Brandimarte', 13, 0), ('1_Brandimarte', 14, 0), ('1_Brandimarte', 15, 0)]
    #histories : list[History] = []

    #for memory conservation 
    #result_path = r'C:\Users\localadmin\Documents\GitHub\scheduling_model\code\upgrades\code\results\\'
    #for instance in selection:
    #    for j in range(n_experiments):
    #        history, real_runtime = run(instance[0], instance[1], instance[2], time_limit)
    #        history.instance = f'{instance[0]}_{instance[1]}'
            # for memory conservation
    #        history.to_file(f'{result_path}{datetime.now().day}-{datetime.now().month}-{datetime.now().year}-{j}-{history.instance}.json')
            #histories.append(history)
    #        print(f'{j} - {instance[0]}{instance[1]} - Done')

            # testing purposes
    """n_options = 5
    makespan_options, idle_time_options, queue_time_options = history.get_options(n_options) # get 5 options

    solutions = dict()
    for i in range(n_options):
        if str(makespan_options[i][0]) not in solutions:
            solutions[str(makespan_options[i][0])] = [makespan_options[i][0], [0, 0, 0]]
        if str(idle_time_options[i][0]) not in solutions:
            solutions[str(idle_time_options[i][0])] = [idle_time_options[i][0], [0, 0, 0]]
        if str(queue_time_options[i][0]) not in solutions:
            solutions[str(queue_time_options[i][0])] = [queue_time_options[i][0], [0, 0, 0]]
    # sum ranks
    for i in range(n_options):
        solutions[str(makespan_options[i][0])][1][0] = i
        solutions[str(idle_time_options[i][0])][1][1] = i
        solutions[str(queue_time_options[i][0])][1][2] = i

    sorted_solutions = sorted(solutions.keys(), key=lambda x: sum(solutions[x][1])/len(solutions[x][1]))
    useable_solutions = [solutions[x][0] for x in sorted_solutions][:n_options]
    #solution = history.overall_best[-1][1][0]
    required_operations = history.required_operations
    durations = history.durations
    rank = 0
    colors = evaluation.predefine_colors(useable_solutions[0][0])
    for solution in useable_solutions:
        sequence = solution[0]
        assignments = solution[1]
        # actually not necessary, but whatever for now
        m = evaluation.makespan(sequence, assignments, durations, required_operations)
        i = evaluation.idle_time(sequence, assignments, durations, required_operations)
        q = evaluation.queue_time(sequence, assignments, durations, required_operations)
        print(f'Makepsan: {m}, Idle-Time: {i}, Queue-Time: {q}')
        evaluation.visualize(sequence, assignments, durations, required_operations, m, i, q, instance[0], instance[1], pre_colors=colors)#, title_prefix=f'Rank {rank}')
        rank += 1
    evaluation.show_plots()"""


if shutdown_when_finished:
    os.system("shutdown /s /t 1")