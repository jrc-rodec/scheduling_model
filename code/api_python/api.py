from flask import Flask, request
import os
import sys

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

# rewrite a specific benchmark
id = 5
result = rewrite_benchmark(source=sources[source], id=id, lower_bound=0.9, upper_bound=1.1, worker_amount=3, path=read_path)
write_file(benchmark=result,path=write_path, file_name=f'{sources[source]}_{id}_updated.fjs')

# rewrite all benchmarks from a specific source
rewrite_all_from_source(sources[source], 0.9, 1.1, 3, read_path, write_path)

# rewrite all benchmarks (with the same parameters)
for i in range(len(sources)):
    source = i
    rewrite_all_from_source(sources[source], 0.9, 1.1, 3, read_path, write_path)"""

@app.route('/sources', methods=["GET"])
def availableBenchmarks():
    sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata', '2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']
    return sources

@app.route('/example', methods=["POST"])
def example():
    return request.get_json()

@app.route('/rewriteBenchmark',  methods=["POST"])
def rewrite_benchmark():
    request_data = request.get_json()

    read_path = os.path.dirname(os.getcwd() + "\\external_test_data\\FJSSPinstances\\")

    result = rewrite_benchmarks.rewrite_benchmark(
        source=request_data["source"], 
        id=request_data["id"], 
        lower_bound=request_data["lower_bound"], 
        upper_bound=request_data["upper_bound"], 
        worker_amount=request_data["worker_amount"], 
        path=read_path)

    print(result)

    return result

if __name__ == '__main__':
    app.run()