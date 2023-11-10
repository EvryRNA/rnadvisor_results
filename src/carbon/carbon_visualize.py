import os
from typing import Dict

import pandas as pd
import plotly.express as px

METRICS = [
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
]
ENERGIES = ["DFIRE", "rsRNASP", "RASP", "BARNABA"]

ALL_SCORES = [
    "RMSD",
    "P-VALUE",
    "INF",
    "MCQ",
    "TM-SCORE",
    "CAD",
    "BARNABA",
    "CLASH",
    "GDT-TS",
    "lDDT",
    "DFIRE",
    "rsRNASP",
    "RASP",
    "BARNABA",
]


class CarbonVisualize:
    def __init__(self, carbon_path: str, save_path: str):
        self.all_df = self.read_csv(carbon_path)
        self.save_path = save_path
        os.makedirs(os.path.dirname(self.save_path), exist_ok=True)

    def read_csv(self, carbon_path: str):
        data: Dict = {"metric": [], "Dataset": [], "carbon": []}
        dfs = pd.DataFrame([])
        names = []
        for csv in os.listdir(carbon_path):
            df = pd.read_csv(os.path.join(carbon_path, csv))
            df = df.drop("NAME", axis=1)
            df = df.mean().to_frame().T * 1000
            dfs = pd.concat([dfs, df])
            name = csv.replace(".csv", "").replace("TestSet", "Test Set ")
            names.append(name)
            data["metric"] += list(df.columns)
            data["Dataset"].extend([name] * len(df.columns))
            data["carbon"] += list(df.values[0])
        new_df = pd.DataFrame(data)
        new_df = new_df[new_df["metric"].isin(ALL_SCORES)]
        new_df.replace("BARNABA", "eRMSD/eSCORE", inplace=True)
        new_df.replace("INF", r"$INF_{all}$", inplace=True)
        new_df.replace("CAD", "CAD-score", inplace=True)
        return new_df

    def update_fig(self, fig):
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
        fig.update_xaxes(title_text="Metrics/Scoring functions")
        fig.update_yaxes(title_text="Emissions (g/CO₂)")
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=14,  # Set the font size here
            )
        )
        return fig

    def run(self):
        fig = px.bar(self.all_df, x="metric", y="carbon", color="Dataset")
        fig = self.update_fig(fig)
        if self.save_path:
            fig.write_image(self.save_path, scale=2)
        else:
            fig.show()


if __name__ == "__main__":
    carbon_path = os.path.join("docker_data", "output", "carbon")
    save_path = os.path.join("docker_data", "plots", "carbon", "carbon.png")
    carbon_visualize = CarbonVisualize(carbon_path, save_path)
    carbon_visualize.run()
