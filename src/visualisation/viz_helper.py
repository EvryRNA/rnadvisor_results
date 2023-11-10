import os
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
from sklearn import preprocessing as pre

from src.utils.evaluation_helper import EvaluationHelper

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
LIST_ALL_METRICS = [
    "RMSD",
    "P-VALUE",
    r"$INF_{all}$",
    "INF-WC",
    "INF-NWC",
    "INF-STACK",
    "DI",
    "MCQ",
    "GDT-TS",
    "GDT-TS@1",
    "GDT-TS@2",
    "GDT-TS@4",
    "GDT-TS@8",
    "CAD-score",
    "εRMSD",
    "TM-score",
    "lDDT",
]

LIST_ENERGIES = ["RASP", "εSCORE", "DFIRE", "rsRNASP"]
NEGATIVE_ENERGY = ["εSCORE"]

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

COLORS_ENERGIES = {
    "RASP": "#6499E9",
    "εSCORE": "#B5CB99",
    "DFIRE": "#EF6262",
    "rsRNASP": "#F3AA60",
}


class VizHelper:
    def __init__(self, csv_folder: str):
        self.csv_folder = csv_folder
        self.csv_paths = [
            os.path.join(self.csv_folder, csv_file) for csv_file in os.listdir(self.csv_folder)
        ]
        self.df = self._init_csv(self.csv_paths)
        self.energy_normalizer = self._init_normalizer(self.df)

    def _init_normalizer(self, df: pd.DataFrame):
        normalizers = {}
        for energy in LIST_ENERGIES:
            new_energy = pre.MinMaxScaler().fit(df[energy].dropna().values.reshape(-1, 1))
            normalizers[energy] = new_energy
        return normalizers

    def _init_csv(self, csv_path: List[str], remove_native: bool = True):
        """Merge the different csv files into one dataframe"""
        df = self.read_csv(csv_path[0], remove_native)
        for csv in csv_path[1:]:
            new_df = self.read_csv(csv, remove_native)
            df = pd.concat([df, new_df], axis=0)
        df = df.rename(columns=DICT_TO_CHANGE)
        return df

    def read_csv(self, csv_path: str, remove_native: bool = True):
        """Read a csv file"""
        df = pd.read_csv(csv_path, index_col=[0])
        if remove_native:
            df = self.remove_native_from_df(df, csv_path)
        return df

    def remove_native_from_df(self, df: pd.DataFrame, name: str) -> pd.DataFrame:
        """
        Remove the native molecules from the dataframe
        :param df:
        :param name: name of the csv file
        """
        native_name = f"normalized_{os.path.basename(name).replace('.csv', '')}.pdb"
        return df[df.index != native_name]

    def _convert_df_to_plot(
        self, energies: List, metrics: List, rna_name: List[str], normalize: bool = True
    ) -> pd.DataFrame:
        """
        Convert the df to plot the energy and the metrics
        """
        if len(rna_name) > 0:
            df = self._init_csv(
                [os.path.join(self.csv_folder, f"{csv_file}.csv") for csv_file in rna_name],
                remove_native=True,
            )
        else:
            df = self.df.copy()
        df = df[energies + metrics]
        new_df: Dict = {"Metric": [], "metric": [], "energy": [], "Energy": [], "RNA": []}
        for metric in metrics:
            for energy in energies:
                new_df["RNA"].extend(df.index.tolist())
                new_df["Energy"].extend(len(df) * [energy])
                new_df["Metric"].extend(len(df) * [metric])
                new_df["metric"].extend(df[metric].values)
                if normalize:
                    energy_normalized = (
                        self.energy_normalizer[energy]
                        .transform(df[energy].values.reshape(-1, 1))
                        .reshape(-1)
                    )
                else:
                    energy_normalized = df[energy].values
                if energy in NEGATIVE_ENERGY:
                    energy_normalized = 1 * normalize - energy_normalized
                energy_normalized = np.log(1e-10 + abs(energy_normalized))
                new_df["energy"].extend(energy_normalized)
        new_df = pd.DataFrame(new_df)
        return new_df

    def filter_df(self, df: pd.DataFrame):
        """
        Remove NaN and infinite values from the df
        """
        new_df = df[(df["metric"] < 1e300) & (df["energy"] < 1e300) & (df["metric"] != 0)]
        return new_df

    def plot_correlation_energy_metrics(
        self, energy: str, metrics: List, rna_name: List[str] = []
    ):
        df = self._convert_df_to_plot([energy], metrics, rna_name)
        df = self.filter_df(df)
        fig = px.scatter(
            df,
            x="metric",
            y="energy",
            facet_col="Metric",
            facet_col_wrap=3,
            hover_data=["RNA"],
        )
        color = "#d6d6d6"
        fig.update_xaxes(matches=None, showticklabels=True)
        params_axes = dict(
            showgrid=True,
            gridcolor=color,
            linecolor="gray",
            zeroline=False,
            linewidth=1,
            showline=True,
            mirror=True,
            gridwidth=1,
            griddash="dot",
        )
        fig.update_layout(dict(plot_bgcolor="white"))
        fig.update_xaxes(**params_axes)
        fig.update_yaxes(**params_axes)
        fig.show()

    def plot_metrics_vs_energies(
        self,
        metrics: List,
        rna_name: List[str] = [],
        save_path: Optional[str] = None,
        to_show: bool = False,
    ):
        df = self._convert_df_to_plot(LIST_ENERGIES, metrics, rna_name, normalize=True)
        df = self.filter_df(df)
        fig = px.scatter(
            df,
            x="metric",
            y="energy",
            facet_col="Energy",
            facet_col_wrap=5,
        )
        fig.show()

    def plot_correlation_all_energies(
        self,
        metrics: List,
        rna_name: List[str] = [],
        save_path: Optional[str] = None,
        to_show: bool = False,
    ):
        df = self._convert_df_to_plot(LIST_ENERGIES, metrics, rna_name, normalize=True)
        df = self.filter_df(df)
        df = df.rename(columns={"Energy": "Scoring function"})
        fig = px.scatter(
            df,
            x="metric",
            y="energy",
            facet_col="Metric",
            facet_col_wrap=4,
            color="Scoring function",
            color_discrete_map=COLORS_ENERGIES,
        )
        fig.update_xaxes(matches=None, showticklabels=True)
        params_axes = dict(
            showgrid=True,
            gridcolor="#d6d6d6",
            linecolor="black",
            zeroline=False,
            linewidth=1,
            showline=True,
            mirror=True,
            gridwidth=1,
            griddash="dot",
            title=None,
        )
        fig.update_xaxes(**params_axes)
        fig.update_yaxes(**params_axes)
        fig.update_layout(dict(plot_bgcolor="white"), margin=dict(l=0, r=5, b=0, t=20))
        param_marker = dict(opacity=1, line=dict(width=0.5, color="DarkSlateGrey"), size=6)
        fig.update_traces(marker=param_marker, selector=dict(mode="markers"))
        for annotation in fig["layout"]["annotations"]:
            annotation["text"] = annotation["text"].replace("Metric=", "")
        name_y_axis = "Normalised scoring function"
        fig["layout"]["yaxis4"]["title"] = name_y_axis
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=14,  # Set the font size here
            )
        )
        fig.update_layout(
            legend=dict(
                orientation="v",
                entrywidth=50,
                yanchor="top",
                y=0.25,
                xanchor="right",
                x=0.7,
                bgcolor="#f3f3f3",
                bordercolor="Black",
                borderwidth=1,
            ),
        )
        if to_show:
            fig.show()
        if save_path is not None:
            pio.write_image(fig, save_path, scale=2, width=800, height=600)

    def compute_er_score(self, list_metrics: List = LIST_ALL_METRICS, add_mean: bool = False):
        """
        Compute the Enrichment Score for the given metric and energy
        """
        eval_helper = EvaluationHelper(
            list_metrics,
            LIST_ENERGIES,
            self.csv_folder,
            save_path=os.path.join("docker_data", "scores", os.path.basename(self.csv_folder)),
        )
        all_scores = eval_helper.compute_all_scores(add_mean=add_mean, paper_format=False)
        eval_helper.show_all_scores(all_scores=all_scores, show=False, add_mean=add_mean)

    def compute_er_score_metrics(self):
        """
        Compute the ER score for the metrics
        """
        eval_helper = EvaluationHelper(
            LIST_MAIN_METRICS,
            LIST_MAIN_METRICS,
            self.csv_folder,
            save_path=os.path.join(
                "docker_data", "scores", "metrics_" + os.path.basename(self.csv_folder)
            ),
            metrics_to_metrics=True,
        )
        all_scores = eval_helper.compute_all_scores(paper_format=False)
        eval_helper.show_all_scores(all_scores=all_scores, show=False)
