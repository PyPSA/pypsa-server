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




from flask import Flask, request, jsonify, render_template, Markup, abort


from redis import Redis

import rq
from rq.job import Job
from rq import Queue

import time, datetime

import json, os, hashlib, yaml

import pandas as pd

conn = Redis()

queue = Queue('pypsa', connection=conn)


app = Flask(__name__)
app.jinja_env.filters['json'] = lambda v: Markup(json.dumps(v))


booleans = ["bev_dsm","v2g","central","tes"]

floats = ["co2_limit",
          "land_transport_electric_share","land_transport_fuel_cell_share",
          "space_heat_demand","water_heat_demand",
          "electricity_demand","land_transport_demand","shipping_demand","aviation_demand","industry_demand",
          "co2_sequestration_potential",
          "solar_potential","onwind_potential","offwind_potential",
          "solar_cost","onwind_cost","offwind_cost","electrolysis_cost","nuclear_cost",
          "electrolysis_cost", "h2_pipeline_cost","co2_sequestration_cost",
          "land_transmission_cost", "linemax_extension", "line_volume"]

strings = ["scenario_name"]

ints = ["frequency"]

float_upper_limit = 1e7

def sanitise_assumptions(assumptions):
    """
    Fix types of assumptions and check they are in correct
    range.

    Parameters
    ----------
    assumptions : dict
        Assumptions (location, technical and economic parameters)

    Returns
    -------
    error_message : None or string
        If there was an error, details of the error
    assumptions : dict
        If there was no error, the clean type-safe assumptions
    """
    for key in strings+ints+booleans+floats:
        if key not in assumptions:
            return f"{key} missing from assumptions", None

    for key in booleans:
        try:
            assumptions[key] = bool(assumptions[key])
        except:
            return "{} {} could not be converted to boolean".format(key,assumptions[key]), None

    for key in floats:
        try:
            assumptions[key] = float(assumptions[key])
        except:
            return "{} {} could not be converted to float".format(key,assumptions[key]), None

        if assumptions[key] < 0 or assumptions[key] > float_upper_limit:
            return "{} {} was not in the valid range [0,{}]".format(key,assumptions[key],float_upper_limit), None

    for key in ints:
        try:
            assumptions[key] = int(assumptions[key])
        except:
            return "{} {} could not be converted to an integer".format(key,assumptions[key]), None

    for key in strings:
        assumptions[key] = str(assumptions[key])

    return None, assumptions


#defaults to only listen to GET and HEAD
@app.route('/')
def root():
    return render_template('index.html')

@app.route('/submit')
def submit():
    return render_template('submit.html')

@app.route('/results')
def results():
    scenarios = pd.read_csv("static/scenarios.csv",
                            names=["jobid","scenario_name","datetime","diff"])
    print(scenarios)
    return render_template('results.html',
                           scenarios=scenarios.T.to_dict())

@app.route('/results/<jobid>')
def resultsid(jobid):

    if not os.path.isdir(f"static/results/{jobid}"):
        abort(404)

    summary = pd.read_csv(f"static/results/{jobid}/csvs/metrics.csv",
                          names=["item","value"],
                          index_col=0,
                          squeeze=True)

    print(summary)

    print(summary.to_dict())

    with open(f"static/results/{jobid}/config.yaml",'r') as f:
        options = yaml.safe_load(f)

    with open(f"static/results/{jobid}/diff.yaml",'r') as f:
        diff = yaml.safe_load(f)

    return render_template('result.html',
                           jobid=jobid,
                           options=options,
                           diff=diff,
                           summary=summary.to_dict())


@app.route('/jobs', methods=['GET','POST'])
def jobs():
    if request.method == "POST":
        if request.headers.get('Content-Type','missing') != 'application/json':
            return jsonify({"status" : "Error", "error" : "No JSON assumptions sent."})

        print(request.json)

        error_message, assumptions = sanitise_assumptions(request.json)

        if error_message is not None:
            return jsonify({"status" : "Error", "error" : error_message})

        job = queue.enqueue("worker.solve", args=(assumptions,), job_timeout=600)
        result = {"jobid" : job.get_id()}
        return jsonify(result)
    elif request.method == "GET":
        return "jobs in queue: {}".format(len(queue.jobs))

@app.route('/jobs/<jobid>')
def jobid(jobid):
    try:
        job = Job.fetch(jobid, connection=conn)
    except:
        return jsonify({"status" : "Error", "error" : "Failed to find job!"})

    if job.is_failed:
        return jsonify({"status" : "Error", "error" : "Job failed."})

    try:
        status = job.meta['status']
    except:
        status = "Waiting for job to run (jobs in queue: {})".format(len(queue.jobs))

    result = {"status" : status}

    if job.is_finished:
        if "error" in job.result:
            result["status"] = "Error"
            result["error"] = job.result["error"]
        else:
            result["status"] = "Finished"

    return jsonify(result)


if __name__ == '__main__':
    app.run(port='5002')
