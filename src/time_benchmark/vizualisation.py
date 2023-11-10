import os
from typing import Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.io as pio

LIST_ENERGIES = ["RASP-ENERGY", "BARNABA-eSCORE", "DFIRE", "rsRNASP"]
LIST_METRICS = [
    "RMSD",
    "INF-ALL",
    "DI",
    "MCQ",
    "TM-score",
    "GDT-TS",
    "CAD",
    "BARNABA-eRMSD",
    "lDDT",
]

COLORS_ENERGIES = {
    "RASP": "#6499E9",
    "εSCORE": "#B5CB99",
    "DFIRE": "#EF6262",
    "rsRNASP": "#F3AA60",
}


class Vizualisation:
    def __init__(self, benchmark_path: str):
        self.benchmark_path = benchmark_path
        self.dfs = {
            name.replace("decoy_", "").replace(".csv", ""): pd.read_csv(
                os.path.join(benchmark_path, name), index_col=[0]
            )
            for name in [x for x in os.listdir(benchmark_path) if not x.endswith("50.csv")]
        }

    def plot_energies(self):
        self.plot(LIST_ENERGIES)

    def plot_metrics(self):
        self.plot(LIST_METRICS)

    def convert_df_to_plot(self, list_scores: List[str]):
        new_df: Dict = {"method": [], "time": [], "nt_length": [], "time_std": []}
        for method, df in self.dfs.items():
            for score in list_scores:
                new_df["method"].append(score)
                try:
                    new_df["time"].append(df[score].mean())
                except KeyError:
                    breakpoint()
                new_df["time_std"].append(df[score].std())
                new_df["nt_length"].append(int(method))
        df = pd.DataFrame(new_df)
        return df

    def plot_all(self):
        self.plot(
            LIST_ENERGIES, save_path=os.path.join("docker_data", "plots", "time", "time_energies.png")
        )
        self.plot(LIST_METRICS, save_path=os.path.join("docker_data", "plots", "time", "time_metrics.png"))

    def _change_names(self, df: pd.DataFrame):
        dict_to_change = {
            "BARNABA-eRMSD": "εRMSD",
            "BARNABA-eSCORE": "εSCORE",
            "RASP-ENERGY": "RASP",
            "tm-score-ost": "TM-score",
            "INF-ALL": r"$INF_{all}$",
            "CAD": "CAD-score",
        }
        for old_value, new_value in dict_to_change.items():
            df = df.replace(old_value, new_value)
        return df

    def plot(self, list_scores: List[str], save_path: Optional[str] = None):
        df = self.convert_df_to_plot(list_scores)
        df.sort_values(by="nt_length", inplace=True)
        df = self._change_names(df)
        new_method = (
            "<b>Scoring functions<b>" if "RASP" in df["method"].values else "<b>Metrics<b>\n"
        )
        df = df.rename(columns={"method": new_method})
        fig = px.line(
            data_frame=df,
            x="nt_length",
            y="time",
            color=new_method,
            markers=True,
            log_y=False,
            color_discrete_map=COLORS_ENERGIES,
            symbol_sequence=["cross"] * len(df),
        )
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
        fig.update_xaxes(title_text="RNA length (nt)")
        fig.update_yaxes(title_text="Time (s)")
        fig.update_layout(
            font=dict(
                family="Computer Modern",
                size=14,  # Set the font size here
            )
        )
        fig.update_layout(
            legend=dict(
                orientation="v",
                entrywidth=10,
                yanchor="top",
                xanchor="left",
                bgcolor="#f3f3f3",
                bordercolor="Black",
                borderwidth=1,
            ),
        )
        if save_path is not None:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            pio.write_image(fig, save_path, scale=2, width=800, height=400)
        fig.show()


if __name__ == "__main__":
    viz = Vizualisation(os.path.join("docker_data", "output", "time"))
    viz.plot_all()
