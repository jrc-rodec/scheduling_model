from data_translator import BenchmarkTranslator, TimeWindowGAEncoder

benchmark_translator = BenchmarkTranslator()
production_environment = benchmark_translator.translate(7)
encoder = TimeWindowGAEncoder()
orders = []
values, jobs = encoder.encode(production_environment, orders)
print(values)