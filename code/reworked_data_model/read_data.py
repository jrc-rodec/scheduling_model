from translation import FJSSPInstancesTranslator
from translation import SequenceGAEncoder
from model import Order, ProductionEnvironment

def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders

source = '6_Fattahi'
instance = 20
production_environment = FJSSPInstancesTranslator().translate(source, instance)
encoder = SequenceGAEncoder()

orders = generate_one_order_per_recipe(production_environment)
workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)

print('Workstations')
print(workstations_per_operation)
print('Durations')
print(base_durations)
print('Job Operations')
print(job_operations)