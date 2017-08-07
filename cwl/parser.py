try:
  from cwltool.load_tool import load_tool, fetch_document, validate_document
  from cwltool.resolver import tool_resolver
except:
  print("install cwltool for commonworkflowlanguage support")
  exit(-1)
import sys
sys.path.append("../")

from server.task import Task
class Parser:

  @staticmethod
  def parse_cwl(cwl_file):

    process_obj = None
    document_loader, workflowobj, uri = fetch_document(cwl_file, resolver=tool_resolver, fetcher_constructor=None)

    try:
      document_loader, avsc_names, process_obj, metada, uri \
        = validate_document(document_loader, 
                            workflowobj, 
                            uri, 
                            enable_dev=False, 
                            strict=True, 
                            preprocess_only=False,
                            fetcher_constructor=None)

    except ValueError:
      print("Syntax Error in CWL File: %s" % cwl_file)
      process_obj = None

    return process_obj       

  @staticmethod
  def parse_data(cwl_file):
    document_loader, workflowobj, uri = fetch_document(cwl_file, resolver=tool_resolver, fetcher_constructor=None)
    return workflowobj


class Workflow:

  def __init__(self, workflow_file, data_file=""):
    self.__steps   = {}
    self.__tasks   = {}
    self.__clts    = {}
    self.__inputs  = {}
    self.__outputs = {}

    wf_object = Parser.parse_cwl(workflow_file)
    if data_file:
      for key, data in Parser.parse_data(data_file).items():
        self.__outputs[key] = data
    
    self.__load_steps(wf_object) 


  def __load_clt(self, run_arg):

    if not run_arg.endswith(".cwl") : raise ValueError("Run argument must be a cwl file")

    clt = Parser.parse_cwl(run_arg)

    if not clt['class'] == "CommandLineTool" : raise ValueError("Run argument must be a CommandLineTool")

    return clt


  def __load_steps(self, wf_object):
    #TODO Add prefix handling
    if not (wf_object["class"] == "Workflow") : raise ValueError("Input file no workflow")
      
    for step in wf_object['steps']:
      identifier = step['id'].split("#")[-1]
      clt        = self.__load_clt(step['run'])
        
      args       = [""] * len(clt['inputs'])
      inputs     = []
      outputs    = []

      #get args and inputs
      for pos, ins in enumerate(clt['inputs']):
        pos    = ins['inputBinding']['position'] - 1 if 'position' in ins['inputBinding'] else len(args)
        arg_id = identifier + "/" + ins['id'].split("#")[-1]
        args.insert(pos, arg_id)
        if(ins['type'] == "File"): inputs.append(arg_id)

      for ins in step['in']:
        self.__inputs[ins['id'].split('#')[-1]] = ins['source'].split('#')[-1]


      #get outputs
      for outs in clt['outputs']:
        #TODO Handle others than glob
        out_id   = identifier + "/" + outs['id'].split('#')[-1]
        out_dest = identifier + "/" + outs['outputBinding']['glob']
        outputs.append(out_id)
        self.__outputs[out_id] = out_dest

      self.__steps[identifier] = {"executable": clt['baseCommand'] ,"args":args, "inputs":inputs, "outputs":outputs}
 


  def get_tasks(self):
    tasks        = {}
    dependencies = {}
    for identifier, step in self.__steps.items():
      args    = []
      inputs  = []
      outputs = []
      deps    = []

      for arg in step['args']:
        if arg in self.__inputs:
          if self.__inputs[arg] in self.__outputs:
            args.append(self.__outputs[self.__inputs[arg]])
          else:
            args.append(self.__inputs[arg])
        else:
          args.append(arg)

      for inp in step['inputs']:
        if self.__inputs[inp] in self.__outputs:
          inputs.append(self.__outputs[self.__inputs[inp]])
        else:
          inputs.append(self.__inputs[inp])
       
        if self.__inputs[inp].split("/")[0] in self.__steps:
          deps.append(self.__inputs[inp].split("/")[0])

      for out in step['outputs']:
        outputs.append(self.__outputs[out])         


      task = Task(step["executable"], args)
      task.input_files(inputs)
      task.output_files(outputs)
      
      tasks[identifier]                 = task
      if deps: dependencies[identifier] = deps

    for identifier in dependencies.keys():
      for dependency in dependencies[identifier]:
        tasks[identifier].depends_on(tasks[dependency])
    
    return tasks.values()
    
          

if __name__ == '__main__':
  wf    = Workflow("./mjob_example.cwl", "mjob_example.json") 
  tasks = wf.get_tasks()
  for task in tasks:
    print(task.executable)
    print(task.args)
    print(task.in_files)
    print(task.out_files)
    print(task.dependencies)
    print("------------------------------")
