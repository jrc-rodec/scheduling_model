from flask import Flask, request
import os
import sys
from models import RewriteBenchmarkRequest

# Install: flask, requests

sys.path.append(os.path.dirname(os.getcwd() + "\\reworked_data_model"))

from reworked_data_model import rewrite_benchmarks

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello"

"""
    EXAMPLE USAGES:
"""
"""source = 1

# rewrite all benchmarks (with the same parameters)
for i in range(len(sources)):
    source = i
    rewrite_all_from_source(sources[source], 0.9, 1.1, 3, read_path, write_path)"""

@app.route('/sources', methods=["GET"])
def availableSources():
    sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata', '2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']
    return sources

# Example Usages
"""
data = {"source":"0_BehnkeGeiger", "id":1, "lower_bound":0.8, "upper_bound":1.2, "worker_amount":4, "read_path":read_path_default} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmark", json=data)

data = {"source":"0_BehnkeGeiger", "id":1} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmark", json=data)
"""

@app.route('/rewriteBenchmark',  methods=["POST"])
def rewrite_benchmark():
    request_json = request.get_json()

    data = RewriteBenchmarkRequest(request_json.get("source"), request_json.get("id", None), 
                                   request_json.get("lower_bound", None), request_json.get("upper_bound", None),
                                   request_json.get("worker_amount", None), request_json.get("read_path", None))

    result = rewrite_benchmarks.rewrite_benchmark(data.source, data.id, 
                                                  data.lower_bound, data.upper_bound, 
                                                  data.worker_amount, data.read_path)

    return result


# Example Usage
"""
data = {"source":"0_BehnkeGeiger", "lower_bound":0.8, "upper_bound":1.2, "worker_amount":4, "read_path":read_path_default, "write_path":write_path_default} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmarksOfSource", json=data)

data = {"source":"0_BehnkeGeiger"} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmarksOfSource", json=data)
"""
@app.route('/rewriteBenchmarksOfSource',  methods=["POST"])
def rewrite_benchmarks_of_source():
    request_json = request.get_json()

    data = RewriteBenchmarkRequest(request_json.get("source"), None, request_json.get("lower_bound", None), 
                                   request_json.get("upper_bound", None), request_json.get("worker_amount", None), 
                                   request_json.get("read_path", None), request_json.get("write_path", None))


    rewrite_benchmarks.rewrite_all_from_source(data.source, data.lower_bound, 
                                               data.upper_bound, data.worker_amount, 
                                               data.read_path, data.write_path)

    return ('', 204)

if __name__ == '__main__':
    app.run()