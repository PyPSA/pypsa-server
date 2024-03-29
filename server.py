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

import json, os, hashlib, yaml, sys

import pandas as pd


sys.path.append("scripts")

from plot_summary import rename_techs, preferred_order


with open(f"config.yaml",'r') as f:
    config = yaml.safe_load(f)

country_fractions = pd.read_csv("resources/country_fractions.csv",index_col=0).squeeze("columns")

#in seconds
job_timeout=60*60*20

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

strings = ["scenario_name","region"]

ints = ["frequency"]

float_upper_limit = 1e7


balances_selection = ["AC", "low_voltage", "H2", "gas", "oil", "co2", "co2_stored", "residential_rural_heat", "urban_central_heat"]

balances_names = {"AC" : "high voltage electricity",
		  "low_voltage" : "low voltage electricity",
		  "H2" : "hydrogen",
		  "gas" : "methane",
		  "oil" : "liquid hydrocarbon",
		  "co2" : "CO2",
		  "co2_stored" : "stored CO2",
		  "residential_rural_heat" : "residential rural building heating",
		  "urban_central_heat" : "urban district heating"}


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

        if key != "co2_limit" and (assumptions[key] < 0 or assumptions[key] > float_upper_limit):
            return "{} {} was not in the valid range [0,{}]".format(key,assumptions[key],float_upper_limit), None

    for key in ints:
        try:
            assumptions[key] = int(assumptions[key])
        except:
            return "{} {} could not be converted to an integer".format(key,assumptions[key]), None

    for key in strings:
        assumptions[key] = str(assumptions[key])

    return None, assumptions


def compute_assumptions_hash(assumptions):
    results_string = ""
    for item in ints+booleans+floats:
        results_string += "&{}={}".format(item,assumptions[item])
    if assumptions["region"] != "EU":
        results_string += "&region={}".format(assumptions["region"])
    hashid = hashlib.md5(results_string.encode()).hexdigest()
    return hashid

#defaults to only listen to GET and HEAD
@app.route('/')
def root():
    return render_template('index.html')

@app.route('/submit')
def submit():
    return render_template('submit.html',
                           country_fractions=country_fractions.to_dict())

@app.route('/results')
def results():
    scenarios = pd.read_csv("static/scenarios.csv",
                            names=["jobid","scenario_name","datetime","co2_shadow","total_costs","diff","hashid"]).fillna("")
    print(scenarios)
    print(scenarios.dtypes)
    return render_template('results.html',
                           scenarios=scenarios.T.to_dict())



