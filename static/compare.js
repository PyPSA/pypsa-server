

var parseDate = d3.timeParse("%Y-%m-%d %H:%M:00");



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
	margin = {top: 20, right: 20, bottom: 30, left: 65},
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
	margin = {top: 20, right: 20, bottom: 30, left: 65},
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

draw_stack(primaries["data"], primaries["techs"], primaries["color"], "primary energy [TWh/a]", "#primaries_graph", " TWh/a");

draw_stack(finals["data"], finals["techs"], finals["color"], "final energy [TWh/a]", "#finals_graph", " TWh/a");


let balances_div = document.getElementById("balances_div");

for (k=0; k < balances_selection.length; k++){
    balance = balances_selection[k];
    balance_name = balances[balance]["name"];
    draw_balance_stack(balance,balances[balance]);
};




function draw_series(results, snapshots, balance){

    let selection = [...Array(snapshots.length).keys()];

    // Inspired by https://bl.ocks.org/mbostock/3885211

    var svgGraph = d3.select("#" + balance + "_power_graph"),
	margin = {top: 20, right: 20, bottom: 110, left: 50},
	marginContext = {top: 430, right: 20, bottom: 30, left: 50},
	width = svgGraph.attr("width") - margin.left - margin.right,
	height = svgGraph.attr("height") - margin.top - margin.bottom,
	heightContext = svgGraph.attr("height") - marginContext.top - marginContext.bottom;

    // remove existing
    svgGraph.selectAll("g").remove();

    var x = d3.scaleTime().range([0, width]).domain(d3.extent(snapshots));
    var y = d3.scaleLinear().range([height, 0]);
    var xContext = d3.scaleTime().range([0, width]).domain(d3.extent(snapshots));
    var yContext = d3.scaleLinear().range([heightContext, 0]);

    var xAxis = d3.axisBottom(x),
	xAxisContext = d3.axisBottom(xContext),
	yAxis = d3.axisLeft(y);


    var brush = d3.brushX()
        .extent([[0, 0], [width, heightContext]])
        .on("start brush end", brushed);


    var zoom = d3.zoom()
        .scaleExtent([1, Infinity])
        .translateExtent([[0, 0], [width, height]])
        .extent([[0, 0], [width, height]])
        .on("zoom", zoomed);


    var data = [];

    // Custom version of d3.stack

    var previous = new Array(selection.length).fill(0);

    for (var j = 0; j < results["positive"].columns.length; j++){
	var item = [];
	for (var k = 0; k < selection.length; k++){
	    item.push([previous[k], previous[k] + results["positive"]["data"][selection[k]][j]]);
	    previous[k] = previous[k] + results["positive"]["data"][selection[k]][j];
	    }
	data.push(item);
    }
    var previous = new Array(selection.length).fill(0);

    for (var j = 0; j < results["negative"].columns.length; j++){
	var item = [];
	for (var k = 0; k < selection.length; k++){
	    item.push([-previous[k] - results["negative"]["data"][selection[k]][j],-previous[k]]);
	    previous[k] = previous[k] + results["negative"]["data"][selection[k]][j];
	    }
	data.push(item);
    }

    var ymin = 0, ymax = 0;
    for (var k = 0; k < selection.length; k++){
	if(data[results["positive"].columns.length-1][k][1] > ymax){ ymax = data[results["positive"].columns.length-1][k][1];};
	if(data[results["positive"].columns.length+results["negative"].columns.length-1][k][0] < ymin){ ymin = data[results["positive"].columns.length+results["negative"].columns.length-1][k][0];};
    };

    y.domain([ymin,ymax]);
    yContext.domain([ymin,ymax]);

    var area = d3.area()
        .curve(d3.curveMonotoneX)
        .x(function(d,i) { return x(snapshots[i]); })
        .y0(function(d) { return y(d[0]); })
        .y1(function(d) { return y(d[1]); });

    var areaContext = d3.area()
        .curve(d3.curveMonotoneX)
        .x(function(d,i) { return xContext(snapshots[i]); })
        .y0(function(d) { return yContext(d[0]); })
        .y1(function(d) { return yContext(d[1]); });


    svgGraph.append("defs").append("clipPath")
        .attr("id", "clip")
	.append("rect")
        .attr("width", width)
        .attr("height", height);

    var focus = svgGraph.append("g")
        .attr("class", "focus")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var context = svgGraph.append("g")
        .attr("class", "context")
        .attr("transform", "translate(" + marginContext.left + "," + marginContext.top + ")");

    var layer = focus.selectAll(".layer")
        .data(data)
        .enter().append("g")
        .attr("class", "layer");

    layer.append("path")
        .attr("class", "area")
        .style("fill", function(d, i) {if(i < results["positive"].color.length){ return results["positive"].color[i];} else{return results["negative"].color[i-results["positive"].color.length];} })
        .attr("d", area);


    focus.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    focus.append("g")
        .attr("class", "axis axis--y")
        .call(yAxis);


    var label = svgGraph.append("g").attr("class", "y-label");

    // text label for the y axis
    label.append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 0)
        .attr("x",0 - (height / 2))
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .text("Power [MW]");


    var layerContext = context.selectAll(".layerContext")
        .data(data)
        .enter().append("g")
        .attr("class", "layerContext");

    layerContext.append("path")
        .attr("class", "area")
        .style("fill", function(d, i) {if(i < results["positive"].color.length){ return results["positive"].color[i];} else{return results["negative"].color[i-results["positive"].color.length];} })
        .attr("d", areaContext);

    context.append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + heightContext + ")")
        .call(xAxisContext);

    var gBrush = context.append("g")
        .attr("class", "brush")
        .call(brush);

    // brush handle follows
    // https://bl.ocks.org/Fil/2d43867ba1f36a05459c7113c7f6f98a

    // following handle looks nicer
    // https://bl.ocks.org/robyngit/89327a78e22d138cff19c6de7288c1cf

    var brushResizePath = function(d) {
	var e = +(d.type == "e"),
	    x = e ? 1 : -1,
	    y = heightContext / 2;
	return "M" + (.5 * x) + "," + y + "A6,6 0 0 " + e + " " + (6.5 * x) + "," + (y + 6) + "V" + (2 * y - 6) + "A6,6 0 0 " + e + " " + (.5 * x) + "," + (2 * y) + "Z" + "M" + (2.5 * x) + "," + (y + 8) + "V" + (2 * y - 8) + "M" + (4.5 * x) + "," + (y + 8) + "V" + (2 * y - 8);
    }

    var handle = gBrush.selectAll(".handle--custom")
	.data([{type: "w"}, {type: "e"}])
	.enter().append("path")
        .attr("class", "handle--custom")
        .attr("stroke", "#000")
        .attr("cursor", "ew-resize")
        .attr("d", brushResizePath);

    gBrush.call(brush.move, x.range()); //this sets initial position of brush


    svgGraph.append("rect")
        .attr("class", "zoom")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .call(zoom);

    function brushed() {
	if (d3.event.sourceEvent && d3.event.sourceEvent.type === "zoom") return; // ignore brush-by-zoom
	var s = d3.event.selection || xContext.range();
	x.domain(s.map(xContext.invert, xContext));
	layer.attr("d", area);
	focus.select(".axis--x").call(xAxis);
	svgGraph.select(".zoom").call(zoom.transform, d3.zoomIdentity
				      .scale(width / (s[1] - s[0]))
				      .translate(-s[0], 0));
	handle.attr("transform", function(d, i) { return "translate(" + [ s[i], - heightContext / 4] + ")"; });
    }

    function zoomed() {
	if (d3.event.sourceEvent && d3.event.sourceEvent.type === "brush") return; // ignore zoom-by-brush
	var t = d3.event.transform;
	x.domain(t.rescaleX(xContext).domain());
	layer.select(".area").attr("d", area);
	focus.select(".axis--x").call(xAxis);
	var newRange = x.range().map(t.invertX, t);
	context.select(".brush").call(brush.move, newRange);
	handle.attr("transform", function(d, i) { return "translate(" + [ newRange[i], - heightContext / 4] + ")"; });
    }


};



var jobid = scenarios[0];

var get_series = new XMLHttpRequest();

get_series.open('GET', '../series/' + jobid, true);

get_series.onload = function () {
    results = JSON.parse(this.response);
    status = results["status"];
    console.log("status is",status);

    if(status == "Error"){
	console.log("Failed with error",results["error"]);
    };
    if(status == "Success"){
	let snapshots = results["snapshots"];
	for(var j=0; j < snapshots.length; j++) {
	    snapshots[j] = parseDate(snapshots[j]);
	};
	for (var k=0; k < balances_selection.length; k++){
	    let balance = balances_selection[k];
	    console.log("Drawing power time series for", balance);
	    let series = results[balance];
	    draw_series(series, snapshots, balance);
	};
    };
};
get_series.send();
