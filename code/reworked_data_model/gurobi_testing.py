from translation import BasicBenchmarkTranslator, GurobiEncoder, FJSSPInstancesTranslator
from model import ProductionEnvironment, Order
from solver import GurobiSolver
from visualization import visualize_schedule
from evaluation import Evaluator, Makespan, IdleTime, TimeDeviation, Tardiness, Profit, UnfulfilledOrders

#simple_translator = BasicBenchmarkTranslator()
#production_environment = simple_translator.translate(3)
source = '6_Fattahi'
benchmark_id = 2
simple_translator = FJSSPInstancesTranslator()
production_environment = simple_translator.translate(source=source, benchmark_id=benchmark_id)

orders : list[Order] = []
for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
    orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))

encoder = GurobiEncoder()
nb_machines, nb_jobs, nb_operations, job_ops_machs, durations, job_op_suitable, upper_bound, jobs = encoder.encode(production_environment, orders)
solver = GurobiSolver(production_environment)
solver.initialize(nb_jobs, nb_operations, nb_machines, job_ops_machs, durations, job_op_suitable, upper_bound)
solver.m.Params.TIME_LIMIT = 1800 # time limit in seconds
solver.run()

print(solver.get_best())
print(solver.get_best_fitness())

xsol, ysol, csol = solver.get_best() # TODO: change signature
schedule = encoder.decode(xsol, ysol, csol, job_ops_machs, durations, production_environment, jobs, solver)

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


from result_writer import write_result
write_result(schedule, f'{source}_{benchmark_id}', solver.name, objective_values, xsol)
