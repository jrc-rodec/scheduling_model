import subprocess
import os
#subprocess.call('py .\test_experiments.py hexaly', shell=True)
subprocess.call('py -3.10 .\test_experiments.py cplex_lp', shell=True)
os.system("shutdown /s /t 1")