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

selection = [('5_Kacem', 1, 11, 72.0, 72.0), ('5_Kacem', 4, 12, 616.0, 616.0), ('6_Fattahi', 10, 516, 32.4, 11.01), ('6_Fattahi', 15, 514, 75.6, 28.08), ('1_Brandimarte', 1, 40, 165.0, 55.0), ('1_Brandimarte', 11, 649, 449-0, 135.45)]
file = 'C:/Users/dhutt/Desktop/SCHEDULING_MODEL/code/reworked_data_model/results/readable_benchmarks.txt'
for source in selection:
    production_environment = FJSSPInstancesTranslator().translate(source[0], source[1])
    orders = generate_one_order_per_recipe(production_environment)
    production_environment.orders = orders
    workstations_per_operation, base_durations, job_operations = SequenceGAEncoder().encode(production_environment, orders)
    
    number_of_machines = len(base_durations[0])
    number_of_jobs = len(orders)
    expected_makespan = source[2]
    number_of_operations = len(job_operations)
    average_operations_per_job = number_of_operations/number_of_jobs
    average_machines_per_operations = sum([len(x) for x in workstations_per_operation]) / number_of_operations
    beta = average_machines_per_operations / number_of_machines

    unique_durations = []
    overall_amount_durations = []
    for duration in base_durations:
        for d in duration:
            if d not in unique_durations and d > 0:
                unique_durations.append(d)
        overall_amount_durations.extend([x for x in duration if x > 0])
    overall_amount_durations = len(overall_amount_durations)
    #print(f'{source[0]}-{source[1]}: Overall: {overall_amount_durations}, Unique: {len(unique_durations)}, Unique/Overall: {overall_amount_durations/len(unique_durations)}')
    with open(file, 'a') as f:
        f.write(f'Benchmark: {source[0]} {source[1]}\nExpected Makespan: {expected_makespan}\nFlexibility (Beta-Value): {beta}\nMax Dissimilarity: {source[3]}\nC-Value: {source[3] * beta}\n# Jobs: {number_of_jobs}\n# Machines: {number_of_machines}\n# Average Available Machine per Operation: {average_machines_per_operations}\n# Operations: {number_of_operations}\n# Average Operations per Job: {average_operations_per_job}\nAvailable Workstations for each Operation:\n{workstations_per_operation}\nDurations:\n{base_durations}\n# of possible Machine Assignments: {overall_amount_durations}\nUnique Duration Values: {len(unique_durations)}\nUnique Durations/# Machine Assignments: {len(unique_durations)/overall_amount_durations}\n\n')