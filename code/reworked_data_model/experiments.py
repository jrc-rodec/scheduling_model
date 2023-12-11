from oo_sequence_ga import GA

from translation import SequenceGAEncoder, FJSSPInstancesTranslator
from evaluation import Makespan
from visualization import visualize_schedule
from model import Order, ProductionEnvironment
import time
import os
import inspect

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
    pruning = parameters['pruning'] if 'pruning' in parameters else False
    fill_gaps = parameters['fill_gaps'] if 'fill_gaps' in parameters else False
    adjust_individuals = parameters['adjust_individuals'] if 'adjust_individuals' in parameters else False
    adjust_parameters = parameters['adjust_mutation'] if 'adjust_mutation' in parameters else False
    update_interval = parameters['mutation_update_interval'] if adjust_parameters else 0
    p_increase_rate = parameters['mutation_increase_rate'] if adjust_parameters else 0
    max_p = parameters['max_mutation_rate'] if adjust_parameters else 0
    restart_at_max_p = parameters['restart_at_max_mutation_rate'] if adjust_parameters else False
    avoid_local_mins = parameters['avoid_local_mins'] if adjust_parameters else False
    local_min_distance = parameters['local_min_distance'] if avoid_local_mins else 0.0
    sequence_mutation = parameters['sequence_mutation'] if 'sequence_mutation' in parameters else 'mix'
    selection = parameters['selection'] if 'selection' in parameters else 'tournament'
    tournament_size = parameters['tournament_size'] if selection == 'tournament' else 0
    random_individual_per_generation_amount = parameters['random_individuals'] if 'random_individuals' in parameters else 0
    output_interval = parameters['output_interval'] if 'output_interval' in parameters else 1000
    start_time = time.time()
    result, history = ga.run(population_size, offspring_amount, max_generations, run_for, stop_at, None, selection, tournament_size, adjust_parameters, update_interval=update_interval, p_increase_rate=p_increase_rate, max_p=max_p, restart_at_max_p=restart_at_max_p, avoid_local_mins=avoid_local_mins, local_min_distance=local_min_distance, elitism=elitism, sequence_mutation=sequence_mutation, pruning=pruning, fill_gaps=fill_gaps, adjust_optimized_individuals=adjust_individuals, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, random_initialization=random_initialization, output_interval=output_interval)
    run_time = time.time() - start_time
    return result, run_time, ga.function_evaluations, ga.restarts, ga.generations

def save_result(result, source, instance, run_time, parameters, fevals, restarts):
    file = 'C:/Users/huda/Documents/GitHub/scheduling_model/code/reworked_data_model/results/testing.txt'
    #maybe add values to dict and use dict writer
    with open(file, 'a') as f:
        f.write(f'{result.workstations};{result.sequence};{source};{instance};{run_time};{result.fitness};{fevals};{parameters};{restarts}\n')

def run(source, instance, max_generation : int = 5000, time_limit : int = None, target_fitness : float = None, output : bool = False):
    
    parameters = {
        'population_size': 300,
        'offspring_amount': 600,
        'max_generations': max_generation,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': 30,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': False,
        'adjust_individuals': True,
        'adjust_mutation': True,
        'mutation_update_interval': 100,
        'mutation_increase_rate': 1.1,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'mix',
        'selection': 'tournament',
        'tournament_size': 30,
        'random_individuals': 0,
        'output_interval': 100 if output else 0
    }

    result, run_time, fevals, restarts = run_experiment(source, instance, parameters)
    return result, run_time, parameters, fevals, restarts

def run_lower_population_size(source, instance, max_generation : int = 5000, time_limit : int = 600, target_fitness : float = None, output : bool = False):
    parameters = {
        'population_size': 100,
        'offspring_amount': 200,
        'max_generations': max_generation,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': 10,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': False,
        'adjust_individuals': True,
        'adjust_mutation': True,
        'mutation_update_interval': 50,
        'mutation_increase_rate': 1.1,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'mix',
        'selection': 'tournament',
        'tournament_size': 10,
        'random_individuals': 0,
        'output_interval': 100 if output else 0
    }

    result, run_time, fevals, restarts = run_experiment(source, instance, parameters)
    return result, run_time, parameters, fevals, restarts

