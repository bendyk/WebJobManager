from server.task import Task

tasks = []

task1 = Task("mjob-tasks-js/mjob1.js", ["data"])
genFiles = ["data.arr1", "data.arr2"]
task1.output_files(genFiles)

task2 = Task("mjob-tasks-js/mjob2.js", [genFiles[0]])
task2.input_files([genFiles[0]])
sortFiles = ["data.srt1", "data.srt2"]
task2.output_files([sortFiles[0]])
task2.depends_on(task1)

task3 = Task("./mjob-tasks-js/mjob2.js", [genFiles[1]])
task3.input_files([genFiles[1]])
task3.output_files([sortFiles[1]])
task3.depends_on(task1)

task4 = Task("./mjob-tasks-js/mjob4.js", sortFiles)
task4.input_files(sortFiles)
task4.output_files(["./data.mrge"])
task4.depends_on(task2)
task4.depends_on(task3)

tasks.append(task1)
tasks.append(task2)
tasks.append(task3)
tasks.append(task4)

