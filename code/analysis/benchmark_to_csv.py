import sys
import os
import csv
from benchmarkrewriter.benchmark_parser import BenchmarkParser, WorkerBenchmarkParser
import statistics
def get_max_w(durations):
    max = 0
    for operation in durations:
        for machine in operation:
            for worker in machine:
                if worker > max:
                    max = worker
    return max

def get_max(durations):
    max = 0
    for operation in durations:
        for machine in operation:
        
            if machine > max:
                max = machine
    return max

def worker_flexibility(benchmark):
    n_assignments = 0
    m = benchmark.n_machines()
    o = benchmark.n_operations()
    durations = benchmark.durations()
    combs = dict()
    for i in range(len(durations)):
        for j in range(len(durations[i])):
            for k in range(len(durations[i][j])):
                if durations[i][j][k] > 0:
                    n_assignments += 1
                combs[(j,k)] = 1
    average_assignments = n_assignments / o
    return average_assignments / len(combs)

def flexibility(benchmark):
    n_assignments = 0
    m = benchmark.n_machines()
    o = benchmark.n_operations()
    durations = benchmark.durations()
    for i in range(len(durations)):
        for j in range(len(durations[i])):
            if durations[i][j] > 0:
                n_assignments += 1
    average_assignments = n_assignments / o
    return average_assignments / n_assignments

def get_flexibility_and_dv_worker(benchmark):
    all = 0
    unique = []
    machines_available = 0
    durations = benchmark.durations()
    for i in range(len(durations)):
        for j in range(len(durations[i])):
            for k in range(len(durations[i][j])):
                if durations[i][j][k] > 0:
                    if durations[i][j][k] not in unique:
                        unique.append(durations[i][j][k])
                    all += 1
            if any([x > 0 for x in durations[i][j]]):
                machines_available+=1
    return worker_flexibility(benchmark), len(unique) / all

def get_flexibility_and_dv(benchmark):
    all = 0
    unique = []
    machines_available = 0
    durations = benchmark.durations()
    for i in range(len(durations)):
        for j in range(len(durations[i])):
            if durations[i][j] > 0:
                if durations[i][j] not in unique:
                    unique.append(durations[i][j])
                all += 1
        if any([x > 0 for x in durations[i]]):
            machines_available+=1
    return flexibility(benchmark), len(unique) / all

def remap(name):
    if name.startswith('_'):
        name = name[1:]
    values = name.split('_')
    if values[0].startswith('Behnke'):
        return 'Behnke'+values[1]
    if values[0].startswith('Brandimarte'):
        return 'BrandimarteMk'+values[1]
    if values[0].startswith('Chambers'):
        return 'ChambersBarnes'+values[1]
    if values[0].startswith('HurinkS'):
        return 'HurinkSdata'+values[1]
    if values[0].startswith('HurinkE'):
        return 'HurinkEdata'+values[1]
    if values[0].startswith('HurinkR'):
        return 'HurinkRdata'+values[1]
    if values[0].startswith('HurinkV'):
        return 'HurinkVdata'+values[1]
    if values[0].startswith('DP'):
        return 'DPpaulli'+values[1]
    if values[0].startswith('Kacem'):
        return 'Kacem'+values[1]
    if values[0].startswith('Fattahi'):
        return 'Fattahi'+values[1]
    return name

