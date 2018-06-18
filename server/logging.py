class Debug:
  class ERROR:
    CONNECTION_LOST    = 0
    CONNECTION_REFUSED = 1

  def error(code, value):

    if code == ERROR.CONNECTION_LOST:
      print("ERROR: %s|%d: connection lost" % value)
    elif code == ERROR.CONNECTION_REFUSED:
      print("ERROR: %s|%d: connection refused" % value)


  def warn(msg, address = ("", 2)):
    pre_msg = "%s|%d WARNING: " % address
    print(pre_msg + msg)


  def log(msg, address=("",1)):
    pre_msg = "%s|%d LOG: " % address
    print(pre_msg + msg)

  def msg(msg, address=("", 0)):
    pre_msg = "%s|%d MESSAGE: " % address
    print(pre_msg + msg)


  def log_file(fname, content):
    with open(fname, "w") as f:

      if not type(content) is str:
        content = "\n".join(content)

      f.write(content)
