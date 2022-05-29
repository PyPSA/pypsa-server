

let n_scenarios = scenarios.length;

let scenario_names = [];

for (i=0; i < n_scenarios; i++){
    scenario_names.push(scenario_data[scenarios[i]]["scenario_name"]);
};

function draw_stack(data, labels, color, ylabel, svgName, suffix){

    let totals = [];
    for(let s=0; s < n_scenarios; s++){
	total = 0.;
	for (let k=0; k < data[s].length; k++){
	    total += data[s][k];
	};
	totals.push(total);
    };

    let svgGraph = d3.select(svgName),
	margin = {top: 20, right: 20, bottom: 30, left: 50},
	width = svgGraph.attr("width") - margin.left - margin.right,
	height = svgGraph.attr("height") - margin.top - margin.bottom;

    // remove existing
    svgGraph.selectAll("g").remove();
    let x = d3.scaleLinear().range([0, width]);
    let y = d3.scaleLinear().range([height, 0]);

    x.domain([0,n_scenarios]);
    y.domain([0,Math.max(...totals)]).nice();

    let tip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([-8, 0])
	.html(function(d,i) {
	    return labels[i] + ": " + Math.abs(d).toFixed(1) + suffix;
	});
    svgGraph.call(tip);

    for(let s=0; s < data.length; s++){

	var g = svgGraph.append("g")
            .attr("transform", "translate(" + (x(s) + margin.left) + "," + margin.top + ")");

	let totals = [0.];
	for (let k=0; k < data[s].length; k++){
	    totals.push(totals[k] + data[s][k]);
	};

	var layer = g.selectAll("rect")
	    .data(data[s])
	    .enter().append("rect")
	    .attr("x", x(0.1))
	    .attr("width", x(0.6))
        .attr("y", function(d,i) { return y(totals[i+1]);})
        // following abs avoids rect with negative height e.g. -1e10
	.attr("height", function(d,i) { return Math.abs((y(totals[i]) - y(totals[i+1])).toFixed(2)); })
    	.attr("width", x(0.8))
        .style("fill", function(d, i) { return color[i];})
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);
    };

    var g = svgGraph.append("g")
        .attr("transform", "translate(" + (margin.left) + "," + margin.top + ")");

    g.append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(y));

    var label = svgGraph.append("g").attr("class", "y-label");

    // text label for the y axis
    label.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(ylabel);

    // add the x Axis
    let xAxisGenerator = d3.axisBottom(x);
    xAxisGenerator.ticks(n_scenarios);

    let ticks = [];
    for(i=0;i < n_scenarios; i++){
	ticks.push(i+0.5);
    };

    xAxisGenerator.tickValues(ticks);
    xAxisGenerator.tickFormat((d,i) => scenario_names[i]);
    svgGraph.append("g")
        .attr("transform", "translate(" + margin.left + "," + (height + margin.top) + ")")
        .call(xAxisGenerator);



    //Legend
    let legendSVG = d3.select(svgName + "_legend");

    let legend = legendSVG.selectAll("g")
	.data(labels)
	.enter()
	.append("g")
	.attr("transform", function (d, i) {  return "translate(0," + (5 + i * 15) + ")" });

    legend.append("rect")
	.attr("x",0)
	.attr("y",0)
	.attr("width", 10)
	.attr("height", 10)
	.style("fill", function (d, i) { return color[color.length - i - 1] });

    legend.append("text")
	.attr("x",20)
	.attr("y",10)
	.text(function (d, i) { return labels[labels.length - i - 1]});
};