@app.route('/results/<jobid>')
def resultsid(jobid):

    jobids = jobid.split(",")

    print(jobids)

    costs_df = pd.DataFrame()
    capacities_df = pd.DataFrame()
    balances_df = pd.DataFrame()

    for jobid in jobids:
        if not os.path.isdir(f"static/results/{jobid}"):
            abort(404)

        costs_df[jobid] = pd.read_csv(f"static/results/{jobid}/csvs/costs.csv",
                                      index_col=list(range(3)),
                                      squeeze=True)
        capacities_df[jobid] = pd.read_csv(f"static/results/{jobid}/csvs/capacities.csv",
                                      index_col=list(range(2)),
                                      squeeze=True)
        balances_df[jobid] = pd.read_csv(f"static/results/{jobid}/csvs/supply_energy.csv",
                                      index_col=list(range(3)),
                                      squeeze=True)

    # costs

    costs_df = costs_df.groupby(costs_df.index.get_level_values(2)).sum()
    costs_df = costs_df.groupby(costs_df.index.map(rename_techs)).sum()/1e9
    to_drop = costs_df.index[costs_df.max(axis=1) < config['plotting']['costs_threshold']*costs_df.sum().max()]
    print("dropping")
    print(costs_df.loc[to_drop])
    costs_df = costs_df.drop(to_drop)
    new_index = preferred_order.intersection(costs_df.index).append(costs_df.index.difference(preferred_order))
    costs_df = costs_df.loc[new_index]

    costs = {}
    costs["data"] = [costs_df[jobid].tolist() for jobid in jobids]
    costs["techs"] = costs_df.index.tolist()
    costs["color"] = [config['plotting']['tech_colors'][i] for i in costs_df.index]


    # capacities

    capacities_df = capacities_df.groupby(level=1).sum()/1e3
    capacities_df = capacities_df.groupby(capacities_df.index.map(rename_techs)).sum()
    selection = ["gas CHP","biomass CHP","H2 Fuel Cell","OCGT","nuclear","solar PV rooftop","solar PV utility","offshore wind (DC)","offshore wind (AC)","onshore wind","hydroelectricity","Fischer-Tropsch","H2 Electrolysis","resistive heater","air heat pump","ground heat pump"]
    capacities_df = capacities_df.loc[[s for s in selection if s in capacities_df.index]]

    capacities = {}
    capacities["data"] = [capacities_df[jobid].tolist() for jobid in jobids]
    capacities["techs"] = capacities_df.index.tolist()
    capacities["color"] = [config['plotting']['tech_colors'][i] for i in capacities_df.index]


    # balances

    co2_carriers = ["co2","co2 stored","process emissions"]
    balance_selections = {i.replace(" ","_") : [i] for i in balances_df.index.levels[0]}
    balance_selections["energy"] = balances_df.index.levels[0].symmetric_difference(co2_carriers)

    balances = {}
    for k in balances_selection:
        if k not in balance_selections:
            continue

        balances[k] = {}
        balances[k]["name"] = balances_names[k]
        if balance_selections[k][0] in co2_carriers:
            balances[k]["label"] = "CO2"
            balances[k]["units"] = "MtCO2/a"
        else:
            balances[k]["label"] = "energy"
            balances[k]["units"] = "TWh/a"

        df = balances_df.loc[balance_selections[k]]
        df = df.groupby(df.index.get_level_values(2)).sum()/1e6
        df.index = [i[:-1] if ((i != "co2") and (i[-1:] in ["0","1","2","3"])) else i for i in df.index]
        df = df.groupby(df.index.map(rename_techs)).sum()

        new_index = preferred_order.intersection(df.index).append(df.index.difference(preferred_order))
        df = df.loc[new_index]
        to_drop = df.index[df.abs().max(axis=1) < config['plotting']['energy_threshold']*df.abs().sum().max()]
        print("dropping")
        print(df.loc[to_drop])
        df = df.drop(to_drop)

        positive_index = df.index[df.sum(axis=1) > 0]
        negative_index = df.index[df.sum(axis=1) < 0]

        balances[k]["positive"] = {}
        balances[k]["negative"] = {}

        balances[k]["positive"]["data"] = [df.loc[positive_index,jobid].tolist() for jobid in jobids]
        balances[k]["positive"]["techs"] = positive_index.tolist()
        balances[k]["positive"]["color"] = [config['plotting']['tech_colors'][i] for i in positive_index]

        balances[k]["negative"]["data"] = [df.loc[negative_index,jobid].tolist() for jobid in jobids]
        balances[k]["negative"]["techs"] = negative_index.tolist()
        balances[k]["negative"]["color"] = [config['plotting']['tech_colors'][i] for i in negative_index]


    # primary energy

    primary = balances_df[(balances_df.index.get_level_values(1).isin(["generators", "storage_units","stores"])& ~balances_df.index.get_level_values(2).isin(["co2 stored","co2"])) ^ balances_df.index.get_level_values(2).str.contains("heat pump") ]

    #this sum subtracts electricity input from heat output for heat pumps
    primary = primary.groupby(primary.index.get_level_values(2)).sum()
    primary = primary.groupby(primary.index.map(rename_techs)).sum()/1e6

    primary.rename({"uranium" : "nuclear heat",
                    "air heat pump" : "ambient air heat",
                    "ground heat pump" : "ambient ground heat"},
                   inplace=True)

    new_index = preferred_order.intersection(primary.index).append(primary.index.difference(preferred_order))
    primary = primary.loc[new_index]

    to_drop = primary.index[primary.abs().max(axis=1) < 5]
    print("dropping")
    print(primary.loc[to_drop])
    primary = primary.drop(to_drop)

    primaries = {}
    primaries["data"] = [primary[jobid].tolist() for jobid in jobids]
    primaries["techs"] = primary.index.tolist()
    primaries["color"] = [config['plotting']['tech_colors'][i] for i in primary.index]


    # final energy

    final_dict = {"electricity": ['BEV charger0', 'V2G1',
                                  'home battery charger0',
                                  'home battery discharger1', 'residential rural ground heat pump0',
                                  'residential rural resistive heater0',
                                  'residential urban decentral air heat pump0',
                                  'residential urban decentral resistive heater0',
                                  'services rural ground heat pump0', 'services rural resistive heater0',
                                  'services urban decentral air heat pump0',
                                  'services urban decentral resistive heater0',
                                  'electricity', 'industry electricity'],
                  "methane" : ['gas for industry CC0', 'gas for industry0',
                               'residential rural gas boiler0',
                               'residential urban decentral gas boiler0', 'services rural gas boiler0',
                               'services urban decentral gas boiler0'],
                  "hydrogen" : ['H2 for industry', 'H2 for shipping',
                                'land transport fuel cell'],
                  "liquid hydrocarbons" : ['kerosene for aviation',
                                           'naphtha for industry'],
                  "district heat" : ['low-temperature heat for industry', 'urban central heat']}

    final_df = pd.DataFrame(columns=jobids)

    for carrier in ["electricity","methane","hydrogen","liquid hydrocarbons","district heat"]:
        final_df.loc[carrier] = -balances_df[balances_df.index.get_level_values(2).isin(final_dict[carrier])].sum()/1e6

    finals = {}
    finals["data"] = [final_df[jobid].tolist() for jobid in jobids]
    finals["techs"] = final_df.index.tolist()
    finals["color"] = [config['plotting']['tech_colors'][i] for i in final_df.index]

    scenarios = pd.read_csv("static/scenarios.csv",
                            names=["scenario_name","datetime","co2_shadow","total_costs","diff","hashid"],
                            index_col=0).fillna("")

    return render_template('compare.html',
                           scenarios=jobids,
                           scenario_data=scenarios.loc[jobids].T.to_dict(),
                           costs=costs,
                           capacities=capacities,
                           balances=balances,
                           balances_selection=[k for k in balances_selection if k in balance_selections],
                           primaries=primaries,
                           finals=finals)


