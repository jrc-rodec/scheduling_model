import os

def write_result(benchmark_name : str, solver_name : str, objective_values : list[float], parameters : str = '') -> None:
    current_director = os.getcwd()
    objectives = ''
    for objective in objective_values:
        objectives += f'{objective};'
    with open(f'{current_director}\\code\\reworked_data_model\\results\\results.csv', 'a') as f:
        f.write(f'{benchmark_name};{solver_name};{objectives}{parameters};\n')