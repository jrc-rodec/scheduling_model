import os 
import inspect
import random
import copy

def read_file(source, id) -> list[str]:
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    path = currentdir + '\\..\\external_test_data\\FJSSPinstances\\'
    if source.startswith('0_'):
        target_file = f'Behnke{id}.fjs'
    elif source.startswith('1_'):
        target_file = f'BrandimarteMk{id}.fjs'
    elif source.startswith('2a'):
        target_file = f'HurinkSdata{id}.fjs'
    elif source.startswith('2b'):
        target_file = f'HurinkEdata{id}.fjs'
    elif source.startswith('2c'):
        target_file = f'HurinkRdata{id}.fjs'
    elif source.startswith('2d'):
        target_file = f'HurinkVdata{id}.fjs'
    elif source.startswith('3_'):
        target_file = f'DPaulli{id}a.fjs'
    elif source.startswith('4_'):
        target_file = f'ChambersBarnes{id}.fjs'
    elif source.startswith('5_'):
        target_file = f'Kacem{id}.fjs'
    elif source.startswith('6_'):
        target_file = f'Fattahi{id}.fjs'
    path += f'{source}\\{target_file}'
    file = open(path, 'r')
    return file.readlines()

def rewrite_benchmark(source, id, lower_bound, upper_bound, worker_amount):
    file_content : list[str] = read_file(source, id)
    values = [list(map(int, x.split(' '))) for x in file_content]
    result = []
    result.append(values[0].copy())
    result[0].append(worker_amount)
    print(values)
    #2 2 1 2 1 25 2 30 2 1 1 37 2 1 1 2 32 2 2 1 24 2 33 -> 2 operations, o1 -> 2 workstations, o1 on m1 -> 2 worker -> o1 on m1 with w1 -> 25, o1 on m1 with w2 -> 30, ...
    for line in values[1:]:
        new_line = []
        idx = 0
        for i in range(line[0]): # for each operation
            new_line.append(line[idx])
            idx += 1
            for j in range(int(line[idx])): # for each option
                new_line.append(line[idx])
                idx += 1 # workstation
                new_line.append(line[idx])
                # randomly choose amount of workers
                workers = random.randint(1, worker_amount)
                new_line.append(workers)
                options = random.choices(range(1, worker_amount), k=workers)
                idx += 1 # duration
                original_duration = line[idx]
                for k in options: # for each possible worker
                    worker_duration = random.uniform(original_duration * lower_bound, original_duration * upper_bound)
                    new_line.append(k)
                    new_line.append(worker_duration)
                #idx += 1
        result.append(new_line)
    print(result)


rewrite_benchmark('6_Fattahi', 1, 0.9, 1.1, 3)