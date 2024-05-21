from encoding import Encoding, WorkerEncoding
import numpy as np

durations = np.array([[1, 2, 0], [4, 0, 6], [0, 8, 9]])
job_sequence = [1, 1, 2, 2, 3, 3, 3, 4]
encoder = Encoding(durations, job_sequence)

worker_durations = np.array([[[1, 0], [2, 1]], [[4, 3], [0, 0]], [[0, 1], [8, 9]]])
worker_encoder = WorkerEncoding(worker_durations, job_sequence)

def test_encoder_n_jobs():
    assert encoder.n_jobs() == 4

def test_encoder_job_sequence():
    assert encoder.job_sequence() == job_sequence
    
def test_encoder_n_operations():
    assert encoder.n_operations() == len(durations[0])

def test_encoder_n_machines():
    assert encoder.n_machines() == len(durations[1])

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
    assert worker_encoder.n_operations() == len(worker_durations[0])

def test_worker_encoder_n_machines():
    assert worker_encoder.n_machines() == len(worker_durations[1])

def test_worker_encoder_get_workers_for_operation():
    print(worker_encoder.get_workers_for_operation(2))
    assert worker_encoder.get_workers_for_operation(2) == [1,2]

def test_worker_encoder_get_machines_for_all_operations():
    print(worker_encoder.get_machines_for_all_operations())
    assert worker_encoder.get_machines_for_all_operations() == [[0], [0, 1], [0, 1], [1], [0, 1]]

def test_worker_encoder_get_workers_for_operation_on_machine():
    assert worker_encoder.get_workers_for_operation_on_machine(2, 1) == [1,2]

def test_worker_is_possible():
    assert worker_encoder.is_possible(2, 1, 1) == False

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

def main():
    test_encoder_n_jobs()
    test_encoder_job_sequence()
    test_encoder_n_operations()
    test_encoder_n_machines()
    test_encoder_get_machines_for_operation()
    test_encoder_get_machines_for_all_operations()
    test_encoder_copy()
    #test_encoder_deep_copy()

    test_worker_encoder_n_jobs()
    test_worker_encoder_job_sequence()
    test_worker_encoder_n_operations()
    test_worker_encoder_n_machines()
    test_worker_encoder_get_workers_for_operation()
    #test_worker_encoder_get_machines_for_all_operations()
    test_worker_encoder_copy()
    #test_worker_encoder_deep_copy()

if __name__ == "__main__":
    main()