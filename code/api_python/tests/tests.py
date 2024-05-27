from benchmarkrewriter import rewrite_benchmarks
from benchmarkrewriter.encoding import WorkerEncoding, Encoding
from benchmarkrewriter.benchmark_parser import BenchmarkParser, WorkerBenchmarkParser
import numpy as np

sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata', '2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']

read_path = "C:\\Users\\Bianca\\OneDrive - FH Vorarlberg\\JRZ\\JRZ\\Scheduling\\scheduling_model\\code\\api_python\\benchmarkrewriter\\FJSSPinstances\\"
write_path = "C:\\Users\\Bianca\\OneDrive - FH Vorarlberg\\JRZ\\JRZ\\Scheduling\\scheduling_model\\code\\api_python\\tests\\output\\"

def test_get_available_sources():
    assert rewrite_benchmarks.get_available_sources() == sources

def test_rewrite_benchmark():
    rewrite_benchmarks.rewrite_benchmark(sources[0], 1, path=read_path, lower_bound=0.9, upper_bound=1.1, worker_amount=3)
    rewrite_benchmarks.rewrite_benchmark(sources[0], 1, path=read_path)

def test_rewrite_all_from_source():
    rewrite_benchmarks.rewrite_all_from_source(sources[0], read_path, write_path, lower_bound=0.9, upper_bound=1.1, worker_amount=3)
    rewrite_benchmarks.rewrite_all_from_source(sources[0], read_path, write_path)

def test_rewrite_all_with_workers():
    rewrite_benchmarks.rewrite_all_with_workers(read_path, write_path)

def test_rewrite_all_from_source_with_workers():
    rewrite_benchmarks.rewrite_all_from_source_with_workers(sources[0], read_path, write_path)
    
def test_rewrite_benchmark_with_workers():
    rewrite_benchmarks.rewrite_benchmark_with_workers(sources[0], 1, read_path, write_path)

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

    for i in range(0, result.durations().shape[0]):
        for j in range(0, result.durations().shape[1]):
            print(f"{result.durations()[i, j]},")

    print(f"n_jobs: {result.n_jobs()}")
    print(f"n_machines: {result.n_machines()}")
    print(f"n_operations: {result.n_operations()}")

"""def test_worker_benchmark_parser(): 
    path = "C:\\Users\\Bianca\\OneDrive - FH Vorarlberg\\JRZ\\JRZ\\Scheduling\\scheduling_model\\code\\external_test_data\\FJSSPinstances\\6_Fattahi\\Fattahi20.fjs"
    parser = WorkerBenchmarkParser()
    result = parser.parse_benchmark(path)

    for i in range(0, result.durations().shape[0]):
        for j in range(0, result.durations().shape[1]):
            for k in range(0, result.durations().shape[2]):
                print(f"{result.durations()[i, j, k]},")

    print(f"n_jobs: {result.n_jobs()}")
    print(f"n_machines: {result.n_machines()}")
    print(f"n_operations: {result.n_operations()}")"""

