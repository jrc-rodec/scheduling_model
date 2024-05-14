import requests
import os
import inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
read_path_default = os.path.abspath(currentdir + '/../external_test_data/FJSSPinstances/')
write_path_default = os.path.abspath(currentdir + '/../reworked_data_model/changed_benchmarks/')

# Example usage for retrieving all available /sources: 
r = requests.get("http://127.0.0.1:5000/sources")
print(r.status_code)

# Example usage for rewriting single benchmark /rewriteBenchmark
data = {"source":"0_BehnkeGeiger", "id":1, "lower_bound":0.8, "upper_bound":1.2, "worker_amount":4, "read_path":read_path_default} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmark", json=data)
print(r.status_code)

data = {"source":"0_BehnkeGeiger", "id":1} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmark", json=data)
print(r.status_code)

# Example usage for rewriting all benchmarks of a source /rewriteBenchmarksOfSource
data = {"source":"0_BehnkeGeiger", "lower_bound":0.8, "upper_bound":1.2, "worker_amount":4, "read_path":read_path_default, "write_path":write_path_default} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmarksOfSource", json=data)
print(r.status_code)

data = {"source":"0_BehnkeGeiger"} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmarksOfSource", json=data)
print(r.status_code)