@app.route('/jobs', methods=['GET','POST'])
def jobs():
    if request.method == "POST":
        if request.headers.get('Content-Type','missing') != 'application/json':
            return jsonify({"status" : "Error", "error" : "No JSON assumptions sent."})

        print(request.json)


        scenarios = pd.read_csv("static/scenarios.csv",
                                names=["jobid","scenario_name","datetime","co2_shadow","total_costs","diff","hashid"]).fillna("")


        error_message, assumptions = sanitise_assumptions(request.json)

        if error_message is not None:
            return jsonify({"status" : "Error", "error" : error_message})

        hashid = compute_assumptions_hash(assumptions)
        assumptions["hashid"] = hashid

        if hashid in scenarios["hashid"].values:
            print(hashid,"already computed")
            jobid = scenarios["jobid"][scenarios["hashid"] == hashid].iat[0]
            result = {"status" : "Solved", "jobid" : jobid}
            return jsonify(result)
        else:
            job = queue.enqueue("worker.solve", args=(assumptions,), job_timeout=job_timeout)
            result = {"status" : "Solving", "jobid" : job.get_id()}
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



@app.route('/series/<jobid>', methods=['GET'])
def series(jobid):

    series_csv = f"static/results/{jobid}/csvs/series.csv"

    if not os.path.isfile(series_csv):
        return jsonify({"status" : "Error", "error" : "Failed to find series."})

    series_df = pd.read_csv(series_csv,
                            index_col=0,
                            header=[0,1],
                            parse_dates=True).round(1)


    series = {}
    series["status"] = "Success"
    series["snapshots"] = [str(s) for s in series_df.index]

    for carrier in balances_selection:
        if carrier.replace("_"," ") not in series_df:
            continue

        print("processing series for energy carrier", carrier)

        #group technologies
        df = series_df[carrier.replace("_"," ")]
        df.columns = [i[:-1] if ((i != "co2") and (i[-1:] in ["0","1","2","3"])) else i for i in df.columns]
        df = df.groupby(df.columns.map(rename_techs),axis=1).sum()

        #drop inactive ones
        to_drop = df.columns[df.abs().max() < 1]
        print("dropping")
        print(to_drop)
        df.drop(to_drop,
                axis=1,
                inplace=True)

        #sort into positive and negative
        separated = {}
        separated["positive"] = pd.DataFrame(index=series_df.index,
                                             dtype=float)
        separated["negative"] = pd.DataFrame(index=series_df.index,
                                             dtype=float)

        for col in df.columns:
            if df[col].min() > -1:
                separated["positive"][col] = df[col]
                separated["positive"][col][separated["positive"][col] < 0] = 0

            elif df[col].max() < 1:
                separated["negative"][col] = df[col]
                separated["negative"][col][separated["negative"][col] > 0] = 0

            else:
                separated["positive"][col] = df[col]
                separated["positive"][col][separated["positive"][col] < 0] = 0
                separated["negative"][col] = df[col]
                separated["negative"][col][separated["negative"][col] > 0] = 0

        separated["negative"] *= -1

        series[carrier] = {}

        if carrier in ["co2", "co2_stored"]:
            series[carrier]["label"] = "CO2 flow"
            series[carrier]["units"] = "ktCO2/h"
        else:
            series[carrier]["label"] = "power"
            series[carrier]["units"] = "GW"

        for sign in ["positive","negative"]:
            series[carrier][sign] = {}
            series[carrier][sign]["columns"] = separated[sign].columns.tolist()
            series[carrier][sign]["data"] = (separated[sign].values/1e3).tolist()
            series[carrier][sign]["color"] = [config['plotting']['tech_colors'][i] for i in separated[sign].columns]


    return jsonify(series)


if __name__ == '__main__':
    app.run(port='5002')
