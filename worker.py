## Copyright 2021 Tom Brown

## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.

## License and more information at:
## https://github.com/PyPSA/pypsa-server




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
