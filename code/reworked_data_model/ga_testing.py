from translation import BasicBenchmarkTranslator, SimpleGAEncoder, FJSSPInstancesTranslator
from model import ProductionEnvironment, Order
from solver import GASolver
from visualization import visualize_schedule
from evaluation import Evaluator, Makespan, IdleTime, TimeDeviation, Tardiness, Profit, UnfulfilledOrders

#simple_translator = BasicBenchmarkTranslator()
#production_environment = simple_translator.translate(3)
simple_translator = FJSSPInstancesTranslator()
production_environment = simple_translator.translate(source='6_Fattahi', benchmark_id=1)

orders : list[Order] = []
for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
    orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))

encoder = SimpleGAEncoder()
values, durations, jobs = encoder.encode(production_environment, orders) # NOTE: create duration dictionary
solver = GASolver(values, durations, jobs, production_environment, orders)

start_time_slot = 0
end_time_slot = 1000
population_size = 100
offspring_amount = 2 * population_size
max_generations = 30000
keep_parents = 0#int(population_size/4)#int(population_size / 6) #NOTE: weirdly only applies if keep_elitism=0, otherwise keep_elitism is used
keep_elitism= int(population_size/4)
crossover = 'two_points' # available options: single_point, two_points, uniform, scattered
selection = 'tournament' # available options: sss (Stead State Selection), rws (Roulette Wheel Selection), sus (Stochastic Universal Selection), rank (Rank Selection), random (Random Selection), tournament (Torunament Selection)
k_tournament = int(population_size/4)
mutation = 'force_feasible' # available options: workstation_only, full_random, random_only_feasible, force_feasible

end = 0
for order in orders:
    recipe = order.resources[0][0].recipes[0]
    for task in recipe.tasks:
        workstations = production_environment.get_available_workstations_for_task(task[0])
        longest = max(w.get_duration(task[0]) for w in workstations)
        end += longest
end_time_slot = end

solver.initialize(earliest_slot=start_time_slot, last_slot=end_time_slot, population_size=population_size, offspring_amount=offspring_amount, max_generations=max_generations, crossover=crossover, selection=selection, mutation=mutation, k_tournament=k_tournament, keep_parents=keep_parents, keep_elitism=keep_elitism, repair=True)
print('starting...')
solver.add_objective(Makespan())
solver.run()

print(solver.get_best())
print(solver.get_best_fitness())

import matplotlib.pyplot as plt
best_history = solver.best_history
generation_average_history = solver.average_history

plt.plot(best_history)
plt.plot(generation_average_history)
plt.show()

schedule = encoder.decode(solver.get_best(), jobs, production_environment, solver=solver)

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