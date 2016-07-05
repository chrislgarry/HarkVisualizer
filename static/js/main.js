var durationRingChart = dc.pieChart("#chart-ring-duration"),
    speakersRowChart = dc.rowChart("#chart-row-speakers");

var xfilter = crossfilter(),
    durationDim = xfilter.dimension(function(d) {return Math.floor(+d.duration);}),
    azimuthDim = xfilter.dimension(function(d) {return Math.floor(+d.azimuth);}),
    guidDim  = xfilter.dimension(function(d) {return d.guid;}),
  
    durationPerAzim = azimuthDim.group().reduceSum(function(d) {return +d.duration;}),
    durationPerName = guidDim.group().reduceSum(function(d) {return +d.duration;});

function render_plots() {
    // Render the dashboards just before plots are rendered
    document.getElementById("processing_loader").style.visibility = "hidden";
    document.getElementsByClassName("left_dashboard")[0].style.visibility = "visible";
    document.getElementsByClassName("right_dashboard")[0].style.visibility = "visible";

    // Initialize and render plots
    durationRingChart
        .width(250).height(250)
        .dimension(azimuthDim)
        .group(durationPerAzim)
        .innerRadius(50)
        .colors(d3.scale.category10())
        .label(function(d) { return d.key + "\xB0"; });
    speakersRowChart
        .width(400).height(250)
        .dimension(guidDim)
        .group(durationPerName)
        .elasticX(true)
        .colors(d3.scale.category10());
    dc.renderAll();
}

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
var connection = new WebSocket("ws://harkvisualizer.com/websocket");

var rendered = false;
// When a socket message is received
connection.onmessage = function(event) {
    var message = JSON.parse(event.data);
    // If utterance is a context result
    if(message.guid){
        // Extract values and render in graph
        guid = message.guid;
        azimuth = message.azimuth;
        duration = message.duration;
        var updateObject =[{
            "guid": guid,
            "azimuth": azimuth,
            "duration": duration
        }];
        xfilter.add(updateObject);
        if(rendered) {
            dc.redrawAll();
        }
        else {
            render_plots();
            rendered = true;
        }
    }
    // Message is a chatbox entry
    else{
        document.getElementById("chart1loader").style.visibility = "hidden";
        document.getElementById("chart2loader").style.visibility = "hidden";

        // If it's a timestamp message, make it bold
        if(message.includes(":")) {
            text = document.createTextNode(message);
            chatbox = document.getElementById("chatbox");
            
            bold = document.createElement("b")
            bold.appendChild(text);
            chatbox.appendChild(bold);

            chatbox.appendChild(document.createElement("br"));
        }
        else {
            // If it's a transcription, 
            text = document.createTextNode(message);
            chatbox = document.getElementById("chatbox");

            chatbox.appendChild(text);
            chatbox.appendChild(document.createElement("br"));
            chatbox.appendChild(document.createElement("br"));
        }

        // Auto-scroll when a new message is printed
        chatbox.scrollTop = chatbox.scrollHeight;
    }
}

// On close, notify the user process complete
connection.onclose = function(event) {
    document.getElementById("layer_1").style.visibility = "hidden";
    rendered = false;
}