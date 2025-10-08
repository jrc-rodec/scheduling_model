from subprocess import Popen
import os
import time

#b_path = r"C:\Users\huda\Documents\GitHub\scheduling_model_jrc\code\upgrades\benchmarks_with_workers"
#files = os.listdir(b_path)
#for file in files:
#    if file.endswith('.json'):
#        print(b_path + "\\" + file)
#        os.remove(b_path + "\\" + file)
shutdown_when_finished = True
modes = ['FJSSP-W', 'FJSSP']
experiments = ['feval 500000', 'feval 1000000', 'feval 2000000', 'feval 5000000', 'feval 10000000']
processes = []
sub_process_path = r'C:\Users\dhutt\source\repos\ImageProcessing\scheduling_model_jrc\code\upgrades\CS_Translation\Solver\bin\Release\net8.0\Solver.exe'
for mode in modes:
    for j in range(len(experiments)):
        for _ in range(5):
            for i in range(6):
                    processes.append(Popen(sub_process_path + f' {i+1} {experiments[j]} {mode}'))
                    time.sleep(1)
            for i in range(len(processes)):
                processes[i].wait()
"""for j in range(2):
    for i in range(6):
        if j == 0:
            processes.append(Popen(sub_process_path + f' {i+1} NO_ADJUSTMENT'))
        else:
            processes.append(Popen(sub_process_path + f' {i+1} ADJUSTMENT'))
        time.sleep(1)
    for i in range(len(processes)):
        processes[i].wait()"""
if shutdown_when_finished:
    os.system("shutdown /s /t 1")
