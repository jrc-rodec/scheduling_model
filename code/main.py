import json
from datetime import datetime
from optimizer_components import get_duration, map_index_to_operation
from models import SimulationEnvironment, Task, Resource, Recipe, Workstation, Order, Schedule
from optimizer import Randomizer, BaseGA
from read_data import read_dataset_1, translate_1, read_dataset_3, translate_3
from visualize import reformat_result, visualize

def string_to_date(date_string : str) -> datetime:
    return datetime.fromisoformat(date_string)

# Parameters
max_generations = 20
earliest_time_slot = 200
last_time_slot = 5000
population_size = 10
offspring_amount = 20

order_amount = 10

# Read Input, Translate Input into correct Datastructure
input, orders, instance = read_dataset_1(use_instance=2, order_amount=order_amount, earliest_time=earliest_time_slot, last_time=last_time_slot)
recipes, workstations, resources, tasks, orders_model = translate_1(instance, orders)
#input, orders, instance = read_dataset_3(order_amount=order_amount, earliest_time=earliest_time_slot, last_time=last_time_slot)
#recipes, workstations, resources, tasks, orders_model = translate_3(instance, n_workstations=10, generated_orders=orders) # for dataset 3, the amount of available machines has to be declared (not included with the data)

env = SimulationEnvironment(workstations, tasks, resources, recipes)

# Setup Optimizer
optimizer = BaseGA(env)
optimizer.set_minimize()
# optional (in this case, all options given are the default option, if the configuration step is skipped)
#optimizer.configure('tardiness', 'onepointcrossover', 'roulettewheel', 'randomize')
optimizer.configure('tardiness', 'twopointcrossover', 'roulettewheel', 'randomize')
"""
    Testing for ignoring planning horizon and use each individual latest acceptable order time as limit
"""
#optimizer.configure('tardiness', 'twopointcrossover', 'roulettewheel', 'onlyfeasibletimeslot')
#last_time_slot = 0
#for order in orders:
#    if order[1] > last_time_slot:
#        last_time_slot = order[1]
# all parameters after offspring_amount are optional (in this case -> verbose=True)
result, best_fitness_history, average_fitness_history, best_generation_history, feasible_gen = optimizer.optimize(orders, max_generations, earliest_time_slot, last_time_slot, population_size, offspring_amount, verbose=True)

# Re-Format result for visualization

workstation_assignments = reformat_result(result, orders, workstations, recipes, tasks)
visualize(workstation_assignments, best_fitness_history, average_fitness_history, best_generation_history, feasible_gen)
