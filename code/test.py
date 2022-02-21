from external_test_data.read_data import read_dataset_1

input, orders, instance = read_dataset_1(use_instance=13)
print(orders)
system_info = instance[0]
jobs = instance[1]
n_jobs = system_info[0]
n_machines = system_info[1]
n_workers = system_info[2]
# ready to start optimization
