from data_translator import BenchmarkTranslator

benchmark_translator = BenchmarkTranslator()
production_environment = benchmark_translator.translate(7)
print('just as breakpoint')