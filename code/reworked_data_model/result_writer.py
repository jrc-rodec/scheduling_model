import os
from model import Schedule

def write_result(schedule : Schedule, benchmark_name : str, solver_name : str, objective_values : list[float], parameters : str = '', solution = None) -> None:
    current_director = os.getcwd()
    objectives = ''
    for objective in objective_values:
        objectives += f'{objective};'
    solution_string = ''
    if solution:
        solution_string = f'{str(solution)};'
    output = f'{benchmark_name};{solver_name};{solution_string}{objectives}{parameters};'
    with open(f'{current_director}\\code\\reworked_data_model\\results\\results.csv', 'a') as f:
        f.write(f'{output}\n')