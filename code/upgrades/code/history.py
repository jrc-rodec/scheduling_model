import json
from collections import namedtuple


class History:

    def __init__(self):
        self.instance = ''
        self.overall_best : list[tuple[float, list[tuple[int, int]]]] = [] # best of all runs
        self.run_best : list[tuple[float, list[tuple[int, int]]]] = [] # best of current run before restart
        self.generation_best : list[tuple[float, list[tuple[int, int]]]] = [] # best of each generation
        self.mutation_probability : list[float] = []
        self.restart_generations : list[int] = []
        self.time_checkpoints : list[tuple[float, list[tuple[int, int]]]] = []

        self.function_evaluations : int = 0
        self.generations : int = 0
        self.runtime : int = 0 # in seconds

        # parameters
        self.population_size : int = 0
        self.offspring_amount : int = 0
        self.restart_time : int = 0 # after how many generations without progress
        self.max_mutation_rate : float = 0
        self.elitism_rate : float = 0
        self.tournament_size : float = 0
        self.population_growth : int = 0

        self.time_limit : int = 0
        self.max_generations : int = 0
        self.target_fitness : float = 0
        self.function_evaluation_limit : int = 0

        # reason the GA stopped
        self.generations_reached = False
        self.time_exceeded = False
        self.function_evaluations_exceeded = False
        self.target_fitness_reached = False

        # production environment information
        self.required_operations : list[int] = []
        self.available_machines : list[list[int]] = [] # available machines for each operation
        self.durations : list[list[int]] = [] # durations on machines

    # make using the history objects easier
    def overall_best_fitness(self) -> list[float]:
        return [x[0] for x in self.overall_best]

    def run_best_fitness(self) -> list[float]:
        return [x[0] for x in self.run_best]
    
    def generation_best_fitness(self) -> list[float]:
        return [x[0] for x in self.generation_best]
    
    def average_dissimilarity_history(self, use_list : str = 'overall') -> list[float]:
        history : list[float] = []
        in_list = None
        if use_list == 'overall':
            in_list = self.overall_best
        elif use_list == 'run':
            in_list = self.run_best
        elif use_list == 'generation':
            in_list = self.generation_best
        else:
            in_list = self.time_checkpoints
        
        for entry in in_list:
            average = 0.0
            # get average distance for every entry to each other entry
            for i in range(len(entry[1])):
                current_average = 0.0
                for j in range(len(entry[1])):
                    if i != j:
                        current_average += self.get_dissimilarity(entry[1][i], entry[1][j])
                current_average = current_average / (len(entry[1]))
                average += current_average
            history.append(average/len(entry[1]))
        return history
    
    def get_dissimilarity(self, a, b):
        dissimilarity = 0
        # 0 - sequence, 1 - assignment
        for i in range(len(a[0])):
            if a[1][i] != b[1][i]:
                dissimilarity += len(self.available_machines[i])
                
            if a[0][i] != b[0][i]:
                dissimilarity += 1
        return dissimilarity
    
    def to_file(self, path : str):
        with open(path, 'w') as f:
            json.dump(self, f, default=History._transform)

    def _transform(obj):
        return obj.__dict__
 
    def from_file(path : str):
        history = None
        with open(path, 'r') as f:
            #...
            #file_data = json.load(f)
            #as_str = json.dumps(file_data)
            #history = json.loads(as_str, object_hook = lambda d : namedtuple('History', file_data.keys()))
            #history = json.loads(as_str, object_hook = lambda d : namedtuple('History', file_data.keys()))
            history = json.load(f, cls=HistoryDecoder)#, object_hook=History.object_hook)
        restored = History()
        restored.instance = history['instance']
        restored.overall_best = history['overall_best']
        restored.run_best = history['run_best']
        restored.generation_best = history['generation_best']
        restored.mutation_probability = history['mutation_probability']
        restored.restart_generations = history['restart_generations']
        restored.time_checkpoints = history['time_checkpoints']

        restored.function_evaluations = history['function_evaluations']
        restored.generations = history['generations']
        restored.runtime = history['runtime']

        restored.population_size = history['population_size']
        restored.offspring_amount = history['offspring_amount']
        restored.restart_time = history['restart_time']
        restored.max_mutation_rate = history['max_mutation_rate']
        restored.elitism_rate = history['elitism_rate']
        restored.tournament_size = history['tournament_size']
        restored.population_growth = history['population_growth']

        restored.time_limit = history['time_limit']
        restored.max_generations = history['max_generations']
        restored.target_fitness = history['target_fitness']
        restored.function_evaluation_limit = history['function_evaluation_limit']

        restored.generations_reached = history['generations_reached']
        restored.time_exceeded = history['time_exceeded']
        restored.function_evaluations_exceeded = history['function_evaluations_exceeded']
        restored.target_fitness_reached = history['target_fitness_reached']

        restored.required_operations = history['required_operations']
        restored.available_machines  = history['available_machines']
        restored.durations  = history['durations']
        
        return restored
    

class HistoryDecoder(json.JSONDecoder):

    def object_hook(self, o):
        history = History()
        history.instance = o.get('instance')
        history.overall_best = o.get('overall_best')
        history.run_best = o.get('run_best')
        history.generation_best = o.get('generation_best')
        history.mutation_probability = o.get('mutation_probability')
        history.restart_generations = o.get('restart_generation')
        history.time_checkpoints = o.get('time_checkpoints')

        history.function_evaluations = o.get('function_evaluations')
        history.generations = o.get('generations')
        history.runtime = o.get('runtime')

        history.population_size = o.get('population_size')
        history.offspring_amount = o.get('offspring_amount')
        history.restart_time = o.get('restart_time')
        history.max_mutation_rate = o.get('max_mutation_rate')
        history.elitism_rate = o.get('elitism_rate')
        history.tournament_size = o.get('tournament_size')
        history.population_growth = o.get('population_growth')

        history.time_limit = o.get('time_limit')
        history.max_generations = o.get('max_generations')
        history.target_fitness = o.get('target_fitness')
        history.function_evaluation_limit = o.get('function_evaluation_limit')

        history.generations_reached = o.get('generations_reached')
        history.time_exceeded = o.get('time_exceeded')
        history.function_evaluations_exceeded = o.get('function_evaluations_exceeded')
        history.target_fitness_reached = o.get('target_fitness_reached')

        history.required_operations = o.get('required_operations')
        history.available_machines  = o.get('available_machines')
        history.durations  = o.get('durations')
        return history