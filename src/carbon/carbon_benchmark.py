import os
from typing import Dict

import pandas as pd
from codecarbon import EmissionsTracker

COMMAND = (
    "docker run --rm -it -v ${PWD}/docker_data/:/app/docker_data -v ${PWD}/tmp:/tmp rnadvisor "
    "--native_path=$path_to_native --pred_path=$path_to_pred "
    "--result_path=$path_to_output --all_scores=$SCORE"
)

ALL_SCORES = [
    "RMSD",
    "P-VALUE",
    "INF",
    "DI",
    "MCQ",
    "TM-SCORE",
    "CAD",
    "BARNABA",
    "CLASH",
    "GDT-TS",
    "lDDT",
    "QS-SCORE",
    "BARNABA",
    "DFIRE",
    "rsRNASP",
    "RASP",
]


class CarbonBenchmark:
    """
    Benchmark class for CodeCarbon for the different datasets.
    """

    def __init__(self, input_paths: Dict, out_path: str):
        self.input_paths = input_paths
        self.out_path = out_path

    def run(self):
        os.makedirs(self.out_path, exist_ok=True)
        out_path = "tmp"
        os.makedirs(out_path, exist_ok=True)
        for dataset, dataset_prefix in self.input_paths.items():
            carbon_emissions = self.get_carbon_emissions_all_dataset(dataset_prefix, out_path)
            save_path = os.path.join(self.out_path, f"{dataset}.csv")
            carbon_emissions.to_csv(save_path, index=False)
            self.clean()

    def clean(self):
        """
        Remove the code carbon outputs
        """
        command = "rm *.csv"
        os.system(command)


    def get_carbon_emissions_all_dataset(self, dataset_prefix: str, out_path: str):
        """
        Return carbon emissions for each metric for each dataset.
        """
        carbon_emissions = None
        rna_lists = os.listdir(os.path.join(dataset_prefix, "NATIVE"))
        for rna_native in rna_lists:
            native_path = os.path.join(dataset_prefix, "NATIVE", rna_native)
            rna = rna_native.replace(".pdb", "")
            # Take only two predictions
            pred_lists = os.listdir(os.path.join(dataset_prefix, "PREDS", rna))[:2]
            c_emission_tmp = None
            for pred in pred_lists:
                pred_path = os.path.join(dataset_prefix, "PREDS", rna, pred)
                carbon_emission = self.get_carbon_emissions(native_path, pred_path, out_path)
                if c_emission_tmp is not None:
                    c_emission_tmp = pd.concat([c_emission_tmp, carbon_emission])
                else:
                    c_emission_tmp = carbon_emission
            current_emission = c_emission_tmp.mean().to_frame().T  # type: ignore
            current_emission["NAME"] = rna_native.replace(".pdb", "")
            carbon_emissions = (
                pd.concat([carbon_emissions, current_emission])
                if carbon_emissions is not None
                else current_emission
            )
        return carbon_emissions

    def get_carbon_emissions(self, native_path: str, pred_path: str, out_path: str):
        output = {}
        tracker = EmissionsTracker(log_level="critical", measure_power_secs=0.1)
        for metric in ALL_SCORES:
            tracker.start_task("test")
            try:
                self.run_docker(native_path, pred_path, out_path, metric)
            finally:
                tracker.stop_task("test")
            output[metric] = tracker._tasks["test"].emissions_data.emissions
        tracker.stop()
        return pd.DataFrame(output, index=[0])

    def run_docker(self, native_path: str, pred_path: str, out_path: str, metric: str):
        command = (
            COMMAND.replace("$path_to_native", native_path)
            .replace("$path_to_pred", pred_path)
            .replace("$path_to_output", out_path)
            .replace("$SCORE", metric)
        )
        os.system(command)


if __name__ == "__main__":
    input_paths = {
        "TestSetI": os.path.join("docker_data", "input", "TestSetI"),
        "TestSetII": os.path.join("docker_data", "input", "TestSetII"),
        "TestSetIII": os.path.join("docker_data", "input", "TestSetIII"),
    }
    out_path = os.path.join("docker_data", "output", "carbon")
    carbon_benchmark = CarbonBenchmark(input_paths, out_path)
    carbon_benchmark.run()
