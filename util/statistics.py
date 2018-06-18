class Statistics:

  @staticmethod
  def save_time_stats(f_name, done_tasks, workflow_start, workflow_end=0):
    lines        = []

    sums = { "mngr": 0, "mngr_sq": 0, "pre": 0, "pre_sq": 0, "main": 0, "main_sq": 0, "post": 0, "post_sq": 0, "worker": 0, "worker_sq": 0 }
    mins = { "mngr": 0xFFFFFFFF, "pre": 0xFFFFFFFF, "main": 0xFFFFFFFF, "post": 0xFFFFFFFF, "worker": 0xFFFFFFFF }
    maxs = { "mngr": 0, "pre": 0, "main": 0, "post": 0, "worker": 0 }
    means = { "mngr": 0, "pre": 0, "main": 0, "post": 0, "worker": 0 }
    stddev = { "mngr": 0, "pre": 0, "main": 0, "post": 0, "worker": 0 }

    last_task_stop = 0 # for workflow runtime

    lines.append("#task; task name; queue time (M); total (M); stage-in (W); mainrun (W); stage-out (W); total (W)")

    with open(f_name, "w") as f:
      for task_nr,task in enumerate(done_tasks):
        time_worker = task.pre_time + task.main_time + task.post_time

        line = []
        line.append(str(task_nr + 1))
        line.append(task.executable.split("/")[-1])
        line.append(str(task.wait_time))
        line.append(str(task.abs_time))
        line.append(str(task.pre_time))
        line.append(str(task.main_time))
        line.append(str(task.post_time))
        line.append(str(time_worker))
        lines.append("; ".join(line))

        sums["mngr"]  += task.abs_time
        sums["pre"]  += task.pre_time
        sums["main"] += task.main_time
        sums["post"] += task.post_time
        sums["worker"] += time_worker

        if task.abs_time < mins["mngr"]:
            mins["mngr"] = task.abs_time
        if task.pre_time < mins["pre"]:
            mins["pre"] = task.pre_time
        if task.main_time < mins["main"]:
            mins["main"] = task.main_time
        if task.post_time < mins["post"]:
            mins["post"] = task.post_time
        if time_worker < mins["worker"]:
            mins["worker"] = time_worker

        if task.abs_time > maxs["mngr"]:
            maxs["mngr"] = task.abs_time
        if task.pre_time > maxs["pre"]:
            maxs["pre"] = task.pre_time
        if task.main_time > maxs["main"]:
            maxs["main"] = task.main_time
        if task.post_time > maxs["post"]:
            maxs["post"] = task.post_time
        if time_worker > maxs["worker"]:
            maxs["worker"] = time_worker

        # for runtime calculation
        if task.abs_time_stop > last_task_stop:
            last_task_stop = task.abs_time_stop

      lines.append("")

      num_tasks = task_nr+1
      means["mngr"] = round(sums["mngr"] / num_tasks)
      means["pre"] = round(sums["pre"] / num_tasks)
      means["main"] = round(sums["main"] / num_tasks)
      means["post"] = round(sums["post"] / num_tasks)
      means["worker"] = round(sums["worker"] / num_tasks)

      # calculating std. dev.
      for task_nr,task in enumerate(done_tasks): 
        sums["mngr_sq"] += ( task.abs_time - means["mngr"] )**2
        sums["pre_sq"] += ( task.pre_time - means["pre"] )**2
        sums["main_sq"] += ( task.main_time - means["main"] )**2
        sums["post_sq"] += ( task.post_time - means["post"] )**2
        sums["worker_sq"] += ( time_worker - means["worker"] )**2

      stddev["mngr"] = ( sums["mngr_sq"] / (num_tasks - 1) )**0.5
      stddev["pre"] = ( sums["pre_sq"] / (num_tasks - 1) )**0.5
      stddev["main"] = ( sums["main_sq"] / (num_tasks - 1) )**0.5
      stddev["post"] = ( sums["post_sq"] / (num_tasks - 1) )**0.5
      stddev["worker"] = ( sums["worker_sq"] / (num_tasks - 1) )**0.5

      line = []
      line.append("sum;;")
      line.append(str(sums["mngr"]))
      line.append(str(sums["pre"]))
      line.append(str(sums["main"]))
      line.append(str(sums["post"]))
      line.append(str(sums["worker"]))
      lines.append("; ".join(line))

      line = []
      line.append("min;;")
      line.append(str(mins["mngr"]))
      line.append(str(mins["pre"]))
      line.append(str(mins["main"]))
      line.append(str(mins["post"]))
      line.append(str(mins["worker"]))
      lines.append("; ".join(line))

      line = []
      line.append("max;;")
      line.append(str(maxs["mngr"]))
      line.append(str(maxs["pre"]))
      line.append(str(maxs["main"]))
      line.append(str(maxs["post"]))
      line.append(str(maxs["worker"]))
      lines.append("; ".join(line))

      line = []
      line.append("std. dev.;;")
      line.append(str(round(stddev["mngr"], 2)))
      line.append(str(round(stddev["pre"], 2)))
      line.append(str(round(stddev["main"], 2)))
      line.append(str(round(stddev["post"], 2)))
      line.append(str(round(stddev["worker"], 2)))
      lines.append("; ".join(line))


      # calculate total workflow runtime
      if workflow_end != 0:
          last_task_stop = workflow_end
      runtime = int(round((last_task_stop - workflow_start) * 1000))
      lines.append("workflow runtime;;; " + str(runtime))

      f.write("\n".join(lines))
      f.write("\n")
