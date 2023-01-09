import multiprocessing as mp

def test_with_queue(lb, ub, queue):
    result = 0
    for i in range(lb, ub):
        result += i
    queue.put(result)

def test_with_pipe(lb, ub, pipe):
    result = 0
    for i in range(lb, ub):
        result += i
    pipe.send(result)

def run_tests():
    context = mp.get_context('spawn')
    queue = context.Queue()
    parent_pipe, child_pipe = context.Pipe()

    n_processes = 5
    lb = 1000
    ub = 100000
    step_size = (int)((ub - lb) / n_processes)
    processes = []
    results = []

    # test queues
    print('####QUEUE TEST####')
    for i in range(n_processes):
        p = context.Process(target=test_with_queue, args=(i * step_size, ((i+1) * step_size), queue))
        processes.append(p)
        p.start()

    sum = 0
    for i in range(n_processes):
        value = queue.get()
        sum += value
        results.append(value)
        
    for result in results:
        print(result)
    print(f'Result: {sum}')

    for process in processes:
        process.join()
    queue.close()

    # test pipes
    print('####PIPE TEST####')
    processes.clear()
    results.clear()
    
    for i in range(n_processes):
        p = context.Process(target=test_with_pipe, args=(i * step_size, ((i+1) * step_size), child_pipe))
        processes.append(p)
        p.start()
    sum = 0
    for _ in range(n_processes):
        value = parent_pipe.recv()
        sum += value
        results.append(value)
    
    for result in results:
        print(result)
    print(f'Result: {sum}')

    for process in processes:
        process.join()
    child_pipe.close()
    parent_pipe.close()

def MAS_TESTING():

    from data_translator import GAToScheduleTranslator, EncodeForGA, TestTranslator
    from hybrid_solution_data_loader import get_data
    from models import Order, SimulationEnvironment, Schedule
    from solver import GASolver, GreedyAgentSolver
    from mas import MAS

    n_workstations, recipes, operation_times = get_data(0)
    recipies, workstations, resources, tasks, _ = TestTranslator().translate(n_workstations, recipes, operation_times)

    env = SimulationEnvironment(workstations, tasks, resources, recipies)

    earliest_slot = 0
    last_slot = 100
    recipe_orders = [0, 1, 2, 3, 0, 3, 2, 1, 0, 3] # for dataset 0
    orders = []
    o_id = 0
    for order in recipe_orders:
        orders.append(Order(o_id, 0, last_slot, last_slot, [order], 100, 50, False, 0, False, 500)) # for now: use resources to select recipe
        o_id = o_id + 1
    
    # translate datamodel to encoding
    encoder = EncodeForGA()
    # TODO: alternatives can be completely removed (TEST first)
    values, durations, all_jobs, alternatives = encoder.translate(env, orders) # encoding, duration lookup table, list of all jobs used (probably not needed), possible alternatives for each job
    # GA config
    crossover = 'two_points' #NOTE: available in PyGAD: 'two_points', 'single_point', 'uniform', 'scattered'
    selection = 'rws' #NOTE: available in PyGAD: 'sss' (steady state selection', 'rws' (roulette wheel), 'sus' (stochastic universal selection), 'rank' (rank selection), 'random' (random selection), 'tournament' (tournament selection)
    mutation = 'workstation_only' #NOTE: available options: 'workstation_only', 'full_random', 'random_only_feasible' #NOTE 2: so far only workstation_only can find feasible results

    population_size = 50
    offspring_amount = 100
    max_generations = 2000
    s1 = GASolver(values, durations, all_jobs, alternatives, env, orders)
    s1.initialize(earliest_slot, last_slot, population_size, offspring_amount, max_generations, crossover=crossover, selection=selection, mutation=mutation, objective='makespan')
    s2 = GASolver(values, durations, all_jobs, alternatives, env, orders)
    s2.initialize(earliest_slot, last_slot, population_size, offspring_amount, max_generations, crossover=crossover, selection=selection, mutation=mutation, objective='idle_time')
    s3 = GreedyAgentSolver(values, durations, all_jobs, env, orders)

    mas = MAS()
    mas.add_solver(s1, GAToScheduleTranslator())
    mas.add_solver(s2, GAToScheduleTranslator())
    mas.add_solver(s3, GAToScheduleTranslator())
    schedule = mas.run(env=env, jobs=all_jobs, orders=orders, parallel=True) # NOTE: parallel runs can be problematic with jupyter notebooks

if __name__ == '__main__':
    run_tests()
    MAS_TESTING()