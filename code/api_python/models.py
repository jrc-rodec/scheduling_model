import os
import inspect 

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
read_path_default = currentdir + '/../external_test_data/FJSSPinstances/'
write_path_default = currentdir + '/../reworked_data_model/changed_benchmarks/'

class RewriteBenchmarkRequest:
  def __init__(self, source, id=None, lower_bound=None, upper_bound=None, worker_amount=None, read_path=None, write_path=None):
    self.source = source
    self.id = -1 if id is None else id
    self.lower_bound = 0.9 if lower_bound is None else lower_bound
    self.upper_bound = 1.1 if upper_bound is None else upper_bound
    self.worker_amount = 3 if worker_amount is None else worker_amount
    self.read_path = read_path_default if read_path is None else read_path
    self.write_path = write_path_default if write_path is None else write_path