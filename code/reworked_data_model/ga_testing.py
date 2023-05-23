from translation import BasicBenchmarkTranslator, SimpleGAEncoder, FJSSPInstancesTranslator
from model import ProductionEnvironment, Order
from solver import GASolver
from visualization import visualize_schedule
from evaluation import Evaluator, Makespan, IdleTime, TimeDeviation, Tardiness, Profit, UnfulfilledOrders

# TODO: sequence GA, result compacting in on_mutation

#simple_translator = BasicBenchmarkTranslator()
#production_environment = simple_translator.translate(3)
source='6_Fattahi'
benchmark_id=10
simple_translator = FJSSPInstancesTranslator()
production_environment = simple_translator.translate(source=source, benchmark_id=benchmark_id)

orders : list[Order] = []
for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
    orders.append(Order(delivery_time=1000, latest_acceptable_time=100000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))

encoder = SimpleGAEncoder()
values, durations, jobs = encoder.encode(production_environment, orders) # NOTE: create duration dictionary
solver = GASolver(values, durations, jobs, production_environment, orders)

start_time_slot = 0
#end_time_slot = 1000
population_size = 25
offspring_amount = 2 * population_size #NOTE: currently unused parameter
max_generations = 1000 #NOTE: for comparison to gurobi, max_time would be more useful, currently not supported by GA library
keep_parents = 0#int(population_size/4)#int(population_size / 6) #NOTE: weirdly only applies if keep_elitism=0, otherwise keep_elitism is used
keep_elitism= int(population_size/4)
crossover = 'two_points' # available options: single_point, two_points, uniform, scattered
#NOTE: some selection methods might require additional parameters
selection = 'tournament' # available options: sss (Stead State Selection), rws (Roulette Wheel Selection), sus (Stochastic Universal Selection), rank (Rank Selection), random (Random Selection), tournament (Torunament Selection)
k_tournament = int(population_size/4)
mutation = 'force_feasible' # available options: workstation_only, full_random, random_only_feasible, force_feasible
repair = True # repairs overlaps in starting times (job sequence and workstation seqeuence)
repair_on_crossover = False # only needed if repair = True -> if True, individuals are repaired after the crossover, if False, individuals are repaired after mutation
random_until_feasible = True # randomize population until at least 1 feasible individual is discovered

postprocessing = False
shift_to_zero = True

end = 0
for order in orders:
    recipe = order.resources[0][0].recipes[0]
    for task in recipe.tasks:
        workstations = production_environment.get_available_workstations_for_task(task[0])
        longest = max(w.get_duration(task[0]) for w in workstations)
        end += longest
end_time_slot = end

solver.initialize(earliest_slot=start_time_slot, last_slot=end_time_slot, population_size=population_size, offspring_amount=offspring_amount, max_generations=max_generations, crossover=crossover, selection=selection, mutation=mutation, k_tournament=k_tournament, keep_parents=keep_parents, keep_elitism=keep_elitism, repair=repair, random_until_feasible=random_until_feasible)
print('starting...')
solver.add_objective(Makespan())
solver.run()

solution = solver.get_best()
print(solution)
print(solver.get_best_fitness())

import matplotlib.pyplot as plt
best_history = solver.best_history
generation_average_history = solver.average_history

plt.plot(best_history)
plt.plot(generation_average_history)
plt.show()

if shift_to_zero:
    current_start = min(solution[1::2])
    for i in range(1, len(solution), 2):
        solution[i] -= current_start

#NOTE: postprocessing algorithm (result compression) could be used here
if postprocessing:
    # TODO: currently produces infeasible solutions due to overlaps
    print('NOTE: post processing steps are applied to the solution found by the solver')
    solution = solver.get_best()
    w_sorting : list[list[int]] = []
    for workstation in production_environment.workstations.keys():
        w_sorting.append([])
        for i in range(0, len(solution), 2):
            if solution[i] == int(workstation):
                w_sorting[-1].append(i)
        w_sorting[-1].sort(key= lambda x: solution[x+1])
    # left shift all on workstation
    for w in w_sorting:
        for i in range(len(w)):
            lb_workstation = 0
            if i > 0:
                lb_workstation = solution[w[i-1]] + production_environment.get_workstation(solution[w[i-1]]).get_duration(jobs[int(w[i-1]/2)].task)
            lb_sequence = 0
            solution[w[i]+1] = max(lb_sequence, lb_workstation)
    for i in range(0, len(solution), 2):
        lb_sequence = 0
        lb_workstation = 0
        if int(i/2)-1 >= 0 and jobs[int(i/2)-1].order == jobs[int(i/2)].order:
            # not first in sequence
            lb_sequence = solution[i-1] + production_environment.get_workstation(solution[i-2]).get_duration(jobs[int(i/2)-1].task)
        prev = solution[i+1]
        solution[i+1] = max(lb_sequence, lb_workstation)
        shift = solution[i+1] - prev
        # shift all jobs following on the same workstation
        for w in w_sorting:
            if i in w:
                index = w.index(i)
                for j in range(index, len(w)):
                    solution[w[j]+1] += shift

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

from result_writer import write_result
write_result(schedule, f'{source}_{benchmark_id}', solver.name, objective_values, solution)