var toDate = new Date()
var to_date = ""
var from_date = ""
var avg = ""
var tags = ""

var dataPointsST = null;
var dataPointsTH = null;
var dataPointsLT = null;
var dataPointsCL = null;
var dataPointsRetro = null;
var dataPointsAPR = null;

var farolST = 0
var farolTH = 0
var farolLT = 0
var farolCL = 0
var farolRetro = 0
var farolAPR = 0

function addData(data) {
	addDataST(data)
	addDataCL(data)
	addDataTH(data)
	addDataLT(data)
}

function addDataST(data) {
	var dpt = data.throughput;
	var dpl = data.leadtime;
	var squadName = data['self.repo.ghrepo']
	
	var tp = dpt[toDate.toISOString().split('T')[0]]
	var lt = dpl[toDate.toISOString().split('T')[0]]

	var cftp = 100 * ( tp[0][1] / tp[0][0] )
	var cflt = 100 * ( lt[0][1] / lt[0][0] )

	var keys = Object.keys(dpl);
	keys.sort();
	dflt = 0
	for (var i = 0; i < keys.length; i++) {
		if (dpl[keys[i]].length > 1){
			dflt += 1 	
		}
	}
	dflt = (dflt / keys.length) * 100

	if (!isNaN(cftp) && !isNaN(cflt)){
		dataPointsST.push({
			x: parseInt(cftp),
			y: parseInt(cflt),
			z: parseInt(dflt),
			name: squadName
		});		
	}

	farolST = farolST - 1

	if (farolST == 0){
		var chartThr = new CanvasJS.Chart("chartContainerST", {
			animationEnabled: true,
			zoomEnabled: true,
			theme: "dark1",
			title: {
				text: "Stability"
			},
			axisY: {
				title: "Coefficient of variation - Leadtime",
				labelFontSize: 10,
				minimum: 0,
				stripLines: [{
					lineDashType: "dot",
					value: 150,
					label: "Ideal",
					labelFontColor: "#808080",
					labelAlign: "near"
				}]
			},
			axisX: {
				title: "Coefficient of variation - Throughput",
				suffix: "%",
				labelFontSize: 10,
				minimum: 0,
				stripLines: [{
					value: 150,
					lineDashType: "dot",
					label: "Ideal",
					labelFontColor: "#808080",
					labelAlign: "near"
				}]
			},
			data: [{
				type: "bubble",
				indexLabel: "{name}",
				indexLabelPlacement: "outside",  
				indexLabelFontSize: 10,
				dataPoints: dataPointsST,
				toolTipContent: "<b>{name}</b><br/>Coef Var TH: {x}%<br/>Coef Var LT: {y}%<br/>Delivery rate: {z}% days"
			}]
		});

		chartThr.render();
	}
}

function addTeamsTableDownload(){
	dataDownload = {};
	
	title=['squad','cvthroughput','cvleadtime','dtretro','dtapr']
	dataPointsST.forEach(function(rowArray){
		dataDownload[rowArray.name] = {
			'squad': rowArray.name, 
			'cvthroughput': rowArray.x.toString(), 
			'cvleadtime': rowArray.y.toString()
		}
	});
	
	dataPointsRetro.forEach(function(rowArray){
		if (dataDownload[rowArray.name] != null){
			dataDownload[rowArray.name]['dtretro'] = rowArray.dt
		}
	});

	dataPointsAPR.forEach(function(rowArray){
		if (dataDownload[rowArray.name] != null){
			dataDownload[rowArray.name]['dtapr'] = rowArray.dt
		}
	});

	if (dataPointsCL != null)
	dataPointsCL.forEach(function(rowArray){
		title.push(rowArray['name']);
		rowArray.dataPoints.forEach(function(row2Array){
			dataDownload[row2Array.name][rowArray['name']]=row2Array.y.toString();
		});
	});

	let csvContent = "data:text/csv;charset=utf-8,";
	csvContent += title + "\r\n";	
	var keys = Object.keys(dataDownload);
	keys.sort();
	for (var i = 0; i < keys.length; i++) {
		values =[]
		title.forEach(function(rowArray){
			values.push(dataDownload[keys[i]][rowArray])
		});
		csvContent += values + "\r\n";	
	}
	
	var encodedUri = encodeURI(csvContent);
	window.open(encodedUri);
}

