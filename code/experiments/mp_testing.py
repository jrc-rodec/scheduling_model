import multiprocessing as mp

def test_with_queue(lb, ub, queue):
    result = 0
    for i in range(lb, ub):
        result += i
    queue.put([result])

def test_with_pipe(lb, ub, pipe):
    result = 0
    for i in range(lb, ub):
        result += i
    pipe.send(result)

def run_tests():
    context = mp.get_context('spawn')
    queue = context.Queue()
    parent_pipe, child_pipe = context.Pipe()

    n_processes = 5

    processes = []
    results = []
    # test queues
    for _ in range(n_processes):
        p = context.Process(target=test_with_queue, args=(0, 10, queue))
        processes.append(p)
        p.start()

    for i in range(n_processes):
        results.append(queue.get())

    for result in results:
        print(result)

    for process in processes:
        process.join()

    queue.close()
    # test pipes
    processes.clear()
    results.clear()
    
    for _ in range(n_processes):
        p = context.Process(target=test_with_pipe, args=(0, 10, child_pipe))
        processes.append(p)
        p.start()
    for _ in range(n_processes):
        results.append(parent_pipe.recv())
    for result in results:
        print(result)
    for process in processes:
        process.join()
    child_pipe.close()
    parent_pipe.close()
    

if __name__ == '__main__':
    run_tests()