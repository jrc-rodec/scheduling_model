import random

class Solver:
    pass

class GASolver(Solver):

    # TODO: inputs needed for each function
    def mutation_function(offsprings, ga_instance):
        for offspring in offsprings:
            p = 1 / (len(offspring)/2) # amount of jobs
            j = 0
            for i in range(len(offspring)):
                if j == 0:
                    if random.random() < p:
                        options = []
                        job = index_to_job(i)
                        for w in range(len(job_durations)):
                            if job_durations[w][job] > 0:
                                options.append(w)
                        # mutate workstation assignment
                        offspring[i] = random.choice(options)
                        # mutate start time
                        offspring[i+1] = random.randint(0, last_slot)
                j += 1
                if j > 1:
                    j = 0
                    
        return offsprings

    def is_feasible(solution):
        j = 0
        order = 0
        for i in range(len(solution)):
            if j == 0:
                job = index_to_job(i)
                
            if j == 1: # timeslot
                # check for last time slot
                if solution[i] + job_durations[solution[i-1]][job] > last_slot:
                    return False
                # check for first slot
                if solution[i] < first_slot: # should never happen
                    return False
            else: # assigned workstation
                # check for overlaps
                y = 0
                for x in range(len(solution)):
                    if y == 0 and not y == i:
                        if solution[y] == solution[i]: # tasks run on the same workstation, check overlap
                            y_job = index_to_job(y)
                            i_start = solution[i+1]
                            y_start = solution[y+1]
                            i_duration = job_durations[solution[i]][job]
                            y_duration = job_durations[solution[y]][y_job]
                            i_end = i_start + i_duration
                            y_end = y_start + y_duration
                            if i_start >= y_start and i_start < y_end:
                                return False
                            if i_end > y_start and i_end <= y_end:
                                return False
                            if y_start >= i_start and y_start < i_end:
                                return False
                            if y_end > i_start and y_end <= i_end:
                                return False
                    y+=1
                    if y > 1:
                        y = 0
                # check for correct sequence
                prev_order = order
                order = index_to_order(i)
                if i != 0 and order == prev_order: # not the first job of the order, check previous jobs
                    l = 1
                    while index_to_order(i - 2*l) == order:
                        prev_start = solution[i - 2*l + 1]
                        prev_end = prev_start + job_durations[solution[i - 2*l]][index_to_job(i-2*l)]
                        start = solution[i+1]
                        if start < prev_end:
                            return False
                        l+=1
            j+=1
            if j > 1:
                j = 0
        return True

    def fitness_function(solution, solution_idx): # NOTE: PyGAD always maximizes
        fitness = 1#0
        if not is_feasible(solution):
            #fitness += last_slot
            return -2 * last_slot
        max = -float('inf')
        min = float('inf')
        j = 0
        for i in range(len(solution)):
            if j == 1: # time assignment
                start = solution[i]
                end = start + job_durations[solution[i-1]][index_to_job(i-1)]
                if end > max:
                    max = end
                if start < min:
                    min = solution[i]
            j+=1
            if j > 1:
                j = 0
        fitness += abs(max - min)
        return -fitness

    def run(self):
        delivery_space = {'low': first_slot, 'high': last_slot}
        workstation_space = {'low': 0, 'high': len(available_workstations)-1}
        gene_space = []
        input = []
        for order in orders:
            for job in available_tasks[order[0]]:
                input.append(0)
                input.append(0)
        j = 0
        for i in range(len(input)): # set lower and upper bounds for mutation for each gene
            if j == 0:
                gene_space.append(workstation_space)
            else:
                gene_space.append(delivery_space)
            j+=1
            if j > 1:
                j = 0

        num_genes = len(input)
        num_generations = 5000
        num_parents_mating = 50
        sol_per_pop = 100
        init_range_low = 0
        init_range_high = last_slot
        parent_selection_type = 'rws'
        keep_parents = 10
        crossover_type = 'two_points'
        mutation_type = mutation_function
        mutation_percentage_genes = 10 # not needed for custom mutation functions
        fitness_func = fitness_function
        gene_type = int

        ga_instance = pygad.GA(num_generations=num_generations, num_parents_mating=num_parents_mating, fitness_func=fitness_func, sol_per_pop=sol_per_pop, num_genes=num_genes, init_range_low=init_range_low, init_range_high=init_range_high, parent_selection_type=parent_selection_type, keep_parents=keep_parents, crossover_type=crossover_type, mutation_type=mutation_type, mutation_percent_genes=mutation_percentage_genes, gene_type=gene_type, gene_space=gene_space)
        ga_instance.run()
        solution, solution_fitness, solution_idx = ga_instance.best_solution()
        print("Parameters of the best solution : {solution}".format(solution=solution))
        print("Fitness value of the best solution = {solution_fitness}".format(solution_fitness=abs(solution_fitness) - 1))