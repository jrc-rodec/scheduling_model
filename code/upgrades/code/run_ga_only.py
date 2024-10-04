from subprocess import Popen
import os
shutdown_when_finished = True
processes = []
sub_process_path = r'C:\Users\huda\Documents\GitHub\scheduling_model_jrc\code\upgrades\CS_Translation\Solver\bin\Release\net8.0\Solver.exe'
for i in range(5):
    processes.append(Popen(sub_process_path))
for i in range(len(processes)):
    processes[i].wait()
if shutdown_when_finished:
    os.system("shutdown /s /t 1")