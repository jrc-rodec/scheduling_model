from subprocess import Popen
import os
import time

def run(command):
    p = Popen(f'{command}')
    p.wait()
if __name__ == '__main__':
    shutdown_when_finished = False
    # CPLEX-CP
    #for i in range(30):
    #    print(f'RUN # {i}')
    #    run('py C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py cplex_cp')
    #    run('py C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py cplex_cp')
    # OR-Tools
    #for i in range(30):
    #    print(f'RUN # {i}')
    #    run('py C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py ortools')
    #    run('py C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py ortools')

    # GA
    #processes = []
    #sub_process_path = r'C:\Users\localadmin\Documents\GitHub\scheduling_model_jrc\code\upgrades\CS_Translation\Solver\bin\Release\net8.0\Solver.exe'
    #processes = []
    #for i in range(6):
    #    processes.append(Popen(sub_process_path + f' {i+1} FJSSP-W'))
    #    time.sleep(1)
    #for i in range(len(processes)):
    #    processes[i].wait()
    #for i in range(6):
    #    processes.append(Popen(sub_process_path + f' {i+1} FJSSP'))
    #    time.sleep(1)
    #for i in range(len(processes)):
    #    processes[i].wait()

    # Gurobi
    #run('py -3.10 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py gurobi')
    #run('py -3.10 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py gurobi')

    # CPLEX-LP
    #run('py -3.10 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py cplex_lp')
    #run('py -3.10 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py cplex_lp')

    # Hexaly
    #run('py -3.12 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments_workers.py hexaly')
    #run('py -3.12 C:\\Users\\localadmin\\Documents\\GitHub\\scheduling_model_jrc\\code\\upgrades\\code\\test_experiments.py hexaly')

    # OPTAL-CP 
    path = r'C:\Users\localadmin\Downloads\benchmarks_no_workers\missing'
    outpath = r'C:\Users\localadmin\Desktop\experiments\OPTAL_FJSSP_W\experiment'
    fjssp_w_instances = os.listdir(path)
    for instance in fjssp_w_instances:
        #run(f'node C:\\Users\\localadmin\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop\\flexible-jobshop-w.mjs --worker0-1.noOverlapPropagationLevel 4 --worker0-1.searchType fds --timeLimit 1200 {path}\\{instance} --fjssp-w-json {outpath}\\{instance}.json')
        #run(f'node C:\\Users\\localadmin\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop\\flexible-jobshop.mjs --timeLimit 1200 {path}\\{instance} --fjssp-w-json {outpath}\\{instance}.json')
        run(f'node c:\\Users\localadmin\\Downloads\\optalcp-benchmarks-main\\optalcp-benchmarks-main\\benchmarks\\flexible-jobshop-w\\flexible-jobshop-w.mjs --timeLimit 1200 {path}\\{instance} --fjssp-w-json {outpath}\\{instance}.json')


    if shutdown_when_finished:
        os.system("shutdown /s /t 1")