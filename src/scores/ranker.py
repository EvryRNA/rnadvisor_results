from typing import Dict

import numpy as np
import pandas as pd

from src.scores.score_abstract import ScoreAbstract


class Ranker(ScoreAbstract):
    def __init__(self, normalize: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.agg_fn = np.mean
        self.normalize = normalize

    def _compute_score(self, metric: str, energy: str, df: pd.DataFrame, name: str) -> float:
        """
        Compute the Enrichment Score for the given metric and energy
        :param metric:
        :param energy:
        :return:
        """
        native_name = f"normalized_{name}.pdb"
        sorted_energy = df.sort_values(
            by=energy, ascending=(energy not in self.ascending_energies)
        )[energy]
        sorted_names = sorted_energy.index.tolist()
        try:
            rank = sorted_names.index(native_name)
        except ValueError:
            rank = sorted_names.index(f"{name}.pdb")
        if self.normalize:
            rank = rank / len(sorted_names)
        else:
            rank = rank + 1  # To ensure the first position is 1 and not 0
        return rank

    def convert_dict_to_df(self, scores: Dict, add_mean: bool = False) -> pd.DataFrame:
        """
        Convert the dictionary of scores to a dataframe by using the mean
        """
        new_scores = {
            energy: [
                round(self.agg_fn(scores[energy][metric]), 2)
                for metric in list(scores[energy].keys())
            ]
            for energy in list(scores.keys())
        }
        new_scores = pd.DataFrame(new_scores).iloc[0, :]
        return new_scores
