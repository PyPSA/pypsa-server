import os, snakemake

run_name = "my_run"


dir_name = f"results/{run_name}"

if not os.path.isdir(dir_name):
    os.mkdir(dir_name)


costs_name = os.path.join(dir_name,"costs.csv")

f = open(costs_name,"w")

f.write("name,value\n")

f.write("PV,300.\n")

f.close()

config_name = os.path.join(dir_name,"config.yaml")

f = open(config_name,"w")

f.write(f"run_name: {run_name}\n")

f.write("rooftop: True\n")

f.close()

snakemake.snakemake("Snakefile",configfiles=[config_name])
