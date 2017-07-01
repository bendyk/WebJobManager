class Statistics:

  @staticmethod
  def save_time_stats(f_name, done_tasks):
    lines    = []
    sum_abs  = 0
    sum_pre  = 0
    sum_main = 0
    sum_post = 0
    sum_wait = 0
    lines.append("#nr  #task_name          #absolute #prerun #mainrun #postrun #time in queue")
 

    with open(f_name, "w") as f:
      for task_nr,task in enumerate(done_tasks):
        line = []
        line.append((str(task_nr)).ljust(5))
        line.append(task.executable.split("/")[-1].ljust(20))
        line.append((str(task.abs_time)).ljust(10))
        line.append((str(task.pre_time)).ljust(8))
        line.append((str(task.main_time)).ljust(9))
        line.append((str(task.post_time)).ljust(9))
        line.append((str(task.wait_time)).ljust(9))
        lines.append("".join(line))

        sum_abs  += task.abs_time
        sum_pre  += task.pre_time
        sum_main += task.main_time
        sum_post += task.post_time
        sum_wait += task.wait_time

      lines.append("")

      line = []
      line.append("sum".ljust(25))
      line.append((str(sum_abs)).ljust(10))
      line.append((str(sum_pre)).ljust(8))
      line.append((str(sum_main)).ljust(9))
      line.append((str(sum_post)).ljust(9))
      line.append((str(sum_wait)).ljust(9))
      lines.append("".join(line))

      f.write("\n".join(lines))
      f.write("\n")
