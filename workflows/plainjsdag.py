from server.task import Task

tasks = []

# read input file and output it again without any modifications
task1 = Task("plain-js/readwrite.js", ["plainjs.in", "plainjs.out"])
task1.input_files(["plainjs.in"])
task1.output_files(["plainjs.out"])

tasks.append(task1)

# a tasks that does nothing at all
empty = Task("plain-js/emptytask.js", [])
#tasks.append(empty)
