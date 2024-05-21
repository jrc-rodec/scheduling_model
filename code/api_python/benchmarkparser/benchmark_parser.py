class BenchmarkParser: 
    def __init__(self):
        pass

    def parse_benchmark(self, path: str):
        file_content = []

        try:
            file = open(path, 'r')
            file_content = file.readlines()
        except Exception as exception: print(exception) 

        info = file_content[0].split(' ')
        n_machines = int(info[1])
        n_overall_operations = 0
        lines = list(range(file_content.count() - 1))
        for i in range(1, file_content.count()):
            line = file_content[i].split(' ')
            lines[i - 1] = line
            n_overall_operations += int(line[0])

        durations = [n_overall_operations, n_machines]
        operation_index = 0
        job_sequence = range(n_overall_operations)

        for i in range(1, len(lines)):
            line = lines[i-1]
            n_operations = int(line[0])
            index = 1
            for j in range(0, n_operations):
                job_sequence[operation_index] = i-1
                n_options = int(line[index])
                index +=1
                for k in range(0, n_options):
                    machine = int(line[index])
                    index += 1
                    duration = int(line[index])
                    index += 1
                    durations[operation_index, machine - 1] = duration
                operation_index += 1
        return Encoding(durations, job_sequence)

        lines = [line.split(' ') for line in file_content[1:]]
        for line in lines:
            n_overall_operations += int(line[0])

        durations = [[0 for _ in range(n_machines)] for _ in range(n_overall_operations)]
        job_sequence = [0] * n_overall_operations
        operation_index = 0
        for i, line in enumerate(lines):
            n_operations = int(line[0])
            index = 1
            for _ in range(n_operations):
                job_sequence[operation_index] = i
                n_options = int(line[index])
                index += 1
                for _ in range(n_options):
                    machine = int(line[index]) - 1
                    duration = int(line[index+1])
                    durations[operation_index][machine] = duration
                    index += 2
                operation_index += 1

        return Encoding(durations, job_sequence)



