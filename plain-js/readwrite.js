function main(args) {
  var data = FS.readFile(args[0]);

  var blob_new = new Blob([data.buffer]);

  var f_reader = new FileReader();

  f_reader.onload = function(){
    var new_data = this.result;
    FS.writeFile(args[1], new_data);
    exit();
  }
  f_reader.readAsArrayBuffer(blob_new);
}

Module['Main']      = main;
Module['arguments'] = arguments;

function getUniqueRunDependency(id){
  return id;
}

function check_dependencies(){  
  if(dependencies == 0){
    clearInterval(prerun_interval);
    Module['Main'](Module['arguments']);
  }
}

function exit(){
  Module['postRun'](); 
}

var FS = {
  files     : {},
  writeFile : function (path, data, encoding){ this.files[path] = data; },
  readFile  : function (path, options){ return this.files[path]; }
};

var dependencies = 0;
Module['addRunDependency']    = function (id){dependencies++};
Module['removeRunDependency'] = function (id){dependencies--};
Module['preRun']();

var prerun_interval = setInterval(check_dependencies, 0);