def read_fjssp(path):
    result = []
    benchmarks = os.listdir(path)
    for benchmark in benchmarks:
        parser = BenchmarkParser()
        data = parser.parse_benchmark(path + '/' + benchmark)
        f, dv = get_flexibility_and_dv(data)
        instance_name = benchmark[:-4]#remap(benchmark[2:-12])
        metrics = dict()

        max_duration = get_max(data.durations())
        counts = [0] * (max_duration+1)
        min_duration = float('inf')
        all_durations = []
        for operation in data.durations():
            for machine in operation:
                if machine > 0:
                    all_durations.append(machine)
                    counts[machine] += 1
                    if machine < min_duration:
                        min_duration = machine
        d_distinct = len([x for x in range(len(counts)) if counts[x] > 0])
        d_unique = len([x for x in range(len(counts)) if counts[x] == 1])
        d_shared = len([x for x in range(len(counts)) if counts[x] > 1])
        #all_d = statistics.stdev([x*counts[x] for x in range(len(counts))])
        #metrics['d_distinct'] = d_distinct
        #metrics['d_unique'] = d_unique
        #metrics['d_shared'] = d_shared
        #metrics['d_average'] = sum(counts)/data.n_operations()

        #Source;Instance;n_jobs;n_machines;n_operations;flexibility;duration_variety;average_operations_per_job;min_duration;max_duration;duration_span;duration_stdev;mean

        #result.append({'source': instance_name, 'n_operations': data.n_operations(), 'flexibility': f, 'duration_variety': dv, 'n_machines': data.n_machines(), 'n_jobs': data.n_jobs(), 'average_operations_per_job': data.n_operations()/data.n_jobs(), 'd_max': max_duration, 'd_min': min_duration, 'd_distinct': d_distinct, 'd_unique': d_unique, 'd_shared': d_shared, 'd_average': sum(counts)/data.n_operations()})
        result.append([instance_name, data.n_operations(), f, dv, data.n_machines(), data.n_jobs(), data.n_operations()/data.n_jobs(), max_duration, min_duration, d_distinct, d_unique, d_shared, sum(all_durations)/len(all_durations)])
    return result

def read_fjssp_w(path):
    result = []
    benchmarks = os.listdir(path)
    for benchmark in benchmarks:
        parser = WorkerBenchmarkParser()
        data = parser.parse_benchmark(path + '/' + benchmark)
        f, dv = get_flexibility_and_dv_worker(data)
        instance_name = remap(benchmark[2:-12])
        metrics = dict()

        max_duration = get_max_w(data.durations())
        counts = [0] * (max_duration+1)
        min_duration = float('inf')
        all_durations = []
        for operation in data.durations():
            for machine in operation:
                for worker in machine:
                    if worker > 0:
                        all_durations.append(worker)
                        counts[worker] += 1
                        if worker < min_duration:
                            min_duration = worker
        d_distinct = len([x for x in range(len(counts)) if counts[x] > 0])
        d_unique = len([x for x in range(len(counts)) if counts[x] == 1])
        d_shared = len([x for x in range(len(counts)) if counts[x] > 1])
        #metrics['d_distinct'] = d_distinct
        #metrics['d_unique'] = d_unique
        #metrics['d_shared'] = d_shared
        #metrics['d_average'] = sum(counts)/data.n_operations()
        #result[instance_name] = {'n_operations': data.n_operations(), 'flexibility': f, 'duration_variety': dv, 'n_machines': data.n_machines(), 'additional_metrics': metrics}
        #result.append({'source': instance_name, 'n_operations': data.n_operations(), 'flexibility': f, 'duration_variety': dv, 'n_machines': data.n_machines(), 'n_jobs': data.n_jobs(), 'average_operations_per_job': data.n_operations()/data.n_jobs(), 'd_max': max_duration, 'd_min': min_duration, 'd_distinct': d_distinct, 'd_unique': d_unique, 'd_shared': d_shared, 'd_average': sum(counts)/data.n_operations()})
        result.append([instance_name, data.n_operations(), f, dv, data.n_machines(), data.n_jobs(), data.n_operations()/data.n_jobs(), max_duration, min_duration, d_distinct, d_unique, d_shared, sum(all_durations)/len(all_durations), data.n_workers()])
    return result
    

if __name__ == '__main__':
    mode = 'FJSSP'
    outpath = r'C:\Users\huda\Desktop\Data'
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    if mode == 'FJSSP-W':
        data = read_fjssp_w(r'C:\Users\huda\Documents\GitHub\scheduling_model_jrc\code\upgrades\benchmarks_with_workers')
        outpath += r'\FJSSP-W\data.csv'
    else:
        data = read_fjssp(r'C:\Users\huda\Documents\GitHub\scheduling_model_jrc\code\upgrades\benchmarks\all')
        outpath += r'\FJSSP\data.csv'
    header = ['source', 'n_operations', 'flexibility', 'duration_variety', 'n_machines', 'n_jobs', 'average_operations_per_job', 'd_max', 'd_min', 'd_distinct', 'd_unique', 'd_shared', 'd_average']
    if mode == 'FJSSP-W':
        header.append('n_worker')
    #write_data = []
    with open(outpath, 'w', newline='') as o:
        writer = csv.writer(o)
        writer.writerow(header)
        writer.writerows(data)
