import random
from model import Job, Schedule, ProductionEnvironment, Workstation
from translation import SimpleGAEncoder
from evaluation import Evaluator, Makespan
import pygad

class GAPSONestedSolver:

    class PSO:

        class Particle:

            def __init__(self):
                self.best_positions : list[int] = []
                self.best_fitness : float = float('inf')
                self.velocities : list[float] = []
                self.current_positions : list[int] = []
                self.current_fitness : float = float('inf')

            def update(self) -> None:
                if self.current_fitness < self.best_fitness:
                    self.best_positions = self.current_positions.copy() # shallow copy should be enough for int list
                    self.best_fitness = self.current_fitness
        
        def __init__(self, swarm_size : int = 100, dimensions : int = 10, lower_bounds : list[int] = [], upper_bounds : list[int] = [], production_environment : ProductionEnvironment = None, jobs : list[Job] = [], workstations : list[int] = [], start_time : int = 0, end_time : int = 10000):
            self.swarm_size = swarm_size
            self.dimensions = dimensions
            self.lower_bounds = lower_bounds
            self.upper_bounds = upper_bounds
            self.production_environment = production_environment
            self.workstations = workstations
            self.jobs = jobs
            self.start_time = start_time
            self.end_time = end_time
            self.encoder = SimpleGAEncoder()
            self.evaluator = Evaluator(production_environment)
            self.evaluator.add_objective(Makespan()) #TODO: just fixed for now

        def _create_particle(self) -> Particle:
            positions : list[int] = []
            velocities : list[float] = []
            for i in range(self.dimensions):
                positions.append(random.randint(self.lower_bounds[i], self.upper_bounds[i]))
                velocities.append(random.random(self.min_velocities[i], self.max_velocities[i]))
            particle = self.Particle()
            particle.current_positions = positions
            particle.velocities = velocities
            return particle

        def get_best(self, particles : list[Particle]) -> Particle:
            best = particles[0]
            for particle in particles:
                if particle.best_fitness < best.best_fitness:
                    best = particle
            return best

        def _is_feasible(self, particle : Particle) -> bool:
            solution = []
            for i in range(len(particle.current_positions)):
                solution.append(self.workstations[i])
                solution.append(particle.current_positions[i])
            order = None
            for i in range(0, len(solution), 2): # go through all workstation assignments
                job = self.jobs[int(i/2)]
                workstation : Workstation = self.production_environment.get_workstation(solution[i])
                own_duration = workstation.get_duration(job.task)
                # check for last time slot
                if solution[i+1] + own_duration > self.end_time: #TODO: durations, end time
                    return False
                # check for earliest time slot
                if solution[i+1] < self.start_time: #TDOO: start time
                    return False
                # check for overlaps
                for j in range(0, len(solution), 2):
                    if not i == j:
                        if solution[i] == solution[j]: # tasks run on the same workstation
                            other_job = self.jobs[int(j/2)]
                            own_start = solution[i+1]
                            other_start = solution[j+1]
                            other_workstation = self.production_environment.get_workstation(solution[j])
                            other_duration = other_workstation.get_duration(other_job.task)
                            own_end = own_start + own_duration
                            other_end = other_start + other_duration
                            if own_start >= other_start and own_start < other_end:
                                return False
                            if own_end > other_start and own_end <= other_end:
                                return False
                            if other_start >= own_start and other_start < own_end:
                                return False
                            if other_end > own_start and other_end <= own_end:
                                return False
                # check for correct sequence
                prev_order = order
                order = self.jobs[int(i/2)].order
                if order:
                    if not prev_order is None and order == prev_order: # if current task is not the first job of this order, check if the previous job ends before the current one starts
                        prev_start = solution[i-1]
                        prev_workstation = self.production_environment.get_workstation(i-2)
                        prev_end = prev_start + prev_workstation.get_duration(self.jobs[int((i-2)/2)].task)
                        if solution[i+1] < prev_end:
                            return False
                else:
                    print("Something went completely wrong!") # TODO: should probably throw exception
            return True

        def _evaluate(self, particle : Particle) -> None:
            if not self._is_feasible(particle):
                particle.current_fitness = float('inf')
            else:
                values = []
                for i in range(len(particle.current_positions)):
                    values.append(self.workstations[i])
                    values.append(particle.current_positions[i])
                schedule : Schedule = self.encoder.decode(values, self.jobs, self.production_environment)
                fitness = self.evaluator.evaluate(schedule, self.jobs)[0] # single objective for now
                particle.current_fitness = fitness
            particle.update()

        def run(self, max_generations : int = 100, personal_weight : float = 0.8, global_weight : float = 1.2, inertia : float = 0.8, min_velocities : list[float] = [], max_velocities : list[float] = []) -> tuple[list[int], list[float]]:
            self.max_generations = max_generations
            self.personal_weight = personal_weight
            self.global_weight = global_weight
            self.inertia = inertia
            self.min_velocities = min_velocities
            self.max_velocities = max_velocities

            swarm : list[self.Particle] = []
            for i in range(self.swarm_size):
                swarm.append(self._create_particle())
            
            for generation in self.max_generations:
                current_best = self.get_best(swarm)
                for particle in swarm:
                    for i in range(self.dimensions):
                        r_personal = random.uniform(0,1)
                        r_global = random.uniform(0,1)
                        velocity = inertia * particle.velocities[i] + personal_weight * r_personal * (particle.best_positions[i] - particle.current_positions[i]) + global_weight * r_global * (current_best.best_positions[i] - particle.current_positions[i])
                        if velocity > max_velocities[i]:
                            velocity = max_velocities[i]
                        if velocity < min_velocities[i]:
                            velocity = min_velocities[i]
                        particle.current_positions[i] += velocity
                        particle.velocities[i] = velocity
                        particle.current_positions[i] = int(particle.current_positions[i]) # clamp
                        if particle.current_positions[i] > self.upper_bounds[i]:
                            particle.current_positions[i] = self.upper_bounds[i]
                        if particle.current_positions[i] < self.lower_bounds[i]:
                            particle.current_positions[i] = self.lower_bounds[i]
                    self._evaluate(particle)
            return current_best.best_positions, [current_best.best_fitness] # NOTE: should be a list itself in the future

    def _run_inner(self, solution : list[int] = [], swarm_size : int = 100, max_generations : int = 100, personal_weight : float = 0.8, global_weight : float = 1.2, inertia : float = 0.8, min_velocities : list[float] = [], max_velocities : list[float] = []) -> tuple[list[int], float]:
        # TODO: parameters
        pso = self.PSO(swarm_size=swarm_size, dimensions=len(self.jobs), lower_bounds=[self.start_time] * len(self.jobs), upper_bounds=[self.end_time] * len(self.jobs), production_environment=self.production_environment, jobs=self.jobs, workstations=solution, start_time=self.start_time, end_time=self.end_time)
        result, fitness = pso.run(max_generations=max_generations, personal_weight=personal_weight, global_weight=global_weight, inertia=inertia, min_velocities=min_velocities, max_velocities=max_velocities)
        return result, fitness[0]

    class GA:

        def __init__(self):
            pass


    def __init__(self, production_environment : ProductionEnvironment):
        self.production_environment = production_environment
        GAPSONestedSolver.instance = self

    def _evaluate(solution, solution_idx) -> float:
        _, fitness = GAPSONestedSolver.instance._run_inner(solution) # TODO: parameter
        return -fitness

    def run(self, encoding : list[int], jobs : list[Job], start_time : int = 0, end_time : int = 0):
        max_generations = 1000
        population_size = 100
        self.jobs = jobs
        self.encoding = encoding
        outer_encoding = self.encoding[::2]
        self.gene_space = []
        for job in self.jobs:
            possibilities = self.production_environment.get_available_workstations_for_task(job.task)
            possible_ids = [int(x.id) for x in possibilities]
            self.gene_space.append(possible_ids)
        # TODO: switch to inner class GA
        self.outer_solver = pygad.GA(num_generations=max_generations, num_parents_mating=int(population_size/2), fitness_func=GAPSONestedSolver._evaluate, sol_per_pop=population_size, num_genes=len(outer_encoding), parent_selection_type='tournament', keep_parents=0, crossover_type='two_points', mutation_type='random', mutation_percent_genes=10, gene_type=int, gene_space=self.gene_space, K_tournament=int(population_size/4))
        self.outer_solver.run()
        self.outer_solution, self.outer_solution_fitness, self.outer_solution_idx = self.outer_solver.best_solution()

        self.final_result, self.fitness = self._run_inner(self.outer_solution) # TODO: parameter
        