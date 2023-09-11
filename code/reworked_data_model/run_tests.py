from oo_sequence_ga import GA

from translation import SequenceGAEncoder, FJSSPInstancesTranslator
from evaluation import Makespan
from visualization import visualize_schedule
from model import Order, ProductionEnvironment

from multiprocessing import freeze_support

def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders

encoder = SequenceGAEncoder()
source = '5_Kacem'
instance = 4
production_environment = FJSSPInstancesTranslator().translate(source, instance)
orders = generate_one_order_per_recipe(production_environment)
production_environment.orders = orders
workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)
ga = GA(job_operations, workstations_per_operation, base_durations)
#('5_Kacem', 4, 12)
population_size = 5
offspring_amount = 20
# stopping criteria - if more than one is defined, GA stops as soon as the first criteria is met
# if a criteria is not in use, initialize it with None
max_generations = None
run_for = 1200 # seconds, NOTE: starts counting after population initialization
stop_at = 12 # target fitness

elitism = None#int(population_size/10) #population_size # maximum amount of individuals of the parent generation that can be transferred into the new generation -> None = no elitism, population_size = full elitism
allow_duplicate_parents = False # decides whether or not the same parent can be used as parent_a and parent_b for the crossover operation
pruning = False # checks if an individual even can be better than the known best before evaluating, returns 2 * min makespan as fitness NOTE: ignored if multiprocessed
fill_gaps = False # optimization for the schedule construction NOTE: ignored if multiprocessed
adjust_optimized_individuals = True # change optimized individuals order of operations
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
result, history = ga.run(population_size, offspring_amount, max_generations, run_for, stop_at, selection, tournament_size, adjust_parameters, update_interval=update_interval, p_increase_rate=p_increase_rate, max_p=max_p, restart_at_max_p=restart_at_max_p, avoid_local_mins=avoid_known_local_mins, local_min_distance=local_min_distance, elitism=elitism, sequence_mutation=sequence_mutation, pruning=pruning, fill_gaps=fill_gaps, adjust_optimized_individuals=adjust_optimized_individuals, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, random_initialization=random_initialization, output_interval=output_interval, parallel_evaluation=parallel_evaluation)

print(result)
print(f'{ga.memory_access} duplicates')
print(f'{ga.function_evaluations} function evaluations (only counts unique and feasible solutions)')
print(f'{ga.infeasible_solutions} infeasible solutions encountered.')

"""
schedule = encoder.decode(result.sequence, result.workstations, result.workers, result.durations, job_operations, production_environment, fill_gaps)

visualize_schedule(schedule, production_environment, orders)

import matplotlib.pyplot as plt
best_history = history[0]
generation_history = history[1]
average_history = history[2]
labels = ['Overall Best', 'Generation Best', 'Average']

if adjust_parameters:
    fig, axs = plt.subplots(2)
else:
    fig, ax = plt.subplots(1)
    axs = [ax]

axs[0].set_title('Fitness History')
axs[0].plot(best_history)
axs[0].plot(generation_history, c='g', linewidth=0.7)
axs[0].plot(average_history, c='r', linewidth=0.4)
axs[0].legend(labels)

if adjust_parameters:
    p_history = history[3]
    axs[1].set_title('Mutation Probability History')
    axs[1].plot(p_history, c='m', linewidth=1.0)
    axs[1].legend(['Mutation Probability'])
plt.show(block=False)

from visualization import visualizer_for_schedule
visualizer_for_schedule(schedule, job_operations)"""

if __name__ == '__main__':
    freeze_support() # NOTE: has to be the first thing to be executed