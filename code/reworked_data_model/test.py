from translation import BenchmarkTranslator, TimeWindowGAEncoder, BasicBenchmarkTranslator, SimpleGAEncoder, FJSSPInstancesTranslator
from model import Order, ProductionEnvironment
from solver import GASolver
from evaluation import Evaluator, Makespan, IdleTime, TimeDeviation
from visualization import visualize_schedule
import random

def generate_orders(amount : int, production_enviornment : ProductionEnvironment) -> list[Order]:
    available_resources = production_enviornment.resources # NOTE: currently works because all resources can be produced
    orders : list[Order] = []
    for i in range(amount):
        resource_id = random.randint(0, len(available_resources)-1)
        resource = production_environment.get_resource(resource_id)
        order = Order(arrival_time=0, delivery_time=1000, latest_acceptable_time=1000, resources=[(resource, 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0) # NOTE: randomize later
        orders.append(order)
    return orders

"""benchmark_translator = BenchmarkTranslator()
production_environment = benchmark_translator.translate(7)
encoder = TimeWindowGAEncoder()
orders = [] # TODO: create orders for testing
values, jobs = encoder.encode(production_environment, orders)
print(values)"""


"""fjssp_translator = FJSSPInstancesTranslator()
production_environment = fjssp_translator.translate('6_Fattahi', 5)"""
#orders = [Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(1), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100)]

simple_translator = BasicBenchmarkTranslator()
production_environment = simple_translator.translate(3)
#orders = [Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(1), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(2), 1)], penalty=10, tardiness_fee=10, profit=100)]

orders = generate_orders(10, production_environment)


encoder = SimpleGAEncoder()
values, durations, jobs = encoder.encode(production_environment, orders) # NOTE: create duration dictionary

solver = GASolver(values, durations, jobs, production_environment, orders)
solver.initialize(selection='sss',max_generations=100,objective='makespan', population_size=50, offspring_amount=100) # just use default options

solver.add_objective(Makespan())


solver.run()
print(solver.get_best())
print(solver.get_best_fitness())

schedule = encoder.decode(solver.get_best(), jobs, production_environment, solver=solver)

visualize_schedule(schedule, production_environment, orders)

# just testing
evaluator = solver.evaluator
evaluator.add_objective(IdleTime())
evaluator.add_objective(TimeDeviation())
objective_values = evaluator.evaluate(schedule, jobs)
print(objective_values)

import matplotlib.pyplot as plt

average_history = solver.average_assignments
best_history = solver.assignments_best

best_generation = 0
for i in range(1, len(best_history)):
    if best_history[i] != best_history[i-1]:
        best_generation = i
print(f'Found best solution in generation: {best_generation}!')

plt.plot(average_history)
plt.plot(best_history)
plt.show()