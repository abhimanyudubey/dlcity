function initNet(nname){
	var net = {};
	net.name = nname;
	net.layer = [];
	return net;
}

function net_addDataLayer(net,lparams){
	var layer = {};
	layer.name = "data";
	layer.type = "ImageData";
	layer.top = "data";
	layer.label = "data - image";
	layer.include = {};
	layer.include.phase = "TRAIN";
	layer.transform_param = "";
	layer.transform_param.mirror = "True";
	layer.transform_param.crop_size= "227";
	layer.transform_param.mean_file = lparams.mean_file;
	layer.data_param={};
	layer.data_param.source = lparams.train_source;
	layer.data_param.batch_size = lparams.train_batch_size;
	net.layer.push(layer);
	layer = {};
	layer.name = lname;
	layer.type = "ImageData";
	layer.top = "data";
	layer.label = "data - image";
	layer.include = {};
	layer.include.phase = "TEST";
	layer.transform_param = "";
	layer.transform_param.mirror = "True";
	layer.transform_param.crop_size= "227";
	layer.transform_param.mean_file = lparams.mean_file;
	layer.data_param={};
	layer.data_param.source = lparams.test_source;
	layer.data_param.batch_size = lparams.test_batch_size;
	net.layer.push(layer);
	return net;
}

function net_addConvLayer(net,lname,lbottom,lparams){
	var layer = {};
	layer.name = lname;
	layer.type = "Convolution";
	layer.top = lname;
	layer.bottom = lbottom;
	layer.convolution_param={};
	layer.convolution_param.num_output = lparams.num_output;
	layer.convolution_param.kernel_size = lparams.kernel_size;
	layer.convolution_param.stride = lparams.stride;
	layer.label=num_outputs+"x"+kernel_size+"x"+kernel_size+" Convolution";
	net.layer.push(layer);
	return net;
}

function net_addRELULayer(net,lname,ltarget){
	var layer = {};
	layer.name = lname;
	layer.type = "ReLU";
	layer.top = ltarget;
	layer.bottom = ltarget;
	layer.label = "RELU";
	net.layer.push(layer);
	return net;
}

function net_addNormLayer(net,lname,lbottom,lparams){
	var layer = {};
	layer.name = lname;
	layer.type = "LRN";
	layer.top = lname;
	layer.bottom = lbottom;
	layer.label = "LRN";
	layer.lrn_param={};
	layer.lrn_param.local_size = lparams.local_size;
	layer.lrn_param.alpha = lparams.alpha;
	layer.lrn_param.beta = lparams.beta;
	net.layer.push(layer);
	return net;
}


function net_addPoolLayer(net,lname,lbottom,lparams){
	var layer = {};
	layer.name = lname;
	layer.type = "Pooling";
	layer.top = lname;
	layer.bottom = lbottom;
	layer.pooling_param={};
	layer.pooling_param.pool = lparams.pool;
	layer.pooling_param.kernel_size = lparams.kernel_size;
	layer.pooling_param.stride = lparams.stride;
	layer.label = kernel_size+"x"+kernel_size+"x"+" Pooling";
	net.layer.push(layer);
	return net;
}

function net_addDropoutLayer(net,lname,ltarget,ratio){
	var layer = {};
	layer.name = lname;
	layer.type = "Dropout";
	layer.top = ltarget;
	layer.bottom = ltarget;
	layer.dropout_param={};
	layer.dropout_param.dropout_ratio = ratio;
	layer.label = ratio+" Dropout";
	net.layer.push(layer);
	return net;
}

function net_addFCLayer(net,lname,lbottom,lparams){
	var layer = {};
	layer.name = lname;
	layer.type = "FC";
	layer.top = lname;
	layer.bottom = lbottom;
	layer.inner_product_param = {};
	layer.inner_product_param.num_output = lparams.num_output;
	layer.label = num_output+" fully connected";
	net.layer.push(layer);
	return net;
}

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
	if(!edges==[]){
		edges.forEach(function(edge) { g.setEdge(edge.src,edge.dst); });
	}
	// Setting edges

	// net.layer.forEach(function(l)){
	// 	var ln = l.name;
	// 	var node = g.node(ln);
	// 	node.rx = node.ry = 3;
	// 	var lt = l.type;
	// 	if(lt=="ImageData"){
	// 		node.style = "fill: ff0";
	// 	}
	// 	if(lt=="Convolution"){
	// 		node.style = "fill: f70";
	// 	}
	// 	if(lt=="ReLU"){
	// 		node.style = "fill: 770";
	// 	}
	// 	if(lt=="LRN"){
	// 		node.style = "fill: 070";
	// 	}
	// 	if(lt=="Pooling"){
	// 		node.style = "fill: 077";
	// 	}
	// 	if(lt=="Dropout"){
	// 		node.style = "fill: 070";
	// 	}
	// 	if(lt=="FC"){
	// 		node.style = "fill: 707";
	// 	}
	// }
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
return g;
}

