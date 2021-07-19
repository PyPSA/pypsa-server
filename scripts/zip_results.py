import os

sum_dir = snakemake.config["summary_dir"]

job = snakemake.config["run"]

os.chdir(sum_dir)

command = f"zip -r {job}/{job}.zip {job}"

print(command)

os.system(command)