function draw_balance_stack(balance, balances){

    let svgName = "#" + balance + "_graph";
    let ylabel = balances["label"] + " [" + balances["units"] + "]";
    let suffix = " " + balances["units"];

    let signs = ["positive", "negative"];
    let totals = {"positive" : [],
		  "negative" : []};
    for (let s=0; s < n_scenarios; s++){
	for (let p=0; p <2; p++){
	    let sign = signs[p];
	    total = 0.;
	    for (let k=0; k < balances[sign]["data"][s].length; k++){
		total += balances[sign]["data"][s][k];
	    };
	    totals[sign].push(total);
	};
    };

    let svgGraph = d3.select(svgName),
	margin = {top: 20, right: 20, bottom: 30, left: 50},
	width = svgGraph.attr("width") - margin.left - margin.right,
	height = svgGraph.attr("height") - margin.top - margin.bottom;

    // remove existing
    svgGraph.selectAll("g").remove();
    let x = d3.scaleLinear().range([0, width]);
    let y = d3.scaleLinear().range([height, 0]);

    x.domain([0,n_scenarios]);
    y.domain([Math.min(...totals["negative"]),Math.max(...totals["positive"])]).nice();

    let tip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([-8, 0])
	.html(function(d,i) {
	    return balances["positive"]["techs"][i] + ": " + Math.abs(d).toFixed(1) + suffix;
	});
    svgGraph.call(tip);

    let negative_tip = d3.tip()
	.attr('class', 'd3-tip')
	.offset([-8, 0])
	.html(function(d,i) {
	    return balances["negative"]["techs"][i] + ": -" + Math.abs(d).toFixed(1) + suffix;
	});
    svgGraph.call(negative_tip);

    for(let s=0; s < n_scenarios; s++){

	var g = svgGraph.append("g")
            .attr("transform", "translate(" + (x(s) + margin.left) + "," + margin.top + ")");

	let totals = [0.];
	for (let k=0; k < balances["positive"]["data"][s].length; k++){
	    totals.push(totals[k] + balances["positive"]["data"][s][k]);
	};

	var layer = g.selectAll("rect")
	    .data(balances["positive"]["data"][s])
	    .enter().append("rect")
	    .attr("x", x(0.1))
	    .attr("width", x(0.6))
        .attr("y", function(d,i) { return y(totals[i+1]);})
        // following abs avoids rect with negative height e.g. -1e10
	.attr("height", function(d,i) { return Math.abs((y(totals[i]) - y(totals[i+1])).toFixed(2)); })
    	.attr("width", x(0.8))
        .style("fill", function(d, i) { return balances["positive"]["color"][i];})
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

	var h = svgGraph.append("g")
            .attr("transform", "translate(" + (x(s) + margin.left) + "," + margin.top + ")");

	let negative_totals = [0.];
	for (let k=0; k < balances["negative"]["data"][s].length; k++){
	    negative_totals.push(negative_totals[k] + balances["negative"]["data"][s][k]);
	};

	var layer = h.selectAll("rect")
	    .data(balances["negative"]["data"][s])
	    .enter().append("rect")
	    .attr("x", x(0.1))
	    .attr("width", x(0.6))
        .attr("y", function(d,i) { return y(negative_totals[i]);})
        // following abs avoids rect with negative height e.g. -1e10
	.attr("height", function(d,i) { return Math.abs((y(negative_totals[i]) - y(negative_totals[i+1])).toFixed(2)); })
    	.attr("width", x(0.8))
        .style("fill", function(d, i) { return balances["negative"]["color"][i];})
	.on('mouseover', negative_tip.show)
        .on('mouseout', negative_tip.hide);

    };

    var g = svgGraph.append("g")
        .attr("transform", "translate(" + (margin.left) + "," + margin.top + ")");

    g.append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(y));

    var label = svgGraph.append("g").attr("class", "y-label");

    // text label for the y axis
    label.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text(ylabel);

    // add the x Axis
    let xAxisGenerator = d3.axisBottom(x);
    xAxisGenerator.ticks(n_scenarios);

    let ticks = [];
    for(i=0;i < n_scenarios; i++){
	ticks.push(i+0.5);
    };

    xAxisGenerator.tickValues(ticks);
    xAxisGenerator.tickFormat((d,i) => scenario_names[i]);
    svgGraph.append("g")
        .attr("transform", "translate(" + margin.left + "," + (height + margin.top) + ")")
        .call(xAxisGenerator);

    //Legend

    //slice to make copy
    let labels = balances["positive"]["techs"].slice().reverse().concat(balances["negative"]["techs"]);
    let color = balances["positive"]["color"].slice().reverse().concat(balances["negative"]["color"]);

    let legendSVG = d3.select(svgName + "_legend");

    let legend = legendSVG.selectAll("g")
	.data(labels)
	.enter()
	.append("g")
	.attr("transform", function (d, i) {  return "translate(0," + (5 + i * 15) + ")" });

    legend.append("rect")
	.attr("x",0)
	.attr("y",0)
	.attr("width", 10)
	.attr("height", 10)
	.style("fill", function (d, i) { return color[i] });

    legend.append("text")
	.attr("x",20)
	.attr("y",10)
	.text(function (d, i) { return d});
};


draw_stack(costs["data"], costs["techs"], costs["color"], "system costs [bnEUR/a]", "#costs_graph", " bnEUR/a");

draw_stack(capacities["data"], capacities["techs"], capacities["color"], "capacities [GW]", "#capacities_graph", " GW");


let balances_div = document.getElementById("balances_div");

for (k=0; k < balances_selection.length; k++){
    balance = balances_selection[k];
    balance_name = balances[balance]["name"];
    draw_balance_stack(balance,balances[balance]);
};
