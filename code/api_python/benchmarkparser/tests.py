from benchmark_parser import BenchmarkParser, WorkerBenchmarkParser
from encoding import Encoding, WorkerEncoding
import numpy as np

durations = np.array([[1, 2, 0], [4, 0, 6], [0, 8, 9]])
job_sequence = [1, 1, 2, 2, 3, 3, 3, 4]
encoder = Encoding(durations, job_sequence)

worker_durations = np.array([
    [[1, 0, 0], [0, 2, 3]],  
    [[0, 4, 0], [5, 0, 6]],  
    [[0, 0, 7], [8, 0, 0]]   
])
worker_encoder = WorkerEncoding(worker_durations, job_sequence)

# The first dimension represents operations (3 operations in total).
# The second dimension represents machines (2 machines per operation).
# The third dimension represents workers (3 workers per machine).

def test_encoder_n_jobs():
    assert encoder.n_jobs() == 4

def test_encoder_job_sequence():
    assert encoder.job_sequence() == job_sequence
    
def test_encoder_n_operations():
    assert encoder.n_operations() == durations.shape[0]

def test_encoder_n_machines():
    assert encoder.n_machines() == durations.shape[1]

def test_encoder_get_machines_for_operation():
    assert encoder.get_machines_for_operation(2) == [1,2]

def test_encoder_get_machines_for_all_operations():
    assert encoder.get_machines_for_all_operations() == [[0, 1], [0, 2], [1, 2]]

def test_encoder_copy():
    copied = encoder.copy()
    new = Encoding(durations, job_sequence)
    assert copied.n_jobs() == new.n_jobs()
    assert copied.job_sequence() == new.job_sequence()
    assert copied.n_machines() == new.n_machines()
    assert copied.n_operations() == new.n_operations()

def test_encoder_deep_copy():
    copied = encoder.deep_copy()
    new = Encoding(durations, job_sequence)
    assert copied.n_jobs() == new.n_jobs()
    assert copied.job_sequence() == new.job_sequence()
    assert copied.n_machines() == new.n_machines()
    assert copied.n_operations() == new.n_operations()

def test_worker_encoder_n_jobs():
    assert worker_encoder.n_jobs() == 4

def test_worker_encoder_job_sequence():
    assert worker_encoder.job_sequence() == job_sequence
    
def test_worker_encoder_n_operations():
    assert worker_encoder.n_operations() == worker_durations.shape[0]

def test_worker_encoder_n_machines():
    assert worker_encoder.n_machines() == worker_durations.shape[1]

def test_worker_encoder_get_workers_for_operation():
    assert worker_encoder.get_workers_for_operation(1) == [1,0,2]

def test_worker_encoder_get_all_machines_for_all_operations():
    assert worker_encoder.get_all_machines_for_all_operations() == [[0, 1], [0, 1], [0, 1]]

def test_worker_encoder_get_workers_for_operation_on_machine():
    assert worker_encoder.get_workers_for_operation_on_machine(1, 1) == [0, 2]

def test_worker_encoder_is_possible():
    assert worker_encoder.is_possible(0, 0, 0) == True
    assert worker_encoder.is_possible(0, 0, 1) == False

def test_worker_encoder_copy():
    copied = worker_encoder.copy()
    new = WorkerEncoding(worker_durations, job_sequence)
    assert copied.n_jobs() == new.n_jobs()
    assert copied.job_sequence() == new.job_sequence()
    assert copied.n_machines() == new.n_machines()
    assert copied.n_operations() == new.n_operations()

def test_worker_encoder_deep_copy():
    copied = worker_encoder.deep_copy()
    new = WorkerEncoding(worker_durations, job_sequence)
    assert copied.n_jobs() == new.n_jobs()
    assert copied.job_sequence() == new.job_sequence()
    assert copied.n_machines() == new.n_machines()
    assert copied.n_operations() == new.n_operations()

def test_benchmark_parser(): 
    path = "C:\\Users\\Bianca\\OneDrive - FH Vorarlberg\\JRZ\\JRZ\\Scheduling\\scheduling_model\\code\\external_test_data\\FJSSPinstances\\6_Fattahi\\Fattahi20.fjs"
    parser = BenchmarkParser()
    result = parser.parse_benchmark(path)

    for i in range(0, len(result.durations()[0])):
        for j in range(0, len(result.durations()[1])):
            print(f"{result.durations()[i, j]},")

    print(f"n_jobs: {result.n_jobs()}")
    print(f"n_machines: {result.n_machines()}")
    print(f"n_operations: {result.n_operations()}")

def test_worker_benchmark_parser(): 
    path = "C:\\Users\\Bianca\\OneDrive - FH Vorarlberg\\JRZ\\JRZ\\Scheduling\\scheduling_model\\code\\external_test_data\\FJSSPinstances\\6_Fattahi\\Fattahi20.fjs"
    parser = WorkerBenchmarkParser()
    result = parser.parse_benchmark(path)

    for i in range(0, len(result.durations()[0])):
        for j in range(0, len(result.durations()[1])):
            for k in range(0, len(result.durations()[2])):
                print(f"{result.durations()[i, j, k]},")

    print(f"n_jobs: {result.n_jobs()}")
    print(f"n_machines: {result.n_machines()}")
    print(f"n_operations: {result.n_operations()}")

def main():
    test_encoder_n_jobs()
    test_encoder_job_sequence()
    test_encoder_n_operations()
    test_encoder_n_machines()
    test_encoder_get_machines_for_operation()
    test_encoder_get_machines_for_all_operations()
    test_encoder_copy()
    test_encoder_deep_copy()

    test_worker_encoder_n_jobs()
    test_worker_encoder_job_sequence()
    test_worker_encoder_n_operations()
    test_worker_encoder_n_machines()
    test_worker_encoder_get_workers_for_operation()
    test_worker_encoder_get_all_machines_for_all_operations()
    test_worker_encoder_get_workers_for_operation_on_machine()
    test_worker_encoder_is_possible()
    test_worker_encoder_copy()
    test_worker_encoder_deep_copy()

    test_benchmark_parser()
    #test_worker_benchmark_parser()

if __name__ == "__main__":
    main()