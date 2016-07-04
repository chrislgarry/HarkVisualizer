var durationRingChart = dc.pieChart("#chart-ring-duration"),
    speakersRowChart = dc.rowChart("#chart-row-speakers");

var xfilter = crossfilter(),
    durationDim = xfilter.dimension(function(d) {return Math.floor(+d.duration);}),
    azimuthDim = xfilter.dimension(function(d) {return Math.floor(+d.azimuth);}),
    guidDim  = xfilter.dimension(function(d) {return d.guid;}),
  
    durationPerAzim = azimuthDim.group().reduceSum(function(d) {return +d.duration;}),
    durationPerName = guidDim.group().reduceSum(function(d) {return +d.duration;});

function render_plots(){
    durationRingChart
        .width(250).height(250)
        .dimension(azimuthDim)
        .group(durationPerAzim)
        .innerRadius(50)
        .colors(d3.scale.category10())
        .label(function(d) { return d.key + "\xB0"; })
        .renderTitle(true);
    speakersRowChart
        .width(400).height(250)
        .dimension(guidDim)
        .group(durationPerName)
        .elasticX(true)
        .colors(d3.scale.category10())
    dc.renderAll();
}

render_plots();

// Resets the graphs
function resetData() {
    var durationChartFilters = durationRingChart.filters();
    var speakerChartFilters = speakersRowChart.filters();
    durationRingChart.filter(null);
    speakersRowChart.filter(null);
    xfilter.remove();
    durationRingChart.filter([durationChartFilters]);
    speakersRowChart.filter([speakerChartFilters]);
}

// Set the chatbox to scroll overflow when text exceeds element size
document.getElementById("chatbox").style.overflow = "scroll";

// Connect to the remote websocket server
var connection = new WebSocket('ws://harkvisualizer.com/websocket');

// When a socket message is received
connection.onmessage = function(event) {
    var message = JSON.parse(event.data);
    // If utterance is a context result
    if(message.guid){
        // Extract values and render in graph
        guid = message.guid
        azimuth = message.azimuth
        duration = message.duration
        var updateObject =[{
            "guid": guid,
            "azimuth": azimuth,
            "duration": duration
        }]
        xfilter.add(updateObject);
        dc.redrawAll();
    }
    // Message is a transcription 
    else{
        // Render transcription in chat box
        document.getElementById('chatbox').innerHTML += "<p id=\"message\">" + message + "</p>";
    }
}

// On close, notify the user process complete
connection.onclose = function(event) {
    alert('Processing complete.');
}