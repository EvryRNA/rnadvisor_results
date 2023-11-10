import os
import random

import numpy as np
from Bio import PDB

np.random.seed(77)
random.seed(77)


class ExtractPDB:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path

    def select_chain_indexes(self, chain_len: float, chain_step: float, n_decoys: int):
        if chain_len == chain_step:
            return [(0, chain_len) for _ in range(n_decoys)]
        indices = [i for i in range(0, chain_len - chain_step)]  # type: ignore
        start_indexes = random.sample(indices, n_decoys)
        chain_indexes = [(start_i, start_i + chain_step) for start_i in start_indexes]
        return chain_indexes

    def extract(self, new_length: int, n_decoys: int, step: int):
        # Load the PDB structure
        # Select a chain (replace 'A' with the chain ID you want to modify)
        indexes = self.select_chain_indexes(2850, new_length, n_decoys)
        for i, index in enumerate(indexes):
            parser = PDB.PDBParser()
            structure = parser.get_structure("structure", self.input_path)
            chain_id = "A"
            chain = structure[0][chain_id]
            # Truncate the chain's residues to the new length
            chain.child_list = chain.child_list[index[0] : index[1]]  # noqa: E203
            # Save the modified structure to a new PDB file
            io = PDB.PDBIO()
            io.set_structure(structure)
            out_dir = os.path.join(self.output_path, f"decoy_{new_length}")
            os.makedirs(out_dir, exist_ok=True)
            path_to_save = os.path.join(out_dir, f"decoy_{new_length}.pdb")
            io.save(path_to_save.replace(".pdb", f"_{i}.pdb"))

    def run(self, min_len: int, max_len: int, step: int, n_decoys: int):
        for i in range(min_len, max_len + 1, step):
            self.extract(i, n_decoys, step)


if __name__ == "__main__":
    input_path = os.path.join("docker_data", "input",  "TestSetI", "NATIVE", "3f1hA.pdb")
    output_path = os.path.join("docker_data", "input", "time", "decoys")
    extract_pdb = ExtractPDB(input_path, output_path)
    MIN_LEN, MAX_LEN, STEP, N_DECOYS = 50, 2850, 50, 5
    extract_pdb.run(MIN_LEN, MAX_LEN, STEP, N_DECOYS)
