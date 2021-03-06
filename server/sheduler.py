import time
from server.logging import Debug
from util.statistics import Statistics

class Sheduler:

  MINIMUM_MACHINES = 1
  workflows = []
  machines  = []

  @staticmethod
  def addWorkflow(workflow):
    Sheduler.workflows.append(workflow)


  @staticmethod
  def addMachine(machine):
    Sheduler.machines.append(machine)

  @staticmethod
  def removeMachine(machine):
    if machine in Sheduler.machines:
      Sheduler.machines.remove(machine)

  @staticmethod
  def wait_min_machines():
    if Sheduler.MINIMUM_MACHINES > 1:
      Debug.msg("Waiting for %d connected worker" % Sheduler.MINIMUM_MACHINES, ("SHEDULER", 1))

    wait_for_machines = True
    while wait_for_machines: # wait until enough machines are connected
      count_connected = Sheduler.count_machines()
      if count_connected >= Sheduler.MINIMUM_MACHINES:
        wait_for_machines = False
        Debug.msg("%d machines available" % count_connected, ("SHEDULER", 1))
      else:
        time.sleep(1)


  @staticmethod
  def count_machines():
    cnt = 0
    for m in Sheduler.machines:
      if (not m.is_busy()):
        cnt += 1
    return cnt


  @staticmethod
  def run():
    log_file = open("./workflow.log", "w")
    Sheduler.wait_min_machines()
    workflow_start_time = 0
    alltasksdone = False

    print(Sheduler.workflows)
    while True:
      alltasksdone = True
      for wf in Sheduler.workflows:
        if wf.remaining_tasks() > 0:
          alltasksdone = False
          task         = wf.get_free_task()
          if task:
            if wf.START_TIME == 0:
              wf.START_TIME = time.time()
            log_file.write(task.path + " executed\n")
            Sheduler.execute_task(task)
        else:
          tasks = wf.get_all_tasks()
          log_file.close()
          Debug.msg("WORKFLOW %s DONE" % wf.wf_path, ("SHEDULER",1))
          Statistics.save_time_stats("%s/task_times.stats" % wf.wf_path, tasks, wf.START_TIME, time.time())
          
          for machine in Sheduler.machines:
            while machine.is_busy():
              time.sleep(0.1)
            machine.clean_workflow_files(wf.wf_path)
          
          Sheduler.workflows.remove(wf) 
          
        time.sleep(0.1)
      time.sleep(0.1)

    tasks = Sheduler.workflows[0].get_all_tasks()
    Debug.msg("all TASKS done", ("SHEDULER",1))
    Statistics.save_time_stats("task_times.stats", tasks, workflow_start_time)


  @staticmethod
  def execute_task(task):
    started = False
    while not started:
      for machine in Sheduler.machines:
        if not machine.is_busy():
          machine.run_task(task)
          started = True
          break
      if started:
        break
      time.sleep(0.5)


  @staticmethod
  def check_file_transfer(task, path):
    return True
    if Sheduler.count_machines() == 1:
      return False
    else:
      return True
