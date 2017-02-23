function get_edges(net){
	edges=[];
	for (var x in net.layer){
		if(!x.type=="ImageData"){
			if(x.bottom != x.top){
				var edge = {};
				edge.src = x.bottom;
				edge.dst = x.top;
				edges.push(edge);
			}
		}
	}
	net.edges = edges;
	return net;
}

function draw_graph(net){
	var g = new dagreD3.graphlib.Graph().setGraph({});
	var layers = net.layer;
	var edges = net.edges;

	layers.forEach(function(layer) { g.setNode(layer.name, { label: layer.label}); });
	// setting nodes

	edges.forEach(function(edge) { g.setEdge(edge.src,edge.dst); });
	// Setting edges

	net.layer.forEach(function(l)) {
		var ln = l.name;
		var node = g.node(ln);
		node.rx = node.ry = 3;
		var lt = l.type;
		if(lt=="ImageData"){
			node.style = "fill: ff0";
		}
		if(lt=="Convolution"){
			node.style = "fill: f70";
		}
		if(lt=="ReLU"){
			node.style = "fill: 770";
		}
		if(lt=="LRN"){
			node.style = "fill: 070";
		}
		if(lt=="Pooling"){
			node.style = "fill: 077";
		}
		if(lt=="Dropout"){
			node.style = "fill: 070";
		}
		if(lt=="FC"){
			node.style = "fill: 707";
		}
	}
	return g;
}

function updateGraph(g,net){
	var g = draw_graph(net);
	var svg = d3.select("svg"),
    inner = svg.select("g");

// Set up zoom support
var zoom = d3.behavior.zoom().on("zoom", function() {
      inner.attr("transform", "translate(" + d3.event.translate + ")" +
                                  "scale(" + d3.event.scale + ")");
    });
svg.call(zoom);

// Create the renderer
var render = new dagreD3.render();

// Run the renderer. This is what draws the final graph.
render(inner, g);

// Center the graph
var initialScale = 0.75;
zoom
  .translate([(svg.attr("width") - g.graph().width * initialScale) / 2, 20])
  .scale(initialScale)
  .event(svg);
svg.attr('height', g.graph().height * initialScale + 40);
}