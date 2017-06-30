from server.task import Task

tasks = []

task1 = Task("./plainjs_test.js", ["aaa.in", "aaa.out"])
task1.input_files(["aaa.in"])
task1.output_files(["aaa.out"])

tasks.append(task1)


