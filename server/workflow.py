from util.cwl_parser import Parser
from server.task import Task
import re
import os

class Workflow:
  def __init__(self, workflow_path, workflow_file, data_file=""):
    self.__steps           = {}
    self.__tasks           = {}
    self.__clts            = {}
    self.__external_inputs = {}
    self.wf_path           = workflow_path

    if workflow_file:
      wf_object   = Parser.parse_cwl(workflow_file)
      data_object = None

      if data_file: data_object = Parser.parse_data(data_file)

      self.__load_ext_inputs(wf_object, data_object)
      self.__load_clts(wf_object)
      self.__load_steps(wf_object)
      self.__init_tasks()

    else:
      #if you didnt specified a workflow_file you've to set the tasks manually with set_tasks() 
      #(used for depricated workflow input syntax)
      pass


  def __load_ext_inputs(self, wf_object, data_object=None):

    for inp in wf_object['inputs']:
      input_obj             = type('',(),{})
      input_obj.identifier  = inp['id'].split("#")[-1]
      input_obj.cwl_type    = inp['type']
      input_obj.source_step = ""

      if data_object:
        if 'path' in data_object[input_obj.identifier]:
          input_obj.value = data_object[input_obj.identifier]['path'] 
        else: 
          input_obj.value = data_object[input_obj.identifier]

      self.__external_inputs[input_obj.identifier] = input_obj


  def __load_steps(self, wf_object):
    if not (wf_object["class"] == "Workflow") : raise ValueError("Input file no workflow")

    for step in wf_object['steps']:
      identifier = step['id'].split("#")[-1]
      self.__steps[identifier] = WorkflowStep(self.__clts[step['run']], step)


  def __load_clts(self, wf_object):
    # load all clts
    for step in wf_object['steps']:
      if not step['run'] in self.__clts:
        self.__clts[step['run']] = self.__parse_clt(step['run'])



  def __parse_clt(self, run_arg):

    if not run_arg.endswith(".cwl") : raise ValueError("Run argument must be a cwl file")
    clt = Parser.parse_cwl(run_arg)
    if not clt['class'] == "CommandLineTool" : raise ValueError("Run argument must be a CommandLineTool")

    return clt


  def __init_tasks(self):
    tasks        = {}
    dependencies = {}

    for identifier, step in self.__steps.items():
      args    = []
      inputs  = []
      outputs = []
      deps    = []
      
      step.resolve_references(self.__steps, self.__external_inputs)
      task = Task(step.command, step.get_sorted_arguments(), self.wf_path, identifier)     
      task.input_files(step.get_input_files())
      task.output_files(step.get_output_files())
      tasks[identifier] = task
      
    for step in self.__steps.values():
      for dep in step.dependencies:
        tasks[step.identifier].depends_on(tasks[dep])

    self.__tasks = tasks.values()


  def check_required_files(self):
    for inp in self.__external_inputs.values():
      if (inp.cwl_type == "File") and not (os.path.isfile("%s/%s" % (self.wf_path, inp.value))):
        return False
    return True


  def remaining_tasks(self):
    remaining = 0
    for task in self.__tasks:
      if not task.done:
        remaining += 1
    return remaining


  def get_free_task(self):
    for task in self.__tasks:
      if task.ready() and not task.done:
        return task
    return None


  def get_all_tasks(self):
    return self.__tasks


  def set_tasks(self, tasks):
    self.__tasks = tasks
    return self


class ParameterReference:

  def __init__(self, parameter, step_id):
    self.step       = step_id
    self.source     = parameter
    self.references = re.findall("\$\(([^\)]+)\)", parameter)
      

  def resolve(self, steps, externals):
      result = self.source

      for ref in self.references:
        [src, identifier] = ref.split(".")

        items = []
        if src == "inputs":
          items = steps[self.step].inputs
        elif src == "arguments":
          items = steps[self.step].arguments

        ref_value = items[identifier].resolve(steps, externals)

        result = result.replace("$(%s)" % ref, ref_value)

      return result