function addDataCL(data) {
	var titles = data.tagsTitles;
	if (titles.length > 0){
		document.getElementById("chartContainerCL").style.display = "block";
	}else{
		document.getElementById("chartContainerCL").style.display = "none";
		dataPointsCL=null;
	}
	var dps = data.throughput;
	var keys = Object.keys(dps);
	keys.sort();
	key = keys[keys.length - 1]

	if (dataPointsCL.length == 0){
		for (var i = 0; i < titles.length; i++) {
			dataPointsCL.push({
				type: "stackedColumn100",
				name: titles[i],
				showInLegend: "true",
				markerSize: 0,
				dataPoints: []
			})
		}
	}

	if (dps[key][0][0] > 0){
		for (var j = 0; j < titles.length; j++) {
			dataPointsCL[j].dataPoints.push({
				//x: farolCL,
				y: dps[key][2][j],
				name: data['self.repo.ghrepo'],
				title: titles[j]
			});
		}
	}


	farolCL = farolCL - 1

	if (farolCL == 0){
		var chartLoad = new CanvasJS.Chart("chartContainerCL", {
			animationEnabled: true,
			theme: "dark1",
			zoomEnabled: true,
			toolTip:{			 
					content: "<b>{title}:<b> #percent %"
					//shared: true
			},
			title: {
				text: "Charge Load"
			},
			axisY: {
				title: "Work %",
				titleFontSize: 24,
				crosshair: {
					enabled: true
				}
			},
			axisX: {
				crosshair: {
					enabled: true,
					snapToDataPoint: true
				},
				labelAngle: 270,
				labelFontSize: 15,
				interval: 1,
				labelFormatter: function ( e ) {
					if (e.chart.data[0].dataPoints[e.value] != null){
						return e.chart.data[0].dataPoints[e.value].name;
					} else {
						return e.value	
					}
				}
			},
			data: dataPointsCL
		});

		chartLoad.render();
	}
}

function addDataTH(data) {
	var squadName = data['self.repo.ghrepo']
	var dps = data.throughput;

	var keys = Object.keys(dps);
	keys.sort();
	var yRec = [null, null, null, null]
	for (var i = 0; i < keys.length; i++) {
		rec = dps[keys[i]]

		if (yRec[0] == null){
			yRec[0] = rec[0][0]
		}

		if ((yRec[1] == null) || (rec[0][0] >= yRec[1])){
			yRec[1] = rec[0][0]
		}

		if ((yRec[2] == null) || (rec[0][0] <= yRec[2])){
			yRec[2] = rec[0][0]
		}

		if (i == (keys.length - 1)){
			yRec[3] = rec[0][0]
		}
	}

	farolTH = farolTH - 1

	if (yRec[0]!=0 || yRec[1]!=0 || yRec[2]!=0 || yRec[3]!=0){
		dataPointsTH.push({
			//x: farolTH,
			y: yRec,
			name: squadName
		});
	}

	if (farolTH == 0){
		var chartThr = new CanvasJS.Chart("chartContainerTH", {
			animationEnabled: true,
			theme: "dark1",
			title: {
				text: "Throughput"
			},
			axisX: {
				labelAngle: 270,
				labelFontSize: 15,
				interval: 1,
				labelFormatter: function ( e ) {
					if (e.chart.data[0].dataPoints[e.value] != null){
						return e.chart.data[0].dataPoints[e.value].name;
					} else {
						return e.value	
					}
				} 
			},
			toolTip: {
				content: "<strong>{name}</strong><br>Open: {y[0]}<br>High: {y[1]}<br>Low: {y[2]}<br>Close: {y[3]}"
			},
			data: [{
				type: "candlestick",
				yValueFormatString: "##0.00",
				risingColor: "green",
				fallingColor: "red",
				color: "white",
				dataPoints: dataPointsTH
			}]
		});

		chartThr.render();
	}
}


function addDataLT(data) {
	var squadName = data['self.repo.ghrepo']
	var dps = data.leadtime;

	var keys = Object.keys(dps);
	keys.sort();
	var yRec = [null, null, null, null]
	for (var i = 0; i < keys.length; i++) {
		rec = dps[keys[i]]

		if (yRec[0] == null){
			yRec[0] = rec[0][0]
		}

		if ((yRec[1] == null) || (rec[0][0] >= yRec[1])){
			yRec[1] = rec[0][0]
		}

		if ((yRec[2] == null) || (rec[0][0] <= yRec[2])){
			yRec[2] = rec[0][0]
		}

		if (i == (keys.length - 1)){
			yRec[3] = rec[0][0]
		}
	}

	farolLT = farolLT - 1

	if (yRec[0]!=null || yRec[1]!=null || yRec[2]!=null || yRec[3]!=null){
		dataPointsLT.push({
			//x: farolTH,
			y: yRec,
			name: squadName
		});
	}

	if (farolLT == 0){
		var chartThr = new CanvasJS.Chart("chartContainerLT", {
			animationEnabled: true,
			theme: "dark1",
			title: {
				text: "Leadtime"
			},
			axisX: {
				labelAngle: 270,
				labelFontSize: 15,
				interval: 1,
				labelFormatter: function ( e ) {
					if (e.chart.data[0].dataPoints[e.value] != null){
						return e.chart.data[0].dataPoints[e.value].name;
					} else {
						return e.value	
					}
				} 
			},
			toolTip: {
				content: "<strong>{name}</strong><br>Open: {y[0]}<br>High: {y[1]}<br>Low: {y[2]}<br>Close: {y[3]}"
			},
			data: [{
				type: "candlestick",
				yValueFormatString: "##0.00",
				risingColor: "red",
				fallingColor: "green",
				color: "white",
				dataPoints: dataPointsLT
			}]
		});

		chartThr.render();
	}
}

