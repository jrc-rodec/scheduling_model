# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 08:33:25 2024

@author: tst
"""

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Bsp von https://developers.google.com/optimization/introduction/python
if 1==0:
    from ortools.linear_solver import pywraplp
    
    
    def main():
        # Create the linear solver with the GLOP backend.
        solver = pywraplp.Solver.CreateSolver("GLOP")
        if not solver:
            return
    
        # Create the variables x and y.
        x = solver.NumVar(0, 1, "x")
        y = solver.NumVar(0, 2, "y")
    
        print("Number of variables =", solver.NumVariables())
    
        # Create a linear constraint, 0 <= x + y <= 2.
        ct = solver.Constraint(0, 2, "ct")
        ct.SetCoefficient(x, 1)
        ct.SetCoefficient(y, 1)
    
        print("Number of constraints =", solver.NumConstraints())
    
        # Create the objective function, 3 * x + y.
        objective = solver.Objective()
        objective.SetCoefficient(x, 3)
        objective.SetCoefficient(y, 1)
        objective.SetMaximization()
    
        print(f"Solving with {solver.SolverVersion()}")
        solver.Solve()
    
        print("Solution:")
        print("Objective value =", objective.Value())
        print("x =", x.solution_value())
        print("y =", y.solution_value())
    
    
    if __name__ == "__main__":
        main()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Bsp von https://developers.google.com/optimization/cp/cp_solver
if 1==0:
    from ortools.sat.python import cp_model
    
    
    class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""
    
        def __init__(self, variables: list[cp_model.IntVar]):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__variables = variables
            self.__solution_count = 0
    
        def on_solution_callback(self) -> None:
            self.__solution_count += 1
            for v in self.__variables:
                print(f"{v}={self.value(v)}", end=" ")
            print()
    
        @property
        def solution_count(self) -> int:
            return self.__solution_count
    
    
    def search_for_all_solutions_sample_sat():
        """Showcases calling the solver to search for all solutions."""
        # Creates the model.
        model = cp_model.CpModel()
    
        # Creates the variables.
        num_vals = 3
        x = model.new_int_var(0, num_vals - 1, "x")
        y = model.new_int_var(0, num_vals - 1, "y")
        z = model.new_int_var(0, num_vals - 1, "z")
    
        # Create the constraints.
        model.add(x != y)
        #model.add(y != z)
        #model.add(x!= z)
    
        # Create a solver and solve.
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter([x, y, z])
        # Enumerate all solutions.
        solver.parameters.enumerate_all_solutions = True
        # Solve.
        status = solver.solve(model, solution_printer)
    
        print(f"Status = {solver.status_name(status)}")
        print(f"Number of solutions found: {solution_printer.solution_count}")
    
    
    search_for_all_solutions_sample_sat()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""Simple solve."""
