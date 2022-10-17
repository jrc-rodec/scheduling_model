class Workstation:

    def __init__(self, id, name, basic_resources, tasks):
        self.id = id
        self.external_id = id
        self.external_id = self.id
        self.name = name
        self.basic_resources = basic_resources # list of resources necessary to operate the workstation independent of performed task
        self.tasks = tasks # tasks which can be done with this workstation

class Task:

    def __init__(self, id, name, resources, result_resources, preceding_tasks, follow_up_tasks, independent, prepare_time, unprepare_time, alternatives):
        self.id = id
        self.external_id = id
        self.name = name
        self.resources = resources
        self.result_resources = result_resources
        self.preceding_tasks = preceding_tasks
        self.follow_up_tasks = follow_up_tasks
        self.independent = independent
        self.prepare_time = prepare_time
        self.unprepare_time = unprepare_time
        self.alternatives = alternatives

class Recipe:

    def __init__(self, id, name, tasks):
        self.id = id
        self.external_id = id
        self.name = name
        self.tasks = tasks
