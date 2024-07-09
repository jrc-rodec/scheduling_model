import numpy as np

class UncertaintySimulation:

    def __init__(self, problem_seed = None, simulation_seed = None) -> None:
        if not problem_seed:
            problem_seed = np.random.RandomState()
        else:
            self.problem_rng = np.random.RandomState(problem_seed)
        if not simulation_seed:
            self.simulation_rng = np.random.RandomState()
        else:
            self.simulation_rng = np.random.RandState(simulation_seed)
        self.problem_seed = problem_seed
        self.simulation_seed = simulation_seed
        self.initialized = False

    def initialize_problem(self, durations : list[list[int]], job_operation_mapping : list[int], mttr_range : float = 0.2, mttf_range : float = 0.3, duration_range : float = 0.1, n_simulations : int = 20) -> None:# -> tuple[list[float], list[float]]:
        # NOTE: both MTTR and duration uncertainty are fixed for each machine
        self.n_machines = len(durations[0])
        self.n_operations = len(durations)
        duration_values = []
        durations_on_machines : list[list[int]] = [[] for _ in range(self.n_machines)]
        for i in range(len(durations)):
            for j in range(len(durations[i])):
                if durations[i][j] > 0:
                    duration_values.append(durations[i][j])
                    durations_on_machines[j].append(durations[i][j])
        median_durations_on_machines = [np.median(machine) for machine in durations_on_machines]
        median_duration = np.median(duration_values)
        self.mttr : list[float] = []
        self.mttf : list[float] = []

        self.job_operations = job_operation_mapping.copy()
        self.fail_probability = 1 / self.n_machines

        self.duration : list[int] = []
        for i in range(self.n_machines):
            self.mttr.append(self.problem_rng.normal(median_duration, mttr_range))
            self.mttf.append(self.problem_rng.normal(median_durations_on_machines[i], mttf_range))
            self.duration.append(self.problem_rng.random() * duration_range)
        self.duration_range = duration_range
        self.mttr_range = mttr_range
        self.mttf_range = mttf_range
        self.durations = durations
        self.n_simulations = n_simulations
        self.initialized = True
        # NOTE: return necessary?
        #return self.mttr, self.mttf, self.duration

    def overlaps(self, start : int, duration : int, breakdown : list[int]) -> bool:
        return (start >= breakdown[0] and start <= breakdown[0]+breakdown[1]) or start+duration >= breakdown[0] and start+duration <= breakdown[0]+breakdown[1]

    def shift(self, start_a : int, duration_a : int, start_b : int, duration_b : int) -> int:
        end_a = start_a + duration_a
        #end_b = start_b + duration_b
        if start_b < end_a:
            return start_b - end_a
        return 0

    def simulate(self, start_times : list[int], machine_assignments : list[int]) -> tuple[float, float]:
        # returns makespan and robust makespan
        makespan = 0.0
        robust_makespan = 0.0
        mean_deterioation = 0.0
        for i in range(len(self.durations)):
            end = start_times[i] + self.durations[i][machine_assignments[i]]
            if end > makespan:
                makespan = end

        for i in range(self.n_simulations):
            machine_breakdown_events = []
            for j in range(self.n_machines):
                if self.simulation_rng.random() < self.fail_probability:
                    time = np.max(0, np.floor(self.mttf[j] + self.simulation_rng.standard_normal() * self.mttf[j]))
                    duration = np.max(0, np.floor(self.mttr[j] + self.simulation_rng.standard_normal() * self.mttr[j]))
                    machine_breakdown_events.append([time, duration])
                else:
                    machine_breakdown_events.append([0,0])
            
                for j in range(len(self.durations)):
                    simulation_durations = self.durations[j][machine_assignments[j]]
            prev_job = 0
            end_on_machines = [0] * self.n_machines
            for j in range(len(self.durations)):
                duration = simulation_durations[j]
                job_shift = 0
                machine_shift = 0
                if j > 0 and prev_job == self.job_operations[j]:
                    # check if job sequence needs to shift
                    job_shift = self.shift(start_times[j], duration, start_times[j-1], simulation_durations[j-1])
                if start_times[j] < end_on_machines[machine_assignments[j]]:
                    # check if there was a shift previously on the assigned machine
                    machine_shift = end_on_machines[machine_assignments[j]] - start_times[j]
                shift = np.max(job_shift, machine_shift)
                start_times[j] += shift
                # check for machine breakdowns
                if machine_breakdown_events[machine_assignments[j]][1] > 0 and self.overlaps(start_times[j], duration, machine_breakdown_events[machine_assignments[j]]):
                    # move start time to the end of the repair time
                    start_times[j] = machine_breakdown_events[machine_assignments[j]][0] + machine_breakdown_events[machine_assignments[j]][1]
                end_on_machines[machine_assignments[j]] = start_times[j] + duration
                prev_job = self.job_operations[j]
            # determine new makespan
            makespan_after_shift = 0.0
            for j in range(len(self.durations)):
                end = start_times[j] + simulation_durations[j]
                if end > makespan_after_shift:
                    makespan_after_shift = end
            
            difference = makespan_after_shift - makespan
            deterioration = difference / makespan
            mean_deterioation += deterioration
            # TODO: compare to other robustness measures, robustness weight as parameter
            robustness_weight = 0.7
            # NOTE: taken from old paper
            robust_makespan += robustness_weight * makespan + (1-robustness_weight) * difference

        return robust_makespan / self.n_simulations, makespan, mean_deterioation / self.n_simulations
