function main(args){
  var data = FS.readFile(args[0]);
  var new_data = null;

  var blob_new = new Blob([data.buffer, data.buffer]);

  var f_reader = new FileReader();
  f_reader.onload = function(){
    new_data = this.result;
    FS.writeFile(args[1], new_data);
    exit();
  }
  f_reader.readAsArrayBuffer(blob_new);
}

