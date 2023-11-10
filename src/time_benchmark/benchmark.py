import os
import shutil

COMMAND = (
    "docker run -it -v ${PWD}/docker_data/:/app/docker_data -v ${PWD}/tmp:/tmp rnadvisor"
    " --native_path=$path_to_native --pred_path=$path_to_pred --result_path=$path_to_output "
    "--all_scores=ALL --time_path=$time_path"
)


class Benchmark:
    def __init__(self, input_path: str, output_path: str):
        self.input_path = input_path
        self.output_path = output_path

    def run(self):
        dirs = os.listdir(os.path.join(self.input_path, "decoys"))
        time_dir, tmp_dir = self.output_path, os.path.join(
            self.input_path, "tmp"
        )
        os.makedirs(time_dir, exist_ok=True)
        for dir in dirs:
            pred_dirs = os.path.join(self.input_path, "decoys", dir)
            native_path = os.path.join(pred_dirs, os.listdir(pred_dirs)[0])
            out_path = tmp_dir
            time_path = os.path.join(time_dir, f"{dir}.csv")
            self.run_docker(native_path, pred_dirs, out_path, time_path)
        shutil.rmtree(tmp_dir)

    def run_docker(self, native_path: str, pred_path: str, out_path: str, time_path: str):
        command = (
            COMMAND.replace("$path_to_native", native_path)
            .replace("$path_to_pred", pred_path)
            .replace("$path_to_output", out_path)
            .replace("$time_path", time_path)
        )
        os.system(command)


if __name__ == "__main__":
    input_path = os.path.join("docker_data", "input", "time")
    output_path = os.path.join("docker_data", "output", "time")
    benchmark = Benchmark(input_path, output_path)
    benchmark.run()
