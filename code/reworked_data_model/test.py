from translation import BenchmarkTranslator, TimeWindowGAEncoder, BasicBenchmarkTranslator, SimpleGAEncoder, FJSSPInstancesTranslator
from model import Order
from solver import GASolver
from evaluation import Evaluator, Makespan, IdleTime, TimeDeviation
from visualization import visualize_schedule
"""benchmark_translator = BenchmarkTranslator()
production_environment = benchmark_translator.translate(7)
encoder = TimeWindowGAEncoder()
orders = [] # TODO: create orders for testing
values, jobs = encoder.encode(production_environment, orders)
print(values)"""


"""fjssp_translator = FJSSPInstancesTranslator()
production_environment = fjssp_translator.translate('6_Fattahi', 20)
orders = [Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(1), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100)]
"""
simple_translator = BasicBenchmarkTranslator()
production_environment = simple_translator.translate(0)
orders = [Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(0), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(1), 1)], penalty=10, tardiness_fee=10, profit=100), Order(delivery_time=100, latest_acceptable_time=100, resources = [(production_environment.get_resource(2), 1)], penalty=10, tardiness_fee=10, profit=100)]

encoder = SimpleGAEncoder()
values, durations, jobs = encoder.encode(production_environment, orders) # NOTE: create duration dictionary

solver = GASolver(values, durations, jobs, production_environment, orders)
solver.initialize(selection='sss',max_generations=100,objective='makespan') # just use default options

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
