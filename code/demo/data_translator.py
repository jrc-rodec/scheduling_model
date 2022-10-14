class DataTranslator:
    pass

class TestTranslator(DataTranslator):

    def translate(self, n_workstations, recipies, processing_times):
        workstations =  []
        recipies = []
        tasks =  []
        for _ in range(len(n_workstations)):
            #workstations.append(Workstation(...))
            pass
        for recipy in recipies:
            tasks_for_recipe = []
            pass
            for i in range(recipy):
                for duration in processing_times[i]:
                    # create task + add to workstation
                    #workstations[i] ...
                    pass
            # add recipies with all tasks
