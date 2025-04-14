import os
import subprocess

env_path="C:\\Users\\21023\\miniconda3\\python.exe"
script_path="D:\\Rice_25spring\\594\\Jiayi_Gao\\noise_detection\\noise_detection_pipeline.py"
args= ["30691","AV"]

subprocess.run([env_path, script_path]+args)

base_dir = "./data/physionet_data/test_data"
for subdir in os.listdir(base_dir):
    subdir_path = os.path.join(base_dir, subdir)
    if os.path.isdir(subdir_path):
        for file in os.listdir(subdir_path):
            if file.endswith(".wav"):
                base_name=os.path.splitext(file)[0]
                id,pos=base_name.split("_")
                args=[id,pos]
                print("Running:"+" ".join(args)+"wav file")
                subprocess.run([env_path, script_path] + args)