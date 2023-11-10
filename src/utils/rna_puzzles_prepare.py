import os
import shutil

"""
Clean the rp02 by removing the gap between nt 10-13 in chain G.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp02 for more details.
Clean the rp06 by moving chain U:1-168 to A:1-168 from predictions.
It also keeps chain A:1-17+24-110+115-168
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp06 for more details.
Clean the rp10 by extracting the A:1-96+B:6-66 from the native and predictions.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp10 for more details.
Clean the rp12 by extracting the A:2-16+34+39-123 from the native and predictions.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp12 for more details.
Clean the rp13 by extracting the A:1-45+57-71 from the native and predictions.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp13 for more details.
Clean the rp14_free by extracting the A:1-21+25-61 from the native and predictions.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp14_free for more details.
Clean the rp17 by extracting the A:1-47+52-62 from the native and predictions.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp17 for more details.
Clean the rp24 by extracting the A:1-34+36-112 from the native and predictions.
See https://github.com/RNA-Puzzles/standardized_dataset/tree/master/rp24 for more details.
"""

RNA_PUZZLES_COMMANDS = {
    "rp02.pdb": "rna_pdb_tools.py --delete G:11-12 $PATH_IN > $PATH_OUT",
    "rp06.pdb": "rna_pdb_tools.py --delete A:18-23+111-114 $PATH_IN > $PATH_OUT",
    "rp10.pdb": "rna_pdb_tools.py --extract 'A:1-96+B:6-66' $PATH_IN > $PATH_OUT",
    "rp12.pdb": "rna_pdb_tools.py --extract 'A:2-16+34+39-123' $PATH_IN > $PATH_OUT",
    "rp13.pdb": "rna_pdb_tools.py --extract 'A:1-45+57-71' $PATH_IN > $PATH_OUT",
    "rp14_free.pdb": "rna_pdb_tools.py --extract 'A:1-21+25-61' $PATH_IN > $PATH_OUT",
    "rp17.pdb": "rna_pdb_tools.py --extract 'A:1-47+52-62' $PATH_IN > $PATH_OUT",
    "rp24.pdb": "rna_pdb_tools.py --extract 'A:1-34+36-112' $PATH_IN > $PATH_OUT",
}


class RNAPuzzlesPrepare:
    def __init__(self, input_path: str, output_path: str):
        """
        Clean the RNA Puzzles dataset that is standardized.
        It applies different transformation for each RNA Puzzles dataset.
        :param input_path: input path where are located the dataset
        :param output_path: where to save the new files.
        """
        self.input_path = input_path
        self.output_path = output_path
        self._init_output_path()

    def _init_output_path(self):
        os.makedirs(self.output_path, exist_ok=True)
        native_path, pred_path = os.path.join(self.output_path, "NATIVE"), os.path.join(
            self.output_path, "PREDS"
        )
        os.makedirs(native_path, exist_ok=True)
        os.makedirs(pred_path, exist_ok=True)

    def run(self):
        list_rp = os.listdir(os.path.join(self.input_path, "NATIVE"))
        for challenge in list_rp:
            self._clean_challenge(challenge)
        shutil.move(self.output_path, self.input_path)

    def _clean_challenge(self, challenge: str):
        """
        Clean the data for the given challenge.
        :param challenge: rpX with X the number of the challenge
        :return:
        """
        native_in, native_out = os.path.join(self.input_path, "NATIVE", challenge), os.path.join(
            self.output_path, "NATIVE", challenge
        )
        pred_in, pred_out = os.path.join(
            self.input_path, "PREDS", challenge.replace(".pdb", "")
        ), os.path.join(self.output_path, "PREDS", challenge.replace(".pdb", ""))
        if challenge in RNA_PUZZLES_COMMANDS:
            self.clean_rp(challenge, native_in, native_out, pred_in, pred_out)
        else:
            shutil.copy(native_in, native_out)
            shutil.copytree(pred_in, pred_out, dirs_exist_ok=True)

    def clean_rp(self, rp_name: str, native_in: str, native_out, pred_in: str, pred_out: str):
        """
        Clean the rpX using the commands from RNA_PUZZLES_COMMANDS.
        :param rp_name: the name of the current puzzle.
        :return:
        """
        os.makedirs(pred_out, exist_ok=True)
        self.launch_command(rp_name, native_in, native_out)
        for rna in os.listdir(pred_in):
            rna_in, rna_out = os.path.join(pred_in, rna), os.path.join(pred_out, rna)
            self.launch_command(rp_name, rna_in, rna_out)

    def launch_command(self, rp_name: str, in_path: str, out_path: str):
        """
        Launch the os command to clean the structure
        """
        command = (
            RNA_PUZZLES_COMMANDS[rp_name]
            .replace("$PATH_IN", in_path)
            .replace("$PATH_OUT", out_path)
        )
        os.system(command)


if __name__ == "__main__":
    input_path = os.path.join("docker_data", "input", "TestSetIII")
    output_path = os.path.join("docker_data", "input", "TestSetIII_clean")
    rna_puzzles_prepare = RNAPuzzlesPrepare(input_path, output_path)
    rna_puzzles_prepare.run()