function addDataRetro(data) {
	var ret = data['retros'];

	if (ret != null){
		var keys = Object.keys(ret);
		keys.sort();

		if (keys.length > 0){
			key = keys[keys.length - 1]
			dt1 = new Date(key + ' 12:00:00')
			dt2 = new Date()

			var timeDiff = Math.abs(dt1.getTime() - dt2.getTime());
			var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 

			dataPointsRetro.push({
				y: diffDays, 
				name: data['self.repo.ghrepo'], 
				dt: key
			})
		}
	}

	farolRetro = farolRetro - 1

	if (farolRetro == 0){
		var chartRetro = new CanvasJS.Chart("chartContainerRetro", {
			animationEnabled: true,
			theme: "dark1",
			title: {
				text: "Retrospective"
			},
			axisX: {
				labelAngle: 270,
				labelFontSize: 15,
				interval: 1,
				labelFormatter: function ( e ) {
					if (e.chart.data[0].dataPoints[e.value] != null){
						return e.chart.data[0].dataPoints[e.value].name;
					} else {
						return e.value	
					}
				} 
			},
			data: [{
				type: "column",
				dataPoints: dataPointsRetro,
				showInLegend: true, 
				markerSize: 0,
				showInLegend: false, 
				legendText: "days since last retrospective"
			}]
		});

		chartRetro.render();
	}
}

function addDataAPR(data) {
	var ret = data['aprs'];

	if (ret != null){
		var keys = Object.keys(ret);
		keys.sort();

		if (keys.length > 0){
			key = keys[keys.length - 1]
			dt1 = new Date(key + ' 12:00:00')
			dt2 = new Date()

			var timeDiff = Math.abs(dt1.getTime() - dt2.getTime());
			var diffDays = Math.ceil(timeDiff / (1000 * 3600 * 24)); 

			dataPointsAPR.push({
				y: diffDays, 
				name: data['self.repo.ghrepo'], 
				dt: key
			})
		}
	}

	farolAPR = farolAPR - 1

	if (farolAPR == 0){
		var chartApr = new CanvasJS.Chart("chartContainerApr", {
			animationEnabled: true,
			theme: "dark1",
			title: {
				text: "APR"
			},
			axisX: {
				labelAngle: 270,
				labelFontSize: 15,
				interval: 1,
				labelFormatter: function ( e ) {
					if (e.chart.data[0].dataPoints[e.value] != null){
						return e.chart.data[0].dataPoints[e.value].name;
					} else {
						return e.value	
					}
				} 
			},
			data: [{
				type: "column",
				dataPoints: dataPointsAPR,
				showInLegend: true, 
				markerSize: 0,
				showInLegend: false, 
				legendText: "days since last retrospective"
			}]
		});

		chartApr.render();
	}
}

function getRepos(data) {
	if ($("#toDate").val() != ""){
		to_date = "&to_date=" + $("#toDate").val();
		toDate = new Date($("#toDate").val())
	}
	if ($("#average").val() != "" && !isNaN($("#average").val())){
		average =  $("#average").val()
		avg = "&average=" + average;
		fromDate = new Date(toDate)
		from_date = "&from_date=" + new Date(fromDate.setDate(fromDate.getDate() - parseInt(average))).toISOString().split('T')[0];
	}
	var val = [];
	$(".tags:checked").each(function(i){
	   val[i] = $(this).val();
	});
	if (val.length > 0){
		tags = '&tags=' + val.toString()
	}else{
		var tags = ""	
	}

	dataPointsST = [];
	dataPointsTH = [];
	dataPointsLT = [];
	dataPointsCL = [];
	dataPointsRetro = [];
	dataPointsAPR = [];

	farolST = data['repos'].length;
	farolTH = data['repos'].length;
	farolLT = data['repos'].length;
	farolCL = data['repos'].length;
	farolRetro = data['repos'].length;
	farolAPR = data['repos'].length;

	for (var i = 0; i < data['repos'].length; i++) {
		url = "https://cxiew7bdgh.execute-api.us-east-1.amazonaws.com/agile/prod-agile-professor-hubert?source=html&action=closed_issues&squad-repo=" 
			+ data['repos'][i] + to_date + from_date + avg + tags;

		$.getJSON(url, addData);
	}

	for (var i = 0; i < data['repos'].length; i++) {
		url = "https://cxiew7bdgh.execute-api.us-east-1.amazonaws.com/agile/prod-agile-professor-hubert?source=html&action=get_retro&squad-repo=" 
			+ data['repos'][i] + to_date;

		$.getJSON(url, addDataRetro);
	}

	for (var i = 0; i < data['repos'].length; i++) {
		url = "https://cxiew7bdgh.execute-api.us-east-1.amazonaws.com/agile/prod-agile-professor-hubert?source=html&action=get_apr&squad-repo=" 
			+ data['repos'][i] + to_date;

		$.getJSON(url, addDataAPR);
	}
}

function printChart(data) {
	url = "https://cxiew7bdgh.execute-api.us-east-1.amazonaws.com/agile/prod-agile-professor-hubert?source=html&action=get_repos&squad-repo=";
	$.getJSON(url, getRepos);
}