def run_lower_new_adaptation(source, instance, max_generation : int = 5000, time_limit : int = 600, target_fitness : float = None, output : bool = False):
    parameters = {
        'population_size': 50,
        'offspring_amount': 200,
        'max_generations': max_generation,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': 10,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': False,
        'adjust_individuals': True,
        'adjust_mutation': True,
        'mutation_update_interval': 200,
        'mutation_increase_rate': 1.1,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'mix',
        'selection': 'tournament',
        'tournament_size': 10,
        'random_individuals': 0,
        'output_interval': 100 if output else 0
    }

    result, run_time, fevals, restarts = run_experiment(source, instance, parameters)
    return result, run_time, parameters, fevals, restarts

def test_individual_adjustment(source, instance, max_generation : int = 5000, time_limit : int = 600, target_fitness : float = None, output : bool = False):
    parameters = {
        'population_size': 5,
        'offspring_amount': 20,
        'max_generations': max_generation,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': 1,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': False,
        'adjust_individuals': True,
        'adjust_mutation': True,
        'mutation_update_interval': 100,
        'mutation_increase_rate': 1.1,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'mix',
        'selection': 'tournament',
        'tournament_size': 2,
        'random_individuals': 0,
        'output_interval': 100 if output else 0
    }

    result, run_time, fevals, restarts = run_experiment(source, instance, parameters)
    return result, run_time, parameters, fevals, restarts

def save_adjustment_experiments(fitness, run_time, fevals, generations, restarts, source, instance, adjust):
    #file = 'C:/Users/huda/Documents/GitHub/scheduling_model/code/reworked_data_model/results/comparison.txt'
    file = r'C:\Users\dhutt\Desktop\SCHEDULING_MODEL\code\reworked_data_model\results\dppaulli_test.txt'
    #maybe add values to dict and use dict writer
    with open(file, 'a') as f:
        f.write(f'{source};{instance};{run_time};{fevals};{generations};{restarts};{fitness};{adjust}\n')

def save_elitism_experiments(fitness, run_time, fevals, generations, restarts, source, instance, elitism):
    file = 'C:/Users/huda/Documents/GitHub/scheduling_model/code/reworked_data_model/results/results_elitism.txt'
    #maybe add values to dict and use dict writer
    with open(file, 'a') as f:
        f.write(f'{source};{instance};{run_time};{fevals};{generations};{restarts};{fitness};{elitism}\n')

def run_experiment_adjust_individual(source, instance, max_generation : int = 5000, time_limit : int = 600, target_fitness : float = None, output : bool = False, adjust : bool = True):
    parameters = {
        'population_size': 5,
        'offspring_amount': 20,
        'max_generations': max_generation,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': None,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': False,
        'adjust_individuals': adjust,
        'adjust_mutation': True,
        'mutation_update_interval': 100,
        'mutation_increase_rate': 1.1,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'mix',
        'selection': 'tournament', # 'tournament'
        'tournament_size': 2,
        'random_individuals': 0,
        'output_interval': 100 if output else 0
    }

    result, run_time, fevals, restarts, generations = run_experiment(source, instance, parameters)
    save_adjustment_experiments(result.fitness, run_time, fevals, generations, restarts, source, instance, parameters['adjust_individuals'])
    #return result, run_time, parameters, fevals, restarts

