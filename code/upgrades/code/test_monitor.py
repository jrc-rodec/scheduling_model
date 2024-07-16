import psutil
import time
#NOTE: interval is in seconds
def monitor_resources(cpu, ram, interval = 5, run = 1):
    while run == 1:
        current_cpu = psutil.cpu_percent()
        current_ram = psutil.virtual_memory().percent
        if cpu.value < current_cpu:
            cpu.value = current_cpu
        if ram.value < current_ram:
            ram.value = current_ram
        # sleep
        time.sleep(interval)