from oo_sequence_ga import Individual, GA
from translation import FJSSPInstancesTranslator, SequenceGAEncoder
from model import Order, ProductionEnvironment

def generate_one_order_per_recipe(production_environment : ProductionEnvironment) -> list[Order]:
    orders : list[Order] = []
    for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
        orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))
    return orders

def run_ga(workstations_per_operation, base_durations, job_operations):
    ga = GA(job_operations, workstations_per_operation, base_durations)
    population_size = 300
    offspring_amount = 600
    # stopping criteria - if more than one is defined, GA stops as soon as the first criteria is met
    # if a criteria is not in use, initialize it with None
    max_generations = 10000
    run_for = 1200 # seconds, NOTE: starts counting after population initialization
    stop_at = None # target fitness

    elitism = int(population_size/10) #population_size # maximum amount of individuals of the parent generation that can be transferred into the new generation -> 0 = no elitism, population_size = full elitism
    allow_duplicate_parents = False # decides whether or not the same parent can be used as parent_a and parent_b for the crossover operation
    fill_gaps = False # optimization for the schedule construction
    adjust_optimized_individuals = True # change optimized individuals order of operations
    random_initialization = False # False = use dissimilarity function

    adjust_parameters = False # decides whether or not the mutation rate should be adjusted during the optimization process
    update_interval = 1000 # update after n generations without progress, NOTE: only relevant if adjust_parameters = True
    p_increase_rate = 1.1 # multiply current p with p_increase_rate, NOTE: only relevant if adjust_parameters = True
    max_p = 1.0 # 1.0 -> turns into random search if there's no progress for a long time, NOTE: only relevant if adjust_parameters = True

    selection = 'tournament' # 'roulette_wheel' or 'tournament'
    tournament_size = max(2, int(population_size / 10)) # NOTE: only relevant if selection = 'tournament'
    random_individual_per_generation_amount = int(population_size / 10) # amount of randomly created individuals included into each new generation, these are also affected by the random_initialization parameter
    output_interval = max_generations/20 if max_generations else 100 # frequency of terminal output (in generations)

    result, history = ga.run(population_size, offspring_amount, max_generations, run_for, stop_at, selection, tournament_size, adjust_parameters, update_interval=update_interval, p_increase_rate=p_increase_rate, max_p=max_p, elitism=elitism, fill_gaps=fill_gaps, adjust_optimized_individuals=adjust_optimized_individuals, random_individuals=random_individual_per_generation_amount, allow_duplicate_parents=allow_duplicate_parents, random_initialization=random_initialization, output_interval=output_interval)
    return result


source = '6_Fattahi'
instance = 20
production_environment = FJSSPInstancesTranslator().translate(source, instance)
orders = generate_one_order_per_recipe(production_environment)
production_environment.orders = orders

encoder = SequenceGAEncoder()
workstations_per_operation, base_durations, job_operations = encoder.encode(production_environment, orders)
result = run_ga(workstations_per_operation, base_durations, job_operations)
#schedule = encoder.decode(result.sequence, result.workstations, result.workers, result.durations, job_operations, production_environment, False)

# run gurobi on result
from gurobi import run_gurobi # wrong one
machines = result.workstations
timelimit = 600
job_op__suitablemachines = None #TODO
nb_jobs = len(orders)
nb_operations = len(job_operations)
job_op__tuple = None #TODO
job_op_mach__duration = None #TODO
nb_tasks = None # ??
nb_machines = len(base_durations[0])