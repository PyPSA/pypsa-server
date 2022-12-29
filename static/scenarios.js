// Copyright 2021 Tom Brown

// This program is free software; you can redistribute it and/or
// modify it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation; either version 3 of the
// License, or (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// License and more information at:
// https://github.com/PyPSA/pypsa-server


assumptions = {"scenario_name" : "no name",
	       "region" : "EU",
               "co2_limit" : 0.,
	       "frequency" : 193,
	       "land_transport_electric_share" : 0.85,
	       "land_transport_fuel_cell_share" : 0.15,
	       "bev_dsm" : true,
	       "v2g" : true,
	       "central" : true,
	       "tes" : true,
	       "space_heat_demand" : 0.71,
	       "water_heat_demand" : 1.0,
               "electricity_demand" : 0.9,
	       "land_transport_demand" : 1.0,
	       "shipping_demand" : 1.0,
	       "aviation_demand" : 1.2,
	       "industry_demand" : 0.9,
	       "co2_sequestration_potential" : 200,
	       "solar_potential" : 1.0,
	       "onwind_potential" : 1.0,
	       "offwind_potential" : 1.0,
	       "linemax_extension" : 10.,
	       "line_volume" : 1.5,
	       "solar_cost" : 302,
	       "onwind_cost" : 963,
	       "offwind_cost" : 1416,
	       "nuclear_cost" : 7940,
	       "electrolysis_cost" : 500,
	       "land_transmission_cost" : 400,
	       "h2_pipeline_cost" : 267,
	       "co2_sequestration_cost" : 20,
	      };

original_co2_sequestration_potential = assumptions["co2_sequestration_potential"];

for (let i = 0; i < Object.keys(assumptions).length; i++){
    let key = Object.keys(assumptions)[i];
    let value = assumptions[key];
    if(typeof value === "boolean"){
	document.getElementsByName(key)[0].checked = value;
	d3.selectAll("input[name='" + key + "']").on("change", function(){
	    assumptions[key] = this.checked;
	    console.log(key,"changed to",assumptions[key]);
	});
    } else if (key === "region"){
	document.getElementsByName(key)[0].value = value;
	d3.selectAll("select[name='region']").on("change", function(){
	    assumptions[key] = this.value;
	    console.log(key,"changed to",assumptions[key]);
	    console.log(this.value,"makes up",country_fractions[this.value],"of the European total");
	    let co2_value = (country_fractions[this.value]*original_co2_sequestration_potential).toFixed(2);
	    document.getElementsByName("co2_sequestration_potential")[0].value = co2_value;
	    assumptions["co2_sequestration_potential"] = co2_value;
	    console.log("co2_sequestration_potential","changed to",assumptions["co2_sequestration_potential"]);
	});
    } else{
	document.getElementsByName(key)[0].value = value;
	d3.selectAll("input[name='" + key + "']").on("change", function(){
	    assumptions[key] = this.value;
	    console.log(key,"changed to",assumptions[key]);
	});
    }
};



var solveButton = d3.select("#solve-button");

var solveButtonText = {"before" : "Solve",
		       "after" : "Solving"}


var jobid = "";

var timer;
var timeout;
var timerStart;
var timerExpected = 10;


// time between status polling in milliseconds
var poll_interval = 2000;

// time out for polling if it doesn't finish after 10 minutes
// Shouldn't be divisible by poll_interval
var poll_timeout = 10*60*1000 + poll_interval/2;


function solve() {
    if (solveButton.text() == solveButtonText["before"]) {
	var send_job = new XMLHttpRequest();
	send_job.open('POST', './jobs', true);
	send_job.setRequestHeader("Content-Type", "application/json");
	send_job.onload = function () {
	    var data = JSON.parse(this.response);
	    if(data["status"] == "Solving"){
		jobid = data["jobid"];
		console.log("Jobid:",jobid);
		timer = setInterval(poll_result, poll_interval);
		timerStart = new Date().getTime();
		console.log("timer",timer,"polling every",poll_interval,"milliseconds");
		timeout = setTimeout(poll_kill, poll_timeout);
		solveButton.text(solveButtonText["after"]);
		solveButton.attr("disabled","");
		document.getElementById("status").innerHTML="Sending job to solver";
	    } else if(data["status"] == "Solved") {
		jobid = data["jobid"];
		console.log("Jobid:",jobid);
		document.getElementById("status").innerHTML='This set of assumptions has already been computed and can be viewed at <a href="results/' + jobid + '">' + jobid + '</a>.' ;
	    } else if(data["status"] == "Error") {
		console.log("results:", data);
		document.getElementById("status").innerHTML = data["status"] + ": " + data["error"];
	    } else {
	    };
	};
	send_job.send(JSON.stringify(assumptions));
    };
};


solveButton.on("click", solve);



function poll_result() {

    var poll = new XMLHttpRequest();

    poll.open('GET', './jobs/' + jobid, true);

    poll.onload = function () {
	results = JSON.parse(this.response);
	status = results["status"];
	document.getElementById("status").innerHTML=status;
	console.log("status is",status);

	if(status == "Error"){
	    clearInterval(timer);
	    clearTimeout(timeout);
	    console.log("results:",results);
	    document.getElementById("status").innerHTML=status + ": " + results["error"];
	    solveButton.text(solveButtonText["before"]);
	    $('#solve-button').removeAttr("disabled");
	};
	if(status == "Finished"){
	    clearInterval(timer);
	    clearTimeout(timeout);
	    console.log("results:",results);
	    solveButton.text(solveButtonText["before"]);
            document.getElementById("status").innerHTML='Finished. Results can be viewed at <a href="results/' + jobid + '">' + jobid + '</a>.' ;
	    $('#solve-button').removeAttr("disabled");
	};
    };
    poll.send();
};





function poll_kill() {
    clearInterval(timer);
    solveButton.text(solveButtonText["before"]);
    $('#solve-button').removeAttr("disabled");
    document.getElementById("status").innerHTML="Error: Timed out";
};