def kacem_and_brandimarte(source, instance, adjust):
    encoder = SequenceGAEncoder()
    production_environment = FJSSPInstancesTranslator().translate(source, instance)
    orders = generate_one_order_per_recipe(production_environment)
    production_environment.orders = orders
    workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)
    ga = GA(job_operations, workstations_per_operation, base_durations)

    population_size = 5
    offspring_amount = 20
    # stopping criteria - if more than one is defined, GA stops as soon as the first criteria is met
    # if a criteria is not in use, initialize it with None
    max_generations = None
    run_for = 1800 # seconds, NOTE: starts counting after population initialization
    stop_at = 927 # target fitness

    elitism = int(population_size/10) #population_size # maximum amount of individuals of the parent generation that can be transferred into the new generation -> None = no elitism, population_size = full elitism
    allow_duplicate_parents = False # decides whether or not the same parent can be used as parent_a and parent_b for the crossover operation
    pruning = False # checks if an individual even can be better than the known best before evaluating, returns 2 * min makespan as fitness NOTE: ignored if multiprocessed
    fill_gaps = False # optimization for the schedule construction NOTE: ignored if multiprocessed NOTE2: shouldn't matter, same as adjust?
    adjust_optimized_individuals = adjust # change optimized individuals order of operations
    random_initialization = False # False = use dissimilarity function

    adjust_parameters = True # decides whether or not the mutation rate should be adjusted during the optimization process
    update_interval = 100#50#int(max_generations/20) # update after n generations without progress, NOTE: only relevant if adjust_parameters = True
    p_increase_rate = 4.0#2.0#1.1 # multiply current p with p_increase_rate, NOTE: only relevant if adjust_parameters = True
    max_p = 1.0#1.0 # 1.0 -> turns into random search if there's no progress for a long time without restarting, NOTE: only relevant if adjust_parameters = True
    restart_at_max_p = True # create a completely new population if max_p is reached to prevent random search
    avoid_known_local_mins = True
    local_min_distance = 0.1
    sequence_mutation = 'mix' # swap, insert, or mix

    selection = 'tournament' # 'roulette_wheel' or 'tournament'
    tournament_size = max(2, int(population_size / 10)) # NOTE: only relevant if selection = 'tournament'
    random_individual_per_generation_amount = 0#int(population_size / 10) # amount of randomly created individuals included into each new generation, these are also affected by the random_initialization parameter
    output_interval = max_generations/20 if max_generations else 100 # frequency of terminal output (in generations)
    parallel_evaluation = False
    start_time = time.time()
    result, history = ga.run(population_size, offspring_amount, max_generations, run_for, stop_at, selection, tournament_size, adjust_parameters, update_interval=update_interval, p_increase_rate=p_increase_rate, max_p=max_p, restart_at_max_p=restart_at_max_p, avoid_local_mins=avoid_known_local_mins, local_min_distance=local_min_distance, elitism=elitism, sequence_mutation=sequence_mutation, pruning=pruning, fill_gaps=fill_gaps, adjust_optimized_individuals=adjust_optimized_individuals, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, random_initialization=random_initialization, output_interval=0, parallel_evaluation=parallel_evaluation)
    run_time = time.time() - start_time
    save_adjustment_experiments(result.fitness, run_time, ga.function_evaluations, ga.generations, ga.restarts, source, instance, adjust)

def run_experiment_elitism(source, instance, max_generation : int = 5000, time_limit : int = 600, target_fitness : float = None, output : bool = False, elitism : bool = True):
    parameters = {
        'population_size': 5,
        'offspring_amount': 20,
        'max_generations': max_generation,
        'time_limit': time_limit,
        'target_fitness': target_fitness,
        'elitism': 1 if elitism else None,
        'random_initialization': False,
        'duplicate_parents': False,
        'pruning': False,
        'fill_gaps': False,
        'adjust_individuals': True,
        'adjust_mutation': True,
        'mutation_update_interval': 100,
        'mutation_increase_rate': 1.1,
        'max_mutation_rate': 1.0,
        'restart_at_max_mutation_rate': True,
        'avoid_local_mins': True,
        'local_min_distance': 0.1,
        'sequence_mutation': 'mix',
        'selection': 'tournament', # 'tournament'
        'tournament_size': 2,
        'random_individuals': 0,
        'output_interval': 100 if output else 0
    }

    result, run_time, fevals, restarts, generations = run_experiment(source, instance, parameters)
    save_elitism_experiments(result.fitness, run_time, fevals, generations, restarts, source, instance, elitism)

