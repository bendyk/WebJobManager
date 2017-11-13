import time

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
      print("Will wait until %d machines are connected" % Sheduler.MINIMUM_MACHINES)

    wait_for_machines = True
    while wait_for_machines: # wait until enough machines are connected
      count_connected = Sheduler.count_machines()
      if count_connected >= Sheduler.MINIMUM_MACHINES:
        wait_for_machines = False
        print("%d machines are ready." % count_connected)
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
    Sheduler.wait_min_machines()
    workflow_start_time = 0
    alltasksdone = False

    while True:
      alltasksdone = True
      for wf in Sheduler.workflows:
        if wf.remaining_tasks() > 0:
          alltasksdone = False
          task         = wf.get_free_task()
          if task:
            if workflow_start_time == 0:
              workflow_start_time = time.time()
            Sheduler.execute_task(task)
          
        time.sleep(1)

      if alltasksdone:
        for machine in Sheduler.machines:
          for wf in Sheduler.workflows:
            if not machine.is_busy():
              machine.clean_workflow_files(wf.wf_path)
            else:
              print("machine is busy")

    tasks = Sheduler.workflows[0].get_all_tasks()
    print("all tasks done.")
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

      time.sleep(1)


  @staticmethod
  def check_file_transfer(task, path):
    return False
    if Sheduler.count_machines() == 1:
      return False
    else:
      return True
