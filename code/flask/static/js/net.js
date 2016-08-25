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
