
class Machine:


    def __init__(self, connection):
        self.connection = connection
        self.__busy     = False


    def run_task(self, task):
        self.task   = task
        self.__busy = True
        self.task.start(self.connection)
        print("Machine: Assigned task %s." % task.executable)


    def is_busy(self):
        if self.__busy:
            self.__busy = False if self.task.done else self.__busy

        return self.__busy
