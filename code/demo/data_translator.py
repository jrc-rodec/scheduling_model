from models import Workstation, Task, Recipe
import random

class DataTranslator:
    pass

class TestTranslator(DataTranslator): # no resources used for this dataset

    def translate(self, n_workstations, recipies, processing_times):
        workstations =  []
        recipies_list = []
        r_id = 0
        tasks =  []
        for w_id in range(n_workstations):
            workstations.append(Workstation(w_id, f'w{w_id}', [], [])) # id, name, basic resources, tasks
        t_id = 0
        for recipe in recipies:
            tasks_for_recipe = []
            for i in range(recipe):
                alternatives = [] # needed for this dataset, also easier for other datasets, could be replaced by searching for tasks with same result resources (if given)
                w_id = 0
                for duration in processing_times[i]:
                    # create task + add to workstation
                    task = Task(t_id, f't{t_id}', [], [], [], [], True, 0, 0, []) # id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time, alternatives
                    t_id = t_id + 1
                    alternatives.append(task)
                    workstations[w_id].tasks.append((t_id, duration))
                    w_id = w_id + 1
                    tasks.append(task) # add to list of all tasks
                for task in alternatives:
                    task.alternatives = alternatives.copy()
                    task.alternatives.remove(task) # remove self from alternative list
                tasks_for_recipe.append(random.choice(alternatives)) # choose random task as placeholder in recipe
            recipies_list.append(Recipe(r_id, f'r{r_id}', tasks_for_recipe))
            r_id = r_id + 1
        return recipies_list, workstations, [], tasks, [] # recipies, workstations, resources, tasks, orders

"""from hybrid_solution_data_loader import get_data

n_workstations, recipes, operation_times = get_data(0)
recipies, workstations, resources, tasks, orders = TestTranslator().translate(n_workstations, recipes, operation_times)
print('end')"""