from solver import Solver
from models import SimulationEnvironment
from data_translator import GAToScheduleTranslator
from objective_function import calculate_comparison_values

import multiprocessing as mp

class SolverWrapper:

    def __init__(self, solver : Solver = None):
        self.solver = solver

class MAS:

    def __init__(self):
        self.solvers = []
        self.translators = dict()

    def add_solver(self, solver : Solver, translator = GAToScheduleTranslator()):
        #NOTE: solvers should be initialized and configured at this point
        self.solvers.append(solver)
        self.translators[solver] = translator

    def run(self, env : SimulationEnvironment = None, jobs : list = None, orders : list = None, parallel : bool = False):
        # setup
        results = []
        self.env = env
        self.jobs = jobs
        self.orders = orders
        # choose run method
        if parallel:
            results = self._run_parallel()
        else:
            results = self._run_sequential()
        schedules = []
        for result in results:
            # convert to schedules or already receive results as schedule from run methods
            # NOTE: currently run methods already convert results to schedules -> [0] -> actual result, [1] -> result as schedule
            # evaluate with multiple objective functions
            makespan_fitness, tardiness_fitness, deviation_fitness, idle_time_fitness, profit_fitness = calculate_comparison_values(result[1], orders, env) # NOTE: should probably return array to make adding objectives easier
            schedules.append((result[1], [makespan_fitness, tardiness_fitness, deviation_fitness, idle_time_fitness, profit_fitness]))
        # compare
        # NOTE: for testing: choose min. makespan
        best = None
        for schedule in schedules:
            if best is None or best[1][0] > schedule[1][0]:
                best = schedule
        # choose result
        return best # resulting schedule should contain information about orders, used solver and used environment, as well as all fitness values in [1]

    def _run_sequential(self):
        results = []
        for solver in self.solvers:
            solver.run()
            result = solver.get_best()
            schedule = self.translators[solver].translate(result=result, jobs=self.jobs, env=self.env, orders=self.orders)
            schedule.created_by = solver
            schedule.created_in = self.env
            schedule.created_for = self.orders
            results.append((result, schedule))
        return results # returns a list of tuples <result, schedule>

    def _run_parallel(self):
        context = mp.get_context('spawn')
        results = []
        queue = context.Queue()
        processes = []
        for solver in self.solvers:
            p = context.Process(target=MAS.__solve_parallel, args=(solver, self.translators[solver], self.jobs, self.env, self.orders, queue))
            p.start()
            processes.append(p)
        for process in processes: # one result per process
            results.append(queue.get())
        for process in processes: # second loop in case results are not added to the queue in order
            process.join() 
        return results

    def __solve_parallel(solver : Solver, translator, jobs, env, orders, queue):
        solver.run()
        result = solver.get_best()
        schedule = translator.translators[solver].translate(result, jobs, env, orders)
        schedule.created_by = solver
        schedule.created_in = env
        schedule.created_for = orders
        queue.put((result, schedule))
