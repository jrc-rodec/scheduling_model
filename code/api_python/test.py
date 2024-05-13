import requests

data = {"source":"0_BehnkeGeiger", "id":1, "lower_bound":0.9, "upper_bound":1.1, "worker_amount":3} 
r = requests.post("http://127.0.0.1:5000/rewriteBenchmark", json=data)
print(r.status_code)

#r = requests.post("http://127.0.0.1:5000/example", json={"test":"Hallo"})