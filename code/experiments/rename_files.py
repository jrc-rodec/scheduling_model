import os
path = r'C:\Users\huda\Documents\Benchmarks\WFJSSP'

instances = os.listdir(path)
#for source in sources:
#instances = os.listdir(benchmark_path + '/' + source)
for instance in instances:
    try:
        current_path = path + '\\' + instance + '\\'
        benchmarks = os.listdir(current_path)
        for benchmark in benchmarks:
            original = os.path.join(current_path, benchmark)
            updated = os.path.join(current_path, benchmark[:-12] + '.fjs')
            os.rename(original, updated)
    except:
        pass