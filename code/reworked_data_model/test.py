from translation import BenchmarkTranslator, TimeWindowGAEncoder

benchmark_translator = BenchmarkTranslator()
production_environment = benchmark_translator.translate(7)
encoder = TimeWindowGAEncoder()
orders = [] # TODO: create orders for testing
values, jobs = encoder.encode(production_environment, orders)
print(values)
