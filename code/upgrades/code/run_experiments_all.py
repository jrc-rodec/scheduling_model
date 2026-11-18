from subprocess import Popen
import os
import time

def run(command):
    p = Popen(f'{command}')
    p.wait()
if __name__ == '__main__':
    shutdown_when_finished = True
    # CPLEX-CP
    for i in range(1):
        print(f'RUN # {i}')
        run('py C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py cplex_cp')
    #    run('py C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py cplex_cp')
    # OR-Tools
    #for i in range(1):
    #    print(f'RUN # {i}')
    #    run('py C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py ortools')
    #    run('py C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py ortools')
    #os.system('PAUSE')
    # OPTAL-CP 
    #path = r'C:\Users\huda\Documents\GitHub\FJSSP-W-Benchmarking\instances\Example_Instances_FJSSP-WF'
    #outpath = r'C:\Users\huda\Desktop\COMPARISON_RESULTS\optal'
    #fjssp_w_instances = os.listdir(path)
    #for instance in fjssp_w_instances:
        #run(f'node C:\\Users\\localadmin\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop\\flexible-jobshop-w.mjs --worker0-1.noOverlapPropagationLevel 4 --worker0-1.searchType fds --timeLimit 1200 {path}\\{instance} --fjssp-w-json {outpath}\\{instance}.json')
        #run(f'node C:\\Users\\localadmin\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop\\flexible-jobshop.mjs --timeLimit 1200 {path}\\{instance} --fjssp-w-json {outpath}\\{instance}.json')
        #with open(f'{outpath}\\{instance}.json', 'w') as f:
        #    pass
        #run(f'node C:\\Users\huda\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop-w\\flexible-jobshop-w.mjs --timeLimit 600 {path}\\{instance} {outpath}\\{instance}.json') # --fjssp-w-json
    #    run(f'node C:\\Users\huda\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop-w\\flexible-jobshop-w.mjs --worker0-1.noOverlapPropagationLevel 4 --worker0-1.searchType fds --timeLimit 600 {path}\\{instance}')# --fjssp-w-json {outpath}\\{instance}.json') #
    # Gurobi
    run('py -3.10 C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py gurobi')
    #run('py -3.10 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py gurobi')

    # CPLEX-LP
    run('py -3.10 C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py cplex_lp')
    #run('py -3.10 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py cplex_lp')

    # Hexaly
    #run('py C:\\Users\\huda\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py hexaly')
    # GA
    #processes = []
    #sub_process_path = r'C:\Users\huda\Documents\GitHub\scheduling_model_jrc\code\upgrades\CS_Translation\Solver\bin\Debug\net8.0\Solver.exe'
    #processes = []
    #for i in range(1):
    #    processes.append(Popen(sub_process_path + f' {i+1} FJSSP-W'))
    #    time.sleep(1)
    #for i in range(len(processes)):
    #    processes[i].wait()
    #for i in range(6):
    #    processes.append(Popen(sub_process_path + f' {i+1} FJSSP'))
    #    time.sleep(1)
    #for i in range(len(processes)):
    #    processes[i].wait()

    #run('py -3.12 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py hexaly')



    if shutdown_when_finished:
        os.system("shutdown /s /t 1")