function initLayerArea(){
	choice = document.getElementById("layerChoice").value;
	if(choice=="ImageData"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Mean File:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='file' id='mean_file' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Training File:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='file' id='train_source' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Train Batchsize:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='train_batch_size' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Test File:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='file' id='test_source' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Test Batchsize:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='test_batch_size' width='100'/><br/>";
	}
	if(choice=="Convolution"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Layer Name:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lname' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Bottom Layer:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lbottom' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Number of Filters:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='num_output' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Kernel Size:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='kernel_size' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Stride:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='stride' width='100'/><br/>";
	}

	if(choice=="ReLU"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Layer Name:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lname' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Target Layer:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='ltarget' width='100'/><br/>";
	}

	if(choice=="LRN"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Layer Name:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lname' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Bottom Layer:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lbottom' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Local Size:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='local_size' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Beta:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='beta' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Alpha:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='alpha' width='100'/><br/>";
	}
		if(choice=="Pooling"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Layer Name:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lname' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Bottom Layer:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lbottom' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Pooling Type:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='pool' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Kernel Size:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='kernel_size' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Stride:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='stride' width='100'/><br/>";
	}
	if(choice=="Dropout"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Layer Name:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lname' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Target Layer:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='ltarget' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Ratio:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='ratio' width='100'/><br/>";
	}
	if(choice=="FC"){
		document.getElementById("layerArea").innerHTML="";
		document.getElementById("layerArea").innerHTML+="Enter Layer Name:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lname' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Bottom Layer:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='lbottom' width='100'/><br/>";
		document.getElementById("layerArea").innerHTML+="Enter Num Output:<br/>";
		document.getElementById("layerArea").innerHTML+="<input type='text' id='num_output' width='100'/><br/>";
	}
	document.getElementById("layerArea").innerHTML+="<button onclick='addLayer(g,net,"+choice+")'>Add Layer</button>";
}

function addLayer(g,net,choice){
	if(choice=="ImageData"){
		var lparams = {};
		lparams.mean_file = document.getElementById("mean_file").value;
		lparams.train_source = document.getElementById("train_source").value;
		lparams.train_batch_size = document.getElementById("train_batch_size").value;
		lparams.test_source = document.getElementById("test_source").value;
		lparams.test_batch_size= document.getElementById("test_batch_size").value;
		console.log(lparams);
		net = net_addDataLayer(net,lparams);
	}
	if(choice=="Convolution"){
		var lparams = {};
		var lname = document.getElementById("lname").value;
		var lbottom = document.getElementById("lbottom").value;
		lparams.num_output = document.getElementById("num_output").value;
		lparams.kernel_size = document.getElementById("kernel_size").value;
		lparams.stride= document.getElementById("stride").value;
		net = net_addConvLayer(net,lname,lbottom,lparams);
	}

	if(choice=="ReLU"){
		var lparams = {};
		var lname = document.getElementById("lname").value;
		var ltarget = document.getElementById("ltarget").value;
		net = net_addRELULayer(net,lname,ltarget);
	}

	if(choice=="LRN"){
		var lparams = {};
		var lname = document.getElementById("lname").value;
		var lbottom = document.getElementById("lbottom").value;
		lparams.local_size = document.getElementById("kernel_size").value;
		lparams.alpha = document.getElementById("alpha").value;
		lparams.beta = document.getElementById("beta").value;
		net = net_addLRNLayer(net,lname,lbottom,lparams);
	}
		if(choice=="Pooling"){
		var lparams = {};
		var lname = document.getElementById("lname").value;
		var lbottom = document.getElementById("lbottom").value;
		lparams.pool = document.getElementById("pool").value;
		lparams.kernel_size = document.getElementById("kernel_size").value;
		lparams.stride = document.getElementById("stride").value;
		net = net_addPoolLayer(net,lname,lbottom,lparams);
	}
	if(choice=="Dropout"){
		var lname = document.getElementById("lname").value;
		var ltarget = document.getElementById("ltarget").value;
		var ratio = document.getElementById("ratio").value;
		net = net_addDropoutLayer(net,lname,ltarget,ratio);
	}
	if(choice=="FC"){
		var lparams = {};
		var lname = document.getElementById("lname").value;
		var lbottom = document.getElementById("lbottom").value;
		lparams.num_output = document.getElementById("num_output").value;
		net = net_addFCLayer(net,lname,lbottom,lparams);
	}
	document.getElementById("layerArea").innerHTML="";
	document.getElementById("layerArea").innerHTML+='Layer Type:<select id="layerChoice"><option value="ImageData">ImageData</option><option value="Convolution" selected="selected">Convolution</option><option value="ReLU">ReLU</option><option value="LRN">LRN</option><option value="Pooling">Pooling</option> <option value="Dropout">Dropout</option><option value="FC">FC</option></select><br/><button onclick="initLayerArea()">Add Layer</button><br/>';
	document.getElementById("layerArea").innerHTML+=net.layer;
	document.getElementById("layerArea").innerHTML+=g;
	g = updateGraph(g,net);

}


    var net = initNet('AlexNet');

    var g = draw_graph(net);
    if(!(net.layer.length==0)){



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