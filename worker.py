import os, snakemake
from rq import get_current_job


def solve(assumptions):

    print(assumptions)

    job = get_current_job()
    jobid = job.get_id()

    job.meta['status'] = "Reading in data"
    job.save_meta()

    run_name = jobid

    dir_name = "static/results"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)

    dir_name = f"static/results/{run_name}"
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)


    costs_name = os.path.join(dir_name,"costs.csv")

    f = open(costs_name,"w")

    f.write("name,value\n")

    f.write("PV,{}\n".format(assumptions["pv_cost"]))

    f.close()

    config_name = os.path.join(dir_name,"config.yaml")

    f = open(config_name,"w")

    f.write(f"run_name: {run_name}\n")

    f.write("rooftop: {}\n".format(assumptions["rooftop"]))

    f.close()

    job.meta['status'] = "Running snakemake workflow"
    job.save_meta()

    snakemake.snakemake("Snakefile",configfiles=[config_name])

    return {}
