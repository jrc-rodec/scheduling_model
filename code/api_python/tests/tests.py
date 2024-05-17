from benchmarkrewriter import rewrite_benchmarks
import benchmarkrewriter.FJSSPinstances as FJSSPInstances

sources = ['0_BehnkeGeiger', '1_Brandimarte', '2a_Hurink_sdata', '2b_Hurink_edata', '2c_Hurink_rdata', '2d_Hurink_vdata', '3_DPpaulli', '4_ChambersBarnes', '5_Kacem', '6_Fattahi']

def test_get_available_sources():
    assert rewrite_benchmarks.get_available_sources() == sources

def test_rewrite_benchmark_with_workers():
    rewrite_benchmarks.rewrite_benchmark(
        sources[0], 1, lower_bound=0.9, upper_bound=1.1, worker_amount=3, path="C:\\Users\\Bianca\\OneDrive - FH Vorarlberg\\JRZ\\JRZ\\Scheduling\\scheduling_model\\code\\api_python\\benchmarkrewriter\\FJSSPinstances")