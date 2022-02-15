import json
from datetime import datetime
from models import SimulationEnvironment, Task, Resource, Recipe, Workstation, Order

def string_to_date(date_string : str) -> datetime:
    return datetime.fromisoformat(date_string)

f = open('example.json')
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

for task in task_data:
    task_resources = []
    for task_resource in task['resources']:
        task_resources.append((task_resource['id'], task_resource['amount']))
    result_resources = []
    for result_resource in task['result_resources']:
        result_resources.append((result_resource['resource_id'], result_resource['amount']))
    tasks.append(Task(task['id'], task['name'], task_resources, result_resources, task['preceding_tasks'], task['follow_up_tasks'], task['independent'], task['prepare_time'], task['unprepare_time']))
for resource in resource_data:
    resources.append(Resource(resource['id'], resource['name'], resource['stock'], resource['price'], resource['renewable'], resource['recipes']))
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
# TODO: generate orders for testing

# jobs, assignments = simulation_environment.create_input(orders)
