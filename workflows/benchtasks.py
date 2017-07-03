from server.task import Task

tasks = []

# execute empty task
empty = Task("benchtasks-js/emptytask.js", [])
#empty.input_files()
#empty.output_files()
tasks.append(empty)

# transfer empty file and execute task
task1 = Task("benchtasks-js/exampletask.js", ["k", "nothing.dat", "out.dat"])
task1.input_files(["nothing.dat"])
task1.output_files(["out.dat"])
#tasks.append(task1)

#task2.depends_on(task1)
