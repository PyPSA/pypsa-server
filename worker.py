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




import os, snakemake, yaml, datetime
from rq import get_current_job

with open('defaults.yaml','r') as f:
    defaults = yaml.safe_load(f)

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

    with open("config.yaml", "r") as default_file:
        default = yaml.safe_load(default_file)

    default["run"] = run_name
    default["scenario"]["datetime"] = str(datetime.datetime.now())

    for item in ["scenario_name","co2_limit","frequency"]:
        default["scenario"][item] = assumptions[item]

    for forbidden in [",","\n"]:
        if forbidden in default["scenario"]["scenario_name"]:
            return {"error" : "Scenario name cannot contain commas or whitespace"}

    if default["scenario"]["frequency"] < 25:
        return {"error" : "Frequency must be 25-hourly or greater for computational reasons"}

    for tech in ["solar","onwind","offwind"]:
        default["scenario"][tech + "_potential"] = assumptions[tech + "_potential"]

    for tech in ["solar","onwind","offwind","nuclear","electrolysis","h2_pipeline"]:
        #scenario cost is ratio to default cost
        default["scenario"][tech + "_cost"] = assumptions[tech + "_cost"]/defaults[tech + "_cost"]

    for item in ["land_transport_electric_share","land_transport_fuel_cell_share",
                 "bev_dsm","v2g",
                 "central","tes",
                 "electricity_demand","land_transport_demand","shipping_demand","aviation_demand","industry_demand",
                 "co2_sequestration_potential",
                 "co2_sequestration_cost"]:
        default["sector"][item] = assumptions[item]

    default["sector"]["reduce_space_heat_exogenously_factor"] = 1 - assumptions['space_heat_demand']

    config_name = os.path.join(dir_name,"config.yaml")

    with open(config_name, "w") as output_file:
        yaml.dump(default, output_file)

    job.meta['status'] = "Running snakemake workflow"
    job.save_meta()

    success = snakemake.snakemake("Snakefile",configfiles=[config_name])

    if not success:
        return {"error" : "Snakemake failed"}

    with open("static/scenarios.csv","a") as f:
        f.write("{},{},{}\n".format(jobid,
                                    default["scenario"]["scenario_name"],
                                    default["scenario"]["datetime"]))

    return {}