if __name__ == '__main__':
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    read_path = currentdir + '/../external_test_data/FJSSPinstances/'

    #sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata', '2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']
    #sources = ['5_Kacem']
    #known_best = [66, 107, 221, 355, 119, 320, 397, 253, 210, 516, 468, 446, 466, 554, 514, 608, 879, 894, 1070, 1196]
    #known_best = [66, 107, 221, 355, 119, 320, 397, 253, 210, 516, 468, 446, 466, 0, 514, 0, 0, 0, 0, 0]
    #known_best = [11, 11, 7, 11]
    n_experiments = 5
    scores = []
    #source = '1_Brandimarte'
    #instance = 1
    #known_best = 40
    selection =  [('3_DPpaulli', 1, 0), ('3_DPpaulli', 5, 0), ('3_DPpaulli', 10, 0)]#[('0_BehnkeGeiger', 60, 0)]#[('4_ChambersBarnes', 6, 927)]#('5_Kacem', 1, 11), ('4_ChambersBarnes', 6, 927), ('6_Fattahi', 15, 514), ('1_Brandimarte', 1, 40)]#('5_Kacem', 4, 11)]#, ('6_Fattahi', 10, 516), ('6_Fattahi', 15, 514), ('1_Brandimarte', 1, 40), ('1_Brandimarte', 11, 649), ('4_ChambersBarnes', 6, 927)]
    time_limit = 1200
    #selection = selection[6:]
    #for benchmark_source in sources:
    #full_path = read_path + source + '/'
    for instance in selection:
        #if instance[0] != '5_Kacem':
        for j in range(n_experiments):
            #result, run_time, parameters = run(source, instance, max_generation=5000, time_limit=600, target_fitness=known_best[i], output=False)
            #result, run_time, parameters, fevals, restarts = run_lower_new_adaptation(source, instance, max_generation=None, time_limit=600, target_fitness=known_best, output=False)
            run_experiment_adjust_individual(instance[0], instance[1], None, time_limit, instance[2], False, True)
            #kacem_and_brandimarte(instance[0], instance[1], True)
            #run_experiment_elitism(instance[0], instance[1], None, time_limit, instance[2], False, True)
            print(f'{j} - {instance[0]}{instance[1]} - With Elitism')
        #for j in range(n_experiments):
            #result, run_time, parameters = run(source, instance, max_generation=5000, time_limit=600, target_fitness=known_best[i], output=False)
            #result, run_time, parameters, fevals, restarts = run_lower_new_adaptation(source, instance, max_generation=None, time_limit=600, target_fitness=known_best, output=False)
            #run_experiment_adjust_individual(instance[0], instance[1], None, time_limit, instance[2], False, False)
            #kacem_and_brandimarte(instance[0], instance[1], False)
            #run_experiment_elitism(instance[0], instance[1], None, time_limit, instance[2], False, False)
            #print(f'{j} - {instance[0]}{instance[1]} - Without Elitism')
            #print(f'Finished Experiment {j+1} with Benchmark {source}{instance}, expected: {known_best}, received: {result.fitness}.')
            # save result and parameters
            #save_result(result, source, instance, run_time, parameters, fevals, restarts)
"""        for i in range(3, len(os.listdir(full_path))):
            source = benchmark_source
            instance = i+1
"""
#source = '6_Fattahi'
#instance = 10

#print(result)
#print(parameters)

"""
-with elitism (different rates)
-without elitism

-with inclusion of random individuals (random initialization)
-with inclusion of random individuals (dissimilarity initialization)
-without inclusion of random individuals 

-with individual adjustment
-without individual adjustment
-without individual adjustment, with gap filling algorithm

-random initialization
-dissimilarity initialization

-with parameter (mutation strength) adjustment (different rates)
-without parameter adjustment
-with restarting
-without restarting

-with preempt # might be better for nested solvers
-without preempt

-sequence mutation swap
-sequence mutation insert
-sequence mutation mix

-population sizes
-offspring amounts

-machine vector recombination methods (two_point, one_point, uniform)

-selection doesn't seem to matter too much (maybe different tournament sizes?)
"""
