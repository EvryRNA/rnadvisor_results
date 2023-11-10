import os

from src.visualisation.viz_all_helper import VizAllHelper
from src.visualisation.viz_helper import VizHelper

LIST_MAIN_METRICS = [
    "RMSD",
    r"$INF_{all}$",
    "DI",
    "MCQ",
    "TM-score",
    "GDT-TS",
    "CAD-score",
    "εRMSD",
    "lDDT",
]


class VizCLI:
    def test_set_i(self):
        csv_folder = os.path.join("docker_data", "output", "TestSetI")
        viz_helper = VizHelper(csv_folder)
        viz_helper.plot_correlation_all_energies(
            LIST_MAIN_METRICS,
            ["1ec6D"],
            to_show=False,
            save_path=os.path.join("docker_data", "plots", "1ec6D_metrics_energies.png"),
        )
        viz_helper.compute_er_score(list_metrics=LIST_MAIN_METRICS, add_mean=True)
        viz_helper.compute_er_score_metrics()

    def test_set_ii(self):
        csv_folder = os.path.join("docker_data", "output", "TestSetII")
        viz_helper = VizHelper(csv_folder)
        viz_helper.compute_er_score(list_metrics=LIST_MAIN_METRICS, add_mean=True)
        viz_helper.compute_er_score_metrics()

    def test_set_iii(self):
        csv_folder = os.path.join("docker_data", "output", "TestSetIII")
        viz_helper = VizHelper(csv_folder)
        viz_helper.compute_er_score(list_metrics=LIST_MAIN_METRICS, add_mean=True)
        viz_helper.compute_er_score_metrics()

    def test_set_all(self):
        in_dir = os.path.join("docker_data", "scores")
        csv_folders = [
            os.path.join(in_dir, dataset)
            for dataset in ["TestSetI", "TestSetII", "TestSetIII"]
        ]
        viz_all_helper = VizAllHelper(csv_folders)
        save_path = os.path.join("docker_data", "plots", "heatmap", "all_heatmap.png")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        viz_all_helper.plot_heat_map(eval_type="PCC", save_path=save_path)
        viz_all_helper.plot_heat_map(eval_type="ES", save_path=save_path, colorscale="viridis")
        save_path = os.path.join("docker_data", "plots", "heatmap", "heatmap.png")
        viz_all_helper.plot_heat_map_individual(save_path)
        save_path = os.path.join("docker_data", "plots", "best_heatmap", "heatmap.png")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        viz_all_helper.plot_best_relation_eval(eval_type="PCC", save_path=save_path)
        viz_all_helper.plot_best_relation_eval(
            eval_type="ES", save_path=save_path, colorscale="viridis"
        )


if __name__ == "__main__":
    viz_cli = VizCLI()
    viz_cli.test_set_i()
    viz_cli.test_set_ii()
    viz_cli.test_set_iii()
    viz_cli.test_set_all()
