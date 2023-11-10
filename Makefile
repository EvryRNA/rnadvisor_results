export PYTHON?=python -m

install_testset_1:
	src/script/setup_data_modeller.sh
install_testset_2:
	src/script/setup_data.sh
install_testset_3:
	src/script/setup_rna_puzzles.sh
	$(PYTHON) src.utils.rna_puzzles_prepare

install_all_data: install_testset_1 install_testset_2 install_testset_3

clean:
	rm -rf tmp

# Benchmarks
extract_pdb_time:
	$(PYTHON) src.utils.extract_pdb
benchmark_time:
	$(PYTHON) src.time_benchmark.benchmark
benchmark_carbon:
	$(PYTHON) src.carbon.carbon_benchmark
compute_scores:
	src/script/compute_scores.sh

# Visualisations
viz:
	$(PYTHON) src.visualisation.viz_cli
viz_time:
	$(PYTHON) src.time_benchmark.vizualisation
viz_carbon:
	$(PYTHON) src.carbon.carbon_visualize