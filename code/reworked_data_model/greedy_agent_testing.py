from translation import BasicBenchmarkTranslator, SimpleGAEncoder, FJSSPInstancesTranslator
from model import ProductionEnvironment, Order
from solver import GreedyAgentSolver
from visualization import visualize_schedule
from evaluation import Evaluator, Makespan, IdleTime, TimeDeviation, Tardiness, Profit, UnfulfilledOrders

# TODO: sequence GA, result compacting in on_mutation

#simple_translator = BasicBenchmarkTranslator()
#production_environment = simple_translator.translate(3)
simple_translator = FJSSPInstancesTranslator()
production_environment = simple_translator.translate(source='6_Fattahi', benchmark_id=15)

orders : list[Order] = []
for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
    orders.append(Order(delivery_time=1000, latest_acceptable_time=10000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))

encoder = SimpleGAEncoder()
values, durations, jobs = encoder.encode(production_environment, orders) # NOTE: create duration dictionary
solver = GreedyAgentSolver(values, durations, jobs, production_environment, orders)
solver.run()
solver.add_objective(Makespan())
solver.run()
solution = solver.get_best()

schedule = encoder.decode(solution, jobs, production_environment, solver=solver)

visualize_schedule(schedule, production_environment, orders)

evaluator = Evaluator(production_environment)
evaluator.add_objective(Makespan())
evaluator.add_objective(IdleTime())
evaluator.add_objective(TimeDeviation())
evaluator.add_objective(Tardiness())
evaluator.add_objective(Profit())
evaluator.add_objective(UnfulfilledOrders())
objective_values = evaluator.evaluate(schedule, jobs)
print(f'Solution created with: {solver.name}')
print(objective_values)
