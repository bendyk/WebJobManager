function main(args) {
	exit();
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
