import os.path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px

DICT_TO_CHANGE = {
    "BARNABA-eRMSD": "εRMSD",
    "BARNABA-eSCORE": "εSCORE",
    "RASP-ENERGY": "RASP",
    "tm-score-ost": "TM-score",
    "lddt": "lDDT",
    "RNA3DCNN_MDMC": "RNA3DCNN",
    "RNA3DCNN_MD": "RNA3DCNN",
    "INF-ALL": r"$INF_{all}$",
    "CAD": "CAD-score",
}


class VizAllHelper:
    def __init__(self, csv_paths: List[str]):
        self.csv_paths = csv_paths
        self.all_dfs = {
            eval_type: self.read_csv_files(
                csv_paths,
                eval_type=eval_type,
            )
            for eval_type in ["PCC", "ES"]
        }

    def read_csv_files_scoring_fn(self, csv_paths: List[str]):
        all_dfs = {
            eval_type: self._read_csv_files_scoring_fn(csv_paths, eval_type=eval_type)
            for eval_type in ["PCC", "ES"]
        }
        return all_dfs

    def _read_csv_files_scoring_fn(self, csv_paths: List[str], eval_type: str = "PCC"):
        all_dfs = {}
        for csv_path in csv_paths:
            name = os.path.join(csv_path, f"{eval_type}.csv")
            all_dfs[csv_path] = pd.read_csv(name, index_col=[0]).rename(columns=DICT_TO_CHANGE)
        return all_dfs

    def read_csv_files(self, csv_paths: List[str], eval_type: str = "PCC"):
        """Read a csv file"""
        all_dfs = {}
        for csv_path in csv_paths:
            basename = os.path.basename(csv_path)
            name = os.path.join(
                csv_path.replace(basename, f"metrics_{basename}"), f"{eval_type}.csv"
            )
            all_dfs[csv_path] = pd.read_csv(name, index_col=[0]).rename(columns=DICT_TO_CHANGE)
        return all_dfs

    def plot_heat_map(
        self,
        eval_type: str,
        save_path: Optional[str] = None,
        to_show: bool = False,
        colorscale="inferno",
        dataset: Optional[str] = None,
    ):
        if dataset is not None:
            mean_scores = self.all_dfs[eval_type][dataset].values
        else:
            mean_scores = np.mean([df.values for df in self.all_dfs[eval_type].values()], axis=0)
        mean_scores = np.round(mean_scores, 2)
        df_example = self.all_dfs[eval_type][list(self.all_dfs[eval_type].keys())[0]]
        index, columns = df_example.index, df_example.columns
        df_mean = pd.DataFrame(mean_scores, index=index, columns=columns)
        df_mean = df_mean.abs().rename(
            columns={"BARNABA-eRMSD": "eRMSD"}, index={"BARNABA-eRMSD": "eRMSD"}
        )
        fig = px.imshow(df_mean, text_auto=True, aspect="auto", color_continuous_scale=colorscale)
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=14,  # Set the font size here
            )
        )
        if save_path is not None:
            path_to_save = save_path.replace(".png", f"_{eval_type}.png")
            path_to_save = (
                path_to_save.replace(".png", f"_{os.path.basename(dataset)}.png")
                if dataset is not None
                else path_to_save
            )
            fig.write_image(path_to_save, scale=2)
        if to_show:
            fig.show()

    def plot_heat_map_individual(self, save_path: Optional[str] = None):
        for eval_type in ["PCC", "ES"]:
            for dataset in self.all_dfs[eval_type].keys():
                self.plot_heat_map(
                    eval_type,
                    save_path,
                    dataset=dataset,
                    colorscale="viridis" if eval_type == "ES" else "inferno",
                )

    def get_count_link_scores_metrics(self, eval_type):
        all_dfs = self.read_csv_files_scoring_fn(self.csv_paths)
        # related_metrics = {}
        # for eval_type in ["PCC", "ES"]:
        score_to_metrics = {}
        for csv_path, df in all_dfs[eval_type].items():
            for score_name, metrics in df.T.to_dict().items():
                best_metrics = self.get_max_metrics(metrics)
                for b_metric in best_metrics:
                    if score_name not in score_to_metrics:
                        score_to_metrics[score_name] = {}
                    score_to_metrics[score_name][b_metric] = (
                        score_to_metrics[score_name].get(b_metric, 0) + 1
                    )
            # related_metrics[eval_type] = score_to_metrics
        metric_names = []
        for metrics in score_to_metrics.values():
            metric_names.extend(list(metrics.keys()))
        metric_names = list(set(metric_names))
        matrix = np.zeros((len(score_to_metrics), len(metric_names)))
        for i_score, (score, metrics) in enumerate(score_to_metrics.items()):
            for metric, value in metrics.items():
                i_metric = metric_names.index(metric)
                matrix[i_score, i_metric] = value
        output = pd.DataFrame(matrix, index=score_to_metrics.keys(), columns=metric_names)
        return output

    def plot_best_relation_eval(
        self, eval_type: str, save_path: Optional[str] = None, colorscale="inferno"
    ):
        related_metrics = self.get_count_link_scores_metrics(eval_type)
        fig = px.imshow(
            related_metrics, text_auto=True, aspect="auto", color_continuous_scale=colorscale
        )
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=14,  # Set the font size here
            )
        )
        fig.update_layout(xaxis_title="Metrics", yaxis_title="Scoring functions")

        if save_path is not None:
            path_to_save = save_path.replace(".png", f"_{eval_type}.png")
            fig.write_image(path_to_save, scale=2)

    def get_max_metrics(self, metrics_scores: Dict):
        scores = list(metrics_scores.values())
        indexes_max = np.where(scores == np.max(scores))[0]
        return [list(metrics_scores.keys())[i] for i in indexes_max]
