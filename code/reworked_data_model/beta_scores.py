import os
import inspect
from translation import FJSSPInstancesTranslator, SequenceGAEncoder
from model import Order, ProductionEnvironment

def read_file(source : str, id : int, path : str) -> list[str]:
    if source.startswith('0'):
        target_file = f'Behnke{id}.fjs'
    elif source.startswith('1'):
        target_file = f'BrandimarteMk{id}.fjs'
    elif source.startswith('2a'):
        target_file = f'HurinkSdata{id}.fjs'
    elif source.startswith('2b'):
        target_file = f'HurinkEdata{id}.fjs'
    elif source.startswith('2c'):
        target_file = f'HurinkRdata{id}.fjs'
    elif source.startswith('2d'):
        target_file = f'HurinkVdata{id}.fjs'
    elif source.startswith('3'):
        target_file = f'DPpaulli{id}.fjs'
    elif source.startswith('4'):
        target_file = f'ChambersBarnes{id}.fjs'
    elif source.startswith('5'):
        target_file = f'Kacem{id}.fjs'
    elif source.startswith('6'):
        target_file = f'Fattahi{id}.fjs'
    path += f'{source}\\{target_file}'
    file = open(path, 'r')
    return file.readlines()

def get_max_dissimilarity(available_workstations, operations):
    return len(operations) + sum([len(x) for x in available_workstations])

def get_approximate_max_dissimilarity(n_jobs, jobs, avg_machines):
    return sum([int(j.split(' ')[0]) for j in jobs]) + sum([int(j.split(' ')[0]) * float(avg_machines) for j in jobs])
"""def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders"""

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
read_path = currentdir + '/../external_test_data/FJSSPinstances/'

sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata', '2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']

scores = []
for benchmark_source in sources:
    full_path = read_path + benchmark_source + '/'
    for i in range(len(os.listdir(full_path))):
        file_content : list[str] = read_file(benchmark_source, i+1, read_path)
        values = file_content[0].split(' ')
        workstation_amount = int(values[1])
        average_workstations = float(values[2])

        #production_environment = FJSSPInstancesTranslator().translate(benchmark_source, i+1)
        #orders = generate_one_order_per_recipe(production_environment)
        #production_environment.orders = orders
        #workstations_per_operation, base_durations, job_operations = SequenceGAEncoder().encode(production_environment, orders)

        max_dissimilarity = get_approximate_max_dissimilarity(values[0], file_content[1:], values[2])
        beta = average_workstations/workstation_amount

        scores.append([f'{benchmark_source}{i+1}', values[0], values[1], values[2], "{:.4f}".format(max_dissimilarity), "{:.4f}".format(beta), "{:.4f}".format(max_dissimilarity * beta)])
        #scores.append((f'{benchmark_source}{i+1}', average_workstations/workstation_amount, f'{values[0]}x{values[1]}-{values[2]}'))
scores.sort(key=lambda x: float(x[6]))
print(scores)

import csv
with open(r'C:\Users\huda\Documents\GitHub\scheduling_model\code\reworked_data_model\results\beta_scores.csv', 'w', newline='') as file:
    writer = csv.writer(file, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['Name', 'Jobs', 'Machines', 'AverageMachines', 'MaxDissimilarity', 'Beta-Value', 'C'])
    writer.writerows(scores)
