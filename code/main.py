import json
from datetime import datetime
from models import SimulationEnvironment, Task, Resource, Recipe, Workstation, Order, Schedule
from optimizer import Randomizer, BaseGA
from read_data import read_dataset_1, translate_1, read_dataset_3, translate_3
from visualize import visualize

def string_to_date(date_string : str) -> datetime:
    return datetime.fromisoformat(date_string)

max_generations = 100
earliest_time_slot = 200
last_time_slot = 2000
population_size = 25
offspring_amount = 50

order_amount = 10
input, orders, instance = read_dataset_1(use_instance=13, order_amount=order_amount, earliest_time=earliest_time_slot, last_time=last_time_slot)
recipes, workstations, resources, tasks, orders_model = translate_1(instance, orders)
#input, orders, instance = read_dataset_3(order_amount=order_amount, earliest_time=earliest_time_slot, last_time=last_time_slot)
#recipes, workstations, resources, tasks, orders_model = translate_3(instance, n_workstations=10, orders) # for dataset 3, the amount of available machines has to be declared (not included with the data)
env = SimulationEnvironment(workstations, tasks, resources, recipes)
env.print()
optimizer = BaseGA(env)
optimizer.set_minimize()
# optional (in this case, all options given are the default option, if the configuration step is skipped)
optimizer.configure('Tardiness', 'OnePointCrossover', 'RouletteWheel', 'Randomize')
# all parameters after offspring_amount are optional (in this case -> verbose=True)
result, best_fitness_history, average_fitness_history, best_generation_history, feasible_gen = optimizer.optimize(orders, max_generations, earliest_time_slot, last_time_slot, population_size, offspring_amount, True)

# TODO: visualize result

"""
#Loading the test data from json file

f = open('test.json')
data = json.load(f)

tasks = []
workstations = []
resources = []
recipes = []

system_info = data['system-info']
task_data = system_info['tasks']
resource_data = system_info['resources']
recipe_data = system_info['recipes']
workstation_data = system_info['workstations']

#Building the simulation environment and orders from the data
for task in task_data:
    task_resources = []
    for task_resource in task['resources']:
        task_resources.append((task_resource['id'], task_resource['amount']))
    result_resources = []
    for result_resource in task['products']:
        result_resources.append((result_resource['resource_id'], result_resource['amount']))
    tasks.append(Task(task['id'], task['name'], task_resources, result_resources, task['preceding_tasks'], task['follow_up_tasks'], task['independent'], task['prepare_time'], task['unprepare_time']))
for resource in resource_data:
    resources.append(Resource(resource['id'], resource['name'], resource['stock'], resource['price'], resource['renewable'], resource['recipes'], resource['delivery_delay']))
for recipe in recipe_data:
    recipes.append(Recipe(recipe['id'], recipe['name'], recipe['tasks']))
for workstation in workstation_data:
    basic_resources = []
    for basic_resource in workstation['basic_resources']:
        basic_resources.append((basic_resource['id'], basic_resource['amount']))
    workstation_tasks = []
    for task in workstation['tasks']:
        workstation_tasks.append((task['task_id'], task['duration']))
    workstations.append(Workstation(workstation['id'], workstation['name'], basic_resources, workstation_tasks))
print(f'Created {len(tasks)} Tasks, {len(resources)} Resources, {len(recipes)} Recipes and {len(workstations)} Workstations')
# TODO: validate system information
simulation_environment = SimulationEnvironment(workstations, tasks, resources, recipes)

order_data = data['orders']
orders = []
for order in order_data:
    arrival_time = string_to_date(order['arrival_time'])
    delivery_time = string_to_date(order['delivery_time'])
    latest_acceptable_time = string_to_date(order['latest_acceptable_time'])
    order_resources = []
    for resource in order['resources']:
        order_resources.append([resource['id'], resource['amount'], resource['price']])
    orders.append(Order(order['id'], arrival_time, delivery_time, latest_acceptable_time, order_resources, order['penalty'], order['tardiness_fee'], order['divisible'], order['customer_id']))
print(f'Created {len(orders)} Orders')
#Creating input from the loaded data for the optimizer and running the optimization
jobs, assignments = simulation_environment.create_input(orders)
print(f'Created {len(jobs)} Jobs for {len(orders)} Orders ({len(assignments)} Assignments)')

# example with randomized result
optimizer = Randomizer()
last_possible_timeslot = 1000
result = optimizer.optimize(assignments, jobs, simulation_environment, last_possible_timeslot)
print(f'Result created with optimizer: {optimizer.name}\nResult:\n{result}')
#Creating a usable schedule from the optimization result
schedule = Schedule()
for i in range(len(result)):
    schedule.add(result[i], jobs[i].id)
print(f'\nThis results in the schedule: (job_id, start timeslot)')
for i in range(len(workstations)):
    slots = schedule.assignments_for(i)
    print(f'{workstations[i].name}: {slots}')
print(f'(Durations, associated Task and Order of each job can be looked up through the job_id)')
"""