class SourceReference:

  def __init__(self, parameter):
    self.source = parameter
    tmp = parameter.split("/")
      
    self.reference = tmp[-1]
    self.step      = tmp[ 0] if len(tmp) > 1 else ""


  def resolve(self, steps, externals):
    result = ""

    if self.step:
      if self.reference in steps[self.step].inputs:
        result = steps[self.step].inputs[self.reference].resolve(steps, externals)
      elif self.reference in steps[self.step].outputs:
        result = steps[self.step].outputs[self.reference].resolve(steps, externals)
    else:
      if self.reference in externals:
        result = externals[self.reference].value
    return result 


 
class CWLInput:

  def __init__(self, clt_inp, wf_step):

    self.identifier = clt_inp['id'].split('#')[-1]
    self.cwl_type   = clt_inp['type']
    self.source     = ""
    self.value      = ""

    if 'inputBinding' in clt_inp:
      self.position = clt_inp['inputBinding']['position']-1 if 'position'  in clt_inp['inputBinding'] else -1
      self.prefix   = clt_inp['inputBinding']['prefix']     if 'prefix'    in clt_inp['inputBinding'] else ""    
      self.source   = clt_inp['inputBinding']['valueFrom']  if 'valueFrom' in clt_inp['inputBinding'] else ""

    self.reference = ParameterReference(self.source, wf_step['id'].split("#")[-1])

    for inp in wf_step['in']:

      if (self.identifier == inp['id'].split('/')[-1]) and not self.source:
        self.reference = SourceReference(inp['source'].split('#')[-1])


  def resolve(self, steps, externals):

    if not self.value: 
      self.value = self.reference.resolve(steps, externals)

    return self.value    


class CWLOutput:

  def __init__(self, clt_out, wf_step):
    self.identifier = clt_out['id'].split('#')[-1]
    self.cwl_type   = clt_out['type']
    self.source     = ""
    self.value      = ""

    self.reference = ParameterReference(clt_out['outputBinding']['glob'], wf_step['id'].split("#")[-1])


  def resolve(self, steps, externals):

    if not self.value:
      self.value = self.reference.resolve(steps, externals)    
 
    return self.value


class WorkflowStep:

  def __init__(self, clt, step):
    self.identifier   = step['id'].split("#")[-1] 
    self.command      = clt['baseCommand']
    self.arguments    = []
    self.inputs       = {}
    self.outputs      = {}
    self.dependencies = []
    self.step         = step
    self.parse_args(clt)
    self.parse_inputs(clt)
    self.parse_outputs(clt)


  def parse_args(self, clt):
    if not 'arguments' in clt: return

    for arg in clt['arguments']:
      if not arg.startswith("$("):
        self.arguments.append(arg)
      else:
        raise ValueError("reference in arguments not supported")


  def parse_inputs(self, clt):
    for inp in clt['inputs']:
      wf_in = CWLInput(inp, self.step)
      self.inputs[wf_in.identifier] = wf_in

      if wf_in.reference.step and not (wf_in.reference.step == self.identifier):
        self.dependencies.append(wf_in.reference.step)


  def parse_outputs(self, clt):
    for out in clt['outputs']:
      wf_out = CWLOutput(out, self.step)
      self.outputs[wf_out.identifier] = wf_out


  def resolve_references(self, wf_steps, ext_inputs):
    for inp in self.inputs.values():
      inp.resolve(wf_steps, ext_inputs)

    for out in self.outputs.values():
      out.resolve(wf_steps, ext_inputs)


  def get_sorted_arguments(self):
    args     = []
    tmp_args = [""] * len(self.inputs)

    for inp in self.inputs.values():
      if hasattr(inp, 'position'):
        if len(self.inputs) > inp.position > -1:
          tmp_args[inp.position] = [inp.prefix, inp.value]
        else:
          tmp_args.append([inp.prefix, inp.value])

    for arg in tmp_args:
      args.extend(arg)

    args.extend(self.arguments)
    return args


  def get_input_files(self):
    files = []
    for inp in self.inputs.values():
      if inp.cwl_type == "File":
        path = inp.reference.step if inp.reference.step else "."
        files.append(path + "/" + inp.value)

    return files


  def get_output_files(self):
    files = []
    for out in self.outputs.values():
      if out.cwl_type == "File":
        files.append(out.value)

    return files
