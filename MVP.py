import requests
import subprocess
import time
import threading
Servers = []

def GetCarbonStatus():
    url = "https://api.carbonintensity.org.uk/intensity"
    response = requests.get(url)
    if response.status_code == 200:
        carbonstatus = response.json()['data'][0]['intensity']['index']
    else:
        carbonstatus = None
    return carbonstatus


class Server:
  def __init__(self, Name, IP):
    self.Name = Name
    self.IP = IP
    self.TaskQueue = []
    self.CurrentTask = None
  def AddTask(self, Task):
    self.TaskQueue.append(Task)
  def GetTasks(self):
    return self.TaskQueue
  def RunTaskAsync(self):
    thread = threading.Thread(target=self.RunTask)
    thread.start()
  def RunTask(self):
    if len(self.TaskQueue) == 0:
      return
    if self.CurrentTask:
      return
    if GetCarbonStatus() != "low":
      self.CurrentTask = self.TaskQueue.pop()
      self.CurrentTask.Execute()
      self.CurrentTask = None
      self.RunTask()

class Task:
  def __init__(self, Name, Description, Path, Executable):
    self.Name = Name
    self.Description = Description
    self.Path = Path
    self.Executable = Executable
    self.Running = False
    self.Process = None
  def Execute(self):
    self.Running = True
    self.Process = subprocess.Popen(self.Path + "/" + self.Executable, shell=True) # TODO: Add SSH capability here
    self.Process.wait()
    self.Running = False


newServer = Server("ONE")
newTask = Task("A","A","/home/runner/PowderblueBrownType/", "execute.sh")
newServer.AddTask(newTask)
Servers.append(newServer)
while True:
  for newServer in Servers:
    newServer.RunTaskAsync()
  time.sleep(5)