if 1 == 0:
    
    from ortools.sat.python import cp_model
    
    
    def main() -> None:
        """Minimal CP-SAT example to showcase calling the solver."""
        # Creates the model.
        model = cp_model.CpModel()
    
        # Creates the variables.
        var_upper_bound = max(50, 45, 37)
        x = model.new_int_var(0, var_upper_bound, "x")
        y = model.new_int_var(0, var_upper_bound, "y")
        z = model.new_int_var(0, var_upper_bound, "z")
    
        # Creates the constraints.
        model.add(2 * x + 7 * y + 3 * z <= 50)
        model.add(3 * x - 5 * y + 7 * z <= 45)
        model.add(5 * x + 2 * y - 6 * z <= 37)
    
        model.maximize(2 * x + 2 * y + 3 * z)
    
        # Creates a solver and solves the model.
        solver = cp_model.CpSolver()
        status = solver.solve(model)
    
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print(f"Maximum of objective function: {solver.objective_value}\n")
            print(f"x = {solver.value(x)}")
            print(f"y = {solver.value(y)}")
            print(f"z = {solver.value(z)}")
        else:
            print("No solution found.")
    
        # Statistics.
        print("\nStatistics")
        print(f"  status   : {solver.status_name(status)}")
        print(f"  conflicts: {solver.num_conflicts}")
        print(f"  branches : {solver.num_branches}")
        print(f"  wall time: {solver.wall_time} s")
    
    
    if __name__ == "__main__":
        main()
        
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Bsp von https://developers.google.com/optimization/cp/cryptarithmetic 
"""Cryptarithmetic puzzle.

First attempt to solve equation CP + IS + FUN = TRUE
where each letter represents a unique digit.

This problem has 72 different solutions in base 10.
"""
if 1 == 0:
    from ortools.sat.python import cp_model
    
    
    #Solution printer nicht notwendig da schon zeile 56ff
    
    """class VarArraySolutionPrinter(cp_model.CpSolverSolutionCallback):
        #Print intermediate solutions.
    
        def __init__(self, variables: list[cp_model.IntVar]):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__variables = variables
            self.__solution_count = 0
    
        def on_solution_callback(self) -> None:
            self.__solution_count += 1
            for v in self.__variables:
                print(f"{v}={self.value(v)}", end=" ")
            print()
    
        @property
        def solution_count(self) -> int:
            return self.__solution_count """
        
    def main() -> None:
        """solve the CP+IS+FUN==TRUE cryptarithm."""
        # Constraint programming engine
        model = cp_model.CpModel()
    
        base = 11
    
        c = model.new_int_var(1, base - 1, "C")
        p = model.new_int_var(0, base - 1, "P")
        i = model.new_int_var(1, base - 1, "I")
        s = model.new_int_var(0, base - 1, "S")
        f = model.new_int_var(1, base - 1, "F")
        u = model.new_int_var(0, base - 1, "U")
        n = model.new_int_var(0, base - 1, "N")
        t = model.new_int_var(1, base - 1, "T")
        r = model.new_int_var(0, base - 1, "R")
        e = model.new_int_var(0, base - 1, "E")
    
        # We need to group variables in a list to use the constraint AllDifferent.
        letters = [c, p, i, s, f, u, n, t, r, e]
    
        # Verify that we have enough digits.
        assert base >= len(letters)
    
        # Define constraints.
        model.add_all_different(letters)
    
        # CP + IS + FUN = TRUE
        model.add(
            c * base + p + i * base + s + f * base * base + u * base + n
            == t * base * base * base + r * base * base + u * base + e
        )
    
        # Creates a solver and solves the model.
        solver = cp_model.CpSolver()
        solution_printer = VarArraySolutionPrinter(letters)
        # Enumerate all solutions.
        solver.parameters.enumerate_all_solutions = True
        # Solve.
        status = solver.solve(model, solution_printer)
    
        # Statistics.
        print("\nStatistics")
        print(f"  status   : {solver.status_name(status)}")
        print(f"  conflicts: {solver.num_conflicts}")
        print(f"  branches : {solver.num_branches}")
        print(f"  wall time: {solver.wall_time} s")
        print(f"  sol found: {solution_printer.solution_count}")
    
    
    if __name__ == "__main__":
        main()
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Bsp aus https://developers.google.com/optimization/cp/queens
"""OR-Tools solution to the N-queens problem."""
if 1 == 0:

    import sys
    import time
    from ortools.sat.python import cp_model
    
    
    class NQueenSolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""
    
        def __init__(self, queens: list[cp_model.IntVar]):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__queens = queens
            self.__solution_count = 0
            self.__start_time = time.time()
    
        @property
        def solution_count(self) -> int:
            return self.__solution_count
    
        def on_solution_callback(self):
            current_time = time.time()
            print(
                f"Solution {self.__solution_count}, "
                f"time = {current_time - self.__start_time} s"
            )
            self.__solution_count += 1
    
            all_queens = range(len(self.__queens))
            for i in all_queens:
                for j in all_queens:
                    if self.value(self.__queens[j]) == i:
                        # There is a queen in column j, row i.
                        print("Q", end=" ")
                    else:
                        print("_", end=" ")
                print()
            print()
    
    
    
    def main(board_size: int) -> None:
        # Creates the solver.
        model = cp_model.CpModel()
    
        # Creates the variables.
        # There are `board_size` number of variables, one for a queen in each column
        # of the board. The value of each variable is the row that the queen is in.
        queens = [model.new_int_var(0, board_size - 1, f"x_{i}") for i in range(board_size)]
    
        # Creates the constraints.
        # All rows must be different.
        model.add_all_different(queens)
    
        # No two queens can be on the same diagonal.
        model.add_all_different(queens[i] + i for i in range(board_size))
        model.add_all_different(queens[i] - i for i in range(board_size))
    
        # Solve the model.
        solver = cp_model.CpSolver()
        solution_printer = NQueenSolutionPrinter(queens)
        solver.parameters.enumerate_all_solutions = True
        solver.solve(model, solution_printer)
    
        # Statistics.
        print("\nStatistics")
        print(f"  conflicts      : {solver.num_conflicts}")
        print(f"  branches       : {solver.num_branches}")
        print(f"  wall time      : {solver.wall_time} s")
        print(f"  solutions found: {solution_printer.solution_count}")
    
    
    if __name__ == "__main__":
        # By default, solve the 8x8 problem.
        size = 8
        if len(sys.argv) > 1:
            size = int(sys.argv[1])
        main(size)
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Bsp von https://developers.google.com/optimization/scheduling/employee_scheduling
"""Nurse scheduling problem with shift requests."""
if 1 == 0:
    from ortools.sat.python import cp_model
    
    
    def main() -> None:
        # This program tries to find an optimal assignment of nurses to shifts
        # (3 shifts per day, for 7 days), subject to some constraints (see below).
        # Each nurse can request to be assigned to specific shifts.
        # The optimal assignment maximizes the number of fulfilled shift requests.
        num_nurses = 5
        num_shifts = 3
        num_days = 7
        all_nurses = range(num_nurses)
        all_shifts = range(num_shifts)
        all_days = range(num_days)
        shift_requests = [
            [[0, 0, 1], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 1]],
            [[0, 0, 0], [0, 0, 0], [0, 1, 0], [0, 1, 0], [1, 0, 0], [0, 0, 0], [0, 0, 1]],
            [[0, 1, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0], [0, 1, 0], [0, 0, 0]],
            [[0, 0, 1], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 0, 0]],
            [[0, 0, 0], [0, 0, 1], [0, 1, 0], [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 0]],
        ]
    
        # Creates the model.
        model = cp_model.CpModel()
    
        # Creates shift variables.
        # shifts[(n, d, s)]: nurse 'n' works shift 's' on day 'd'.
        shifts = {}
        for n in all_nurses:
            for d in all_days:
                for s in all_shifts:
                    shifts[(n, d, s)] = model.new_bool_var(f"shift_n{n}_d{d}_s{s}")
    
        # Each shift is assigned to exactly one nurse in .
        for d in all_days:
            for s in all_shifts:
                model.add_exactly_one(shifts[(n, d, s)] for n in all_nurses)
    
        # Each nurse works at most one shift per day.
        for n in all_nurses:
            for d in all_days:
                model.add_at_most_one(shifts[(n, d, s)] for s in all_shifts)
    
        # Try to distribute the shifts evenly, so that each nurse works
        # min_shifts_per_nurse shifts. If this is not possible, because the total
        # number of shifts is not divisible by the number of nurses, some nurses will
        # be assigned one more shift.
        min_shifts_per_nurse = (num_shifts * num_days) // num_nurses
        if num_shifts * num_days % num_nurses == 0:
            max_shifts_per_nurse = min_shifts_per_nurse
        else:
            max_shifts_per_nurse = min_shifts_per_nurse + 1
        for n in all_nurses:
            num_shifts_worked = 0
            for d in all_days:
                for s in all_shifts:
                    num_shifts_worked += shifts[(n, d, s)]
            model.add(min_shifts_per_nurse <= num_shifts_worked)
            model.add(num_shifts_worked <= max_shifts_per_nurse)
    
        model.maximize(
            sum(
                shift_requests[n][d][s] * shifts[(n, d, s)]
                for n in all_nurses
                for d in all_days
                for s in all_shifts
            )
        )
    
        # Creates the solver and solve.
        solver = cp_model.CpSolver()
        status = solver.solve(model)
    
        if status == cp_model.OPTIMAL:
            print("Solution:")
            for d in all_days:
                print("Day", d)
                for n in all_nurses:
                    for s in all_shifts:
                        if solver.value(shifts[(n, d, s)]) == 1:
                            if shift_requests[n][d][s] == 1:
                                print("Nurse", n, "works shift", s, "(requested).")
                            else:
                                print("Nurse", n, "works shift", s, "(not requested).")
                print()
            print(
                f"Number of shift requests met = {solver.objective_value}",
                f"(out of {num_nurses * min_shifts_per_nurse})",
            )
        else:
            print("No optimal solution found !")
    
        # Statistics.
        print("\nStatistics")
        print(f"  - conflicts: {solver.num_conflicts}")
        print(f"  - branches : {solver.num_branches}")
        print(f"  - wall time: {solver.wall_time}s")
    
    
    if __name__ == "__main__":
        main()
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Bsp von https://developers.google.com/optimization/scheduling/job_shop
"""Minimal jobshop example."""
if 1 == 0:
    import collections
    from ortools.sat.python import cp_model
    
    
    def main() -> None:
        """Minimal jobshop problem."""
        # Data.
        jobs_data = [  # task = (machine_id, processing_time).
            [(0, 3), (1, 2), (2, 2)],  # Job0
            [(0, 2), (2, 1), (1, 4)],  # Job1
            [(1, 4), (2, 3)],  # Job2
        ]
    
        machines_count = 1 + max(task[0] for job in jobs_data for task in job)
        all_machines = range(machines_count)
        # Computes horizon dynamically as the sum of all durations.
        horizon = sum(task[1] for job in jobs_data for task in job)
    
        # Create the model.
        model = cp_model.CpModel()
    
        # Named tuple to store information about created variables.
        task_type = collections.namedtuple("task_type", "start end interval")
        # Named tuple to manipulate solution information.
        assigned_task_type = collections.namedtuple(
            "assigned_task_type", "start job index duration"
        )
    
        # Creates job intervals and add to the corresponding machine lists.
        all_tasks = {}
        machine_to_intervals = collections.defaultdict(list)
    
        for job_id, job in enumerate(jobs_data):
            for task_id, task in enumerate(job):
                machine, duration = task
                suffix = f"_{job_id}_{task_id}"
                start_var = model.new_int_var(0, horizon, "start" + suffix)
                end_var = model.new_int_var(0, horizon, "end" + suffix)
                interval_var = model.new_interval_var(
                    start_var, duration, end_var, "interval" + suffix
                )
                all_tasks[job_id, task_id] = task_type(
                    start=start_var, end=end_var, interval=interval_var
                )
                machine_to_intervals[machine].append(interval_var)
    
        # Create and add disjunctive constraints.
        for machine in all_machines:
            model.add_no_overlap(machine_to_intervals[machine])
    
        # Precedences inside a job.
        for job_id, job in enumerate(jobs_data):
            for task_id in range(len(job) - 1):
                model.add(
                    all_tasks[job_id, task_id + 1].start >= all_tasks[job_id, task_id].end
                )
    
        # Makespan objective.
        obj_var = model.new_int_var(0, horizon, "makespan")
        model.add_max_equality(
            obj_var,
            [all_tasks[job_id, len(job) - 1].end for job_id, job in enumerate(jobs_data)],
        )
        model.minimize(obj_var)
    
        # Creates the solver and solve.
        solver = cp_model.CpSolver()
        status = solver.solve(model)
    
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            print("Solution:")
            # Create one list of assigned tasks per machine.
            assigned_jobs = collections.defaultdict(list)
            for job_id, job in enumerate(jobs_data):
                for task_id, task in enumerate(job):
                    machine = task[0]
                    assigned_jobs[machine].append(
                        assigned_task_type(
                            start=solver.value(all_tasks[job_id, task_id].start),
                            job=job_id,
                            index=task_id,
                            duration=task[1],
                        )
                    )
    
            # Create per machine output lines.
            output = ""
            for machine in all_machines:
                # Sort by starting time.
                assigned_jobs[machine].sort()
                sol_line_tasks = "Machine " + str(machine) + ": "
                sol_line = "           "
    
                for assigned_task in assigned_jobs[machine]:
                    name = f"job_{assigned_task.job}_task_{assigned_task.index}"
                    # add spaces to output to align columns.
                    sol_line_tasks += f"{name:15}"
    
                    start = assigned_task.start
                    duration = assigned_task.duration
                    sol_tmp = f"[{start},{start + duration}]"
                    # add spaces to output to align columns.
                    sol_line += f"{sol_tmp:15}"
    
                sol_line += "\n"
                sol_line_tasks += "\n"
                output += sol_line_tasks
                output += sol_line
    
            # Finally print the solution found.
            print(f"Optimal Schedule Length: {solver.objective_value}")
            print(output)
        else:
            print("No solution found.")
    
        # Statistics.
        print("\nStatistics")
        print(f"  - conflicts: {solver.num_conflicts}")
        print(f"  - branches : {solver.num_branches}")
        print(f"  - wall time: {solver.wall_time}s")
    
    
    if __name__ == "__main__":
        main()
        
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
if 1==0:
    #!/usr/bin/env python3
    # Copyright 2010-2024 Google LLC
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    
    """Solves a flexible jobshop problems with the CP-SAT solver.
    
    A jobshop is a standard scheduling problem when you must sequence a
    series of task_types on a set of machines. Each job contains one task_type per
    machine. The order of execution and the length of each job on each
    machine is task_type dependent.
    
    The objective is to minimize the maximum completion time of all
    jobs. This is called the makespan.
    """
    
    # overloaded sum() clashes with pytype.
    
    import collections
    
    from ortools.sat.python import cp_model
    
    
    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""
    
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__solution_count = 0
    
        def on_solution_callback(self):
            """Called at each new solution."""
            print(
                "Solution %i, time = %f s, objective = %i"
                % (self.__solution_count, self.wall_time, self.objective_value)
            )
            self.__solution_count += 1
    
    
    def flexible_jobshop():
        """solve a small flexible jobshop problem."""
        # Data part.
        jobs = [  # task = (processing_time, machine_id)
            [  # Job 0
                [(3, 0), (1, 1), (5, 2)],  # task 0 with 3 alternatives
                [(2, 0), (4, 1), (6, 2)],  # task 1 with 3 alternatives
                [(2, 0), (3, 1)],  # task 2 with 3 alternatives , (1, 2)
            ],
            [  # Job 1
                [(2, 0), (3, 1), (4, 2)],
                [(1, 0), (5, 1), (4, 2)],
                [(2, 0), (1, 1), (4, 2)],
            ],
            [  # Job 2
                [(2, 0), (1, 1), (4, 2)],
                [(2, 0), (3, 1), (4, 2)],
                [(3, 0), (1, 1), (5, 2)],
            ],
        ]
    
        num_jobs = len(jobs)
        all_jobs = range(num_jobs)
    
        num_machines = 3
        all_machines = range(num_machines)
    
        # Model the flexible jobshop problem.
        model = cp_model.CpModel()
    
        horizon = 0
        for job in jobs:
            for task in job:
                max_task_duration = 0
                for alternative in task:
                    max_task_duration = max(max_task_duration, alternative[0])
                horizon += max_task_duration
    
        print("Horizon = %i" % horizon)
    
        # Global storage of variables.
        intervals_per_resources = collections.defaultdict(list)
        starts = {}  # indexed by (job_id, task_id).
        presences = {}  # indexed by (job_id, task_id, alt_id).
        job_ends = []
    
        # Scan the jobs and create the relevant variables and intervals.
        for job_id in all_jobs:
            job = jobs[job_id]
            num_tasks = len(job)
            previous_end = None
            for task_id in range(num_tasks):
                task = job[task_id]
    
                min_duration = task[0][0]
                max_duration = task[0][0]
    
                num_alternatives = len(task)
                all_alternatives = range(num_alternatives)
    
                for alt_id in range(1, num_alternatives):
                    alt_duration = task[alt_id][0]
                    min_duration = min(min_duration, alt_duration)
                    max_duration = max(max_duration, alt_duration)
    
                # Create main interval for the task.
                suffix_name = "_j%i_t%i" % (job_id, task_id)
                start = model.new_int_var(0, horizon, "start" + suffix_name)
                duration = model.new_int_var(
                    min_duration, max_duration, "duration" + suffix_name
                )
                end = model.new_int_var(0, horizon, "end" + suffix_name)
                interval = model.new_interval_var(
                    start, duration, end, "interval" + suffix_name
                )
    
                # Store the start for the solution.
                starts[(job_id, task_id)] = start
    
                # Add precedence with previous task in the same job.
                if previous_end is not None:
                    model.add(start >= previous_end)
                previous_end = end
    
                # Create alternative intervals.
                if num_alternatives > 1:
                    l_presences = []
                    for alt_id in all_alternatives:
                        alt_suffix = "_j%i_t%i_a%i" % (job_id, task_id, alt_id)
                        l_presence = model.new_bool_var("presence" + alt_suffix)
                        l_start = model.new_int_var(0, horizon, "start" + alt_suffix)
                        l_duration = task[alt_id][0]
                        l_end = model.new_int_var(0, horizon, "end" + alt_suffix)
                        l_interval = model.new_optional_interval_var(
                            l_start, l_duration, l_end, l_presence, "interval" + alt_suffix
                        )
                        l_presences.append(l_presence)
    
                        # Link the primary/global variables with the local ones.
                        model.add(start == l_start).only_enforce_if(l_presence)
                        model.add(duration == l_duration).only_enforce_if(l_presence)
                        model.add(end == l_end).only_enforce_if(l_presence)
    
                        # Add the local interval to the right machine.
                        intervals_per_resources[task[alt_id][1]].append(l_interval)
    
                        # Store the presences for the solution.
                        presences[(job_id, task_id, alt_id)] = l_presence
    
                    # Select exactly one presence variable.
                    model.add_exactly_one(l_presences)
                else:
                    intervals_per_resources[task[0][1]].append(interval)
                    presences[(job_id, task_id, 0)] = model.new_constant(1)
    
            job_ends.append(previous_end)
    
        # Create machines constraints.
        for machine_id in all_machines:
            intervals = intervals_per_resources[machine_id]
            if len(intervals) > 1:
                model.add_no_overlap(intervals)
    
        # Makespan objective
        makespan = model.new_int_var(0, horizon, "makespan")
        model.add_max_equality(makespan, job_ends)
        model.minimize(makespan)
    
        # Solve model.
        solver = cp_model.CpSolver()
        solution_printer = SolutionPrinter()
        status = solver.solve(model, solution_printer)
    
        # Print final solution.
        for job_id in all_jobs:
            print("Job %i:" % job_id)
            for task_id in range(len(jobs[job_id])):
                start_value = solver.value(starts[(job_id, task_id)])
                machine = -1
                duration = -1
                selected = -1
                for alt_id in range(len(jobs[job_id][task_id])):
                    if solver.value(presences[(job_id, task_id, alt_id)]):
                        duration = jobs[job_id][task_id][alt_id][0]
                        machine = jobs[job_id][task_id][alt_id][1]
                        selected = alt_id
                print(
                    "  task_%i_%i starts at %i (alt %i, machine %i, duration %i)"
                    % (job_id, task_id, start_value, selected, machine, duration)
                )
    
        print("solve status: %s" % solver.status_name(status))
        print("Optimal objective value: %i" % solver.objective_value)
        print("Statistics")
        print("  - conflicts : %i" % solver.num_conflicts)
        print("  - branches  : %i" % solver.num_branches)
        print("  - wall time : %f s" % solver.wall_time)
    
    
    flexible_jobshop()
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#FJSSP mit constraint programming
if 1 == 1:
    import collections
    
    from ortools.sat.python import cp_model
    
    class SolutionPrinter(cp_model.CpSolverSolutionCallback):
        """Print intermediate solutions."""
    
        def __init__(self):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__solution_count = 0
    
        def on_solution_callback(self):
            """Called at each new solution."""
            print(
                "Solution %i, time = %f s, objective = %i"
                % (self.__solution_count, self.wall_time, self.objective_value)
            )
            self.__solution_count += 1
    
    
    #read and arrange Data
    #f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\1_Brandimarte\BrandimarteMk1.fjs')
    #f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\2a_Hurink_sdata\HurinkSdata1.fjs')
    #f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\4_ChambersBarnes\ChambersBarnes17.fjs')
    #f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\5_Kacem\Kacem4.fjs')
    #f = open(r'C:\Users\tst\OneDrive - FH Vorarlberg\Forschung\JobShopScheduling\openHSU_436_2\FJSSPinstances\6_Fattahi\Fattahi19.fjs')
    f = open(r'C:\Users\huda\Documents\GitHub\scheduling_model\code\upgrades\code\benchmarks\6_Fattahi\Fattahi14.fjs')
    
    lines = f.readlines()
    first_line = lines[0].split()
    
    # Number of jobs
    nb_jobs = int(first_line[0])
    # Number of machines
    nb_machines = int(first_line[1])
    # Number of operations for each job
    nb_operations = [int(lines[j + 1].split()[0]) for j in range(nb_jobs)]
    # Constant for incompatible machines
    INFINITE = 1000000
    
    task_processing_time = [[[INFINITE for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]
    
    jobs =  [[[(INFINITE,INFINITE) for m in range(nb_machines)] for o in range(nb_operations[j])] for j in range(nb_jobs)]
    
    for j in range(nb_jobs):
        line = lines[j + 1].split()
        tmp = 0
        for o in range(nb_operations[j]):
            nb_machines_operation = int(line[tmp + o + 1])
            machine_helper =[]
            for i in range(nb_machines_operation):
                machine = int(line[tmp + o + 2 * i + 2]) - 1
                time = int(line[tmp + o + 2 * i + 3])
                machine_helper += [(time,machine)]
                task_processing_time[j][o][machine] = time
            jobs[j][o] = machine_helper
            tmp = tmp + 2 * nb_machines_operation
    
    
     # Trivial upper bound for the start times of the tasks
    L=0
    for j in range(nb_jobs):
        for o in range(nb_operations[j]):
            L += max(task_processing_time[j][o][m] for m in range(nb_machines) if task_processing_time[j][o][m] != INFINITE)
           
    num_jobs = len(jobs)
    all_jobs = range(num_jobs)

    num_machines = nb_machines
    all_machines = range(num_machines)

    # Model the flexible jobshop problem.
    model = cp_model.CpModel()
    
    horizon = L
    """horizon = 0
    for job in jobs:
        for task in job:
            max_task_duration = 0
            for alternative in task:
                max_task_duration = max(max_task_duration, alternative[0])
            horizon += max_task_duration"""

    print("Horizon = %i" % horizon)

    # Global storage of variables.
    intervals_per_resources = collections.defaultdict(list)
    starts = {}  # indexed by (job_id, task_id).
    presences = {}  # indexed by (job_id, task_id, alt_id).
    job_ends = []

    # Scan the jobs and create the relevant variables and intervals.
    for job_id in all_jobs:
        job = jobs[job_id]
        num_tasks = len(job)
        previous_end = None
        for task_id in range(num_tasks):
            task = job[task_id]

            min_duration = task[0][0]
            max_duration = task[0][0]

            num_alternatives = len(task)
            all_alternatives = range(num_alternatives)

            for alt_id in range(1, num_alternatives):
                alt_duration = task[alt_id][0]
                min_duration = min(min_duration, alt_duration)
                max_duration = max(max_duration, alt_duration)

            # Create main interval for the task.
            suffix_name = "_j%i_t%i" % (job_id, task_id)
            start = model.new_int_var(0, horizon, "start" + suffix_name)
            duration = model.new_int_var(
                min_duration, max_duration, "duration" + suffix_name
            )
            end = model.new_int_var(0, horizon, "end" + suffix_name)
            interval = model.new_interval_var(
                start, duration, end, "interval" + suffix_name
            )

            # Store the start for the solution.
            starts[(job_id, task_id)] = start

            # Add precedence with previous task in the same job.
            if previous_end is not None:
                model.add(start >= previous_end)
            previous_end = end

            # Create alternative intervals.
            if num_alternatives > 1:
                l_presences = []
                for alt_id in all_alternatives:
                    alt_suffix = "_j%i_t%i_a%i" % (job_id, task_id, alt_id)
                    l_presence = model.new_bool_var("presence" + alt_suffix)
                    l_start = model.new_int_var(0, horizon, "start" + alt_suffix)
                    l_duration = task[alt_id][0]
                    l_end = model.new_int_var(0, horizon, "end" + alt_suffix)
                    l_interval = model.new_optional_interval_var(
                        l_start, l_duration, l_end, l_presence, "interval" + alt_suffix
                    )
                    l_presences.append(l_presence)

                    # Link the primary/global variables with the local ones.
                    model.add(start == l_start).only_enforce_if(l_presence)
                    model.add(duration == l_duration).only_enforce_if(l_presence)
                    model.add(end == l_end).only_enforce_if(l_presence)

                    # Add the local interval to the right machine.
                    intervals_per_resources[task[alt_id][1]].append(l_interval)

                    # Store the presences for the solution.
                    presences[(job_id, task_id, alt_id)] = l_presence

                # Select exactly one presence variable.
                model.add_exactly_one(l_presences)
            else:
                intervals_per_resources[task[0][1]].append(interval)
                presences[(job_id, task_id, 0)] = model.new_constant(1)

        job_ends.append(previous_end)

    # Create machines constraints.
    for machine_id in all_machines:
        intervals = intervals_per_resources[machine_id]
        if len(intervals) > 1:
            model.add_no_overlap(intervals)

    # Makespan objective
    makespan = model.new_int_var(0, horizon, "makespan")
    model.add_max_equality(makespan, job_ends)
    model.minimize(makespan)

    # Solve model.
    solver = cp_model.CpSolver()
    solution_printer = SolutionPrinter()
    status = solver.solve(model, solution_printer)

    # Print final solution.
    for job_id in all_jobs:
        print("Job %i:" % job_id)
        for task_id in range(len(jobs[job_id])):
            start_value = solver.value(starts[(job_id, task_id)])
            machine = -1
            duration = -1
            selected = -1
            for alt_id in range(len(jobs[job_id][task_id])):
                if solver.value(presences[(job_id, task_id, alt_id)]):
                    duration = jobs[job_id][task_id][alt_id][0]
                    machine = jobs[job_id][task_id][alt_id][1]
                    selected = alt_id
            print(
                "  task_%i_%i starts at %i (alt %i, machine %i, duration %i)"
                % (job_id, task_id, start_value, selected, machine, duration)
            )

    print("solve status: %s" % solver.status_name(status))
    print("Optimal objective value: %i" % solver.objective_value)
    print("Statistics")
    print("  - conflicts : %i" % solver.num_conflicts)
    print("  - branches  : %i" % solver.num_branches)
    print("  - wall time : %f s" % solver.wall_time)