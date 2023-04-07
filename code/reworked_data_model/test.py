from translation import BenchmarkTranslator, TimeWindowGAEncoder, BasicBenchmarkTranslator, SimpleGAEncoder
from model import Order
from solver import GASolver
"""benchmark_translator = BenchmarkTranslator()
production_environment = benchmark_translator.translate(7)
encoder = TimeWindowGAEncoder()
orders = [] # TODO: create orders for testing
values, jobs = encoder.encode(production_environment, orders)
print(values)"""


simple_translator = BasicBenchmarkTranslator()
production_environment = simple_translator.translate(0)
encoder = SimpleGAEncoder()
orders = [Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(1), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(2), 1)], penalty=10, tardiness_fee=10, profit=100)]
values, durations, jobs = encoder.encode(production_environment, orders) # NOTE: create duration dictionary
print(values)

solver = GASolver(values, durations, jobs, production_environment, orders)
print('just for testing')
solver.initialize(selection='sss') # just use default options
solver.run()
print(solver.get_best())
print(solver.get_best_fitness())