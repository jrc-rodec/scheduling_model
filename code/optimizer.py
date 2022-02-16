import random

class Optimizer:

    def __init__(self):
        pass

    def optimize(self, assignments, jobs, simulation_environment, last_timeslot):
        pass

class Randomizer(Optimizer):

    def __init__(self):
        super().__init__()
        self.name = "Randomizer"
    
    def optimize(self, assignments, jobs, simulation_environment, last_timeslot):
        for i in range(len(assignments)):
            job = jobs[i]
            assignment = assignments[i]
            workstations = simulation_environment.get_valid_workstations(job.task_id)
            if len(workstations) == 0:
                print(job.task_id)
            assignment[0] = workstations[random.randint(0, len(workstations) - 1)].external_id
            assignment[1] = random.randint(0, last_timeslot)
        return assignments

