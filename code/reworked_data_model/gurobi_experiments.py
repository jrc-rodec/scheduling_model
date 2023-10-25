from solver import GurobiSolver
from translation import GurobiEncoder, FJSSPInstancesTranslator
from model import Order
import time
import os
import inspect

#upper bound, lower bound, best solution (fitness),gap, status, # explored solution, laufzeit, gesamtlaufzeit, X+Y+C vektoren
def write_result(source : str, instance : int, best_result, upper_bound : float, lower_bound : float, x, y, c, gap, status, n_explored_solutions, runtime, overall_runtime):
    path = r'C:\Users\localadmin\Documents\GitHub\scheduling_model\code\reworked_data_model\results\gurobi_results.txt'
    with open(path, 'a') as f:
        f.write(f'{source};{instance};{best_result};{upper_bound};{lower_bound};{gap};{status};{n_explored_solutions};{runtime};{overall_runtime};{x};{y};{c}\n')


currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
read_path = currentdir + '/../external_test_data/FJSSPinstances/'
use_sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata','2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']
for benchmark_source in use_sources:
    full_path = read_path + benchmark_source + '/'
    for i in range(len(os.listdir(full_path))):
        source = benchmark_source
        benchmark_id = i+1

        simple_translator = FJSSPInstancesTranslator()
        production_environment = simple_translator.translate(source=source, benchmark_id=benchmark_id)

        orders : list[Order] = []
        for i in range(len(production_environment.resources.values())): # should be the same amount as recipes for now
            orders.append(Order(delivery_time=1000, latest_acceptable_time=1000, resources=[(production_environment.get_resource(i), 1)], penalty=100.0, tardiness_fee=50.0, divisible=False, profit=500.0))

        encoder = GurobiEncoder()
        nb_machines, nb_jobs, nb_operations, job_ops_machs, durations, job_op_suitable, upper_bound, jobs = encoder.encode(production_environment, orders)
        start_time = time.time()
        solver = GurobiSolver(production_environment)
        solver.initialize(nb_jobs, nb_operations, nb_machines, job_ops_machs, durations, job_op_suitable, upper_bound)
        solver.m.Params.TIME_LIMIT = 1800 # time limit in seconds -> 30 Minutes - 1800
        solver.run()
        real_time = time.time() - start_time
        xsol, ysol, csol = solver.get_best() 
        write_result(source, benchmark_id, solver.m.objVal, solver.Cmax.UB, solver.Cmax.LB, xsol, ysol, csol, solver.m.MIPGap, solver.m.Status, solver.m.NodeCount, solver.m.Runtime, real_time)
