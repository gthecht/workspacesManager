import pandas as pd
import queue

from rarian import powershellClient as PSClient

class Executor:
  def __init__(self, projects_handler, quit, os="windows") -> None:
    self.projects_handler = projects_handler
    self.quit = quit
    self.running = True
    self.os = os
    self.data = {
      "files": None,
      "apps": None,
      "urls": None,
      "notes": None,
      "projects": None
    }
    self.bookmarks = self.data.copy() #empty dictionary
    self.reply_q = queue.Queue()

  def add_job(self, job):
    self.projects_handler.q.put(job)
    if "reply_q" not in job.keys(): return
    else:
      reply = None
      while self.reply_q.empty():
        if not self.running: return False
        continue
      reply = self.reply_q.get()
      return reply

  # Open and close:
  def set_current(self, name=None, path=None):
    "Set current project"
    job = {
      "method": "set_current",
      "args": {
        "name": name,
        "path": path
      },
      "reply_q": self.reply_q
    }
    return self.add_job(job)
    self.projects_handler.set_current(name, path)

  def save(self):
    "Save the projects"
    job = {
      "method": "save",
      "args": {}
    }
    return self.add_job(job)
    self.projects_handler.save()

  def close_project(self):
    "Close current project"
    job = {
      "method": "close_project",
      "args": {}
    }
    return self.add_job(job)

  # Insert new:
  def new_project(
    self,
    paths=None,
    name=None,
    proj_type=None,
    author=None,
    start_time=None,
    dirs=None,
    files=None,
    apps=None,
  ):
    "Create new project"
    # if fields are missing, query for them...
    job = {
      "method": "new_project",
      "args": {
        "paths": paths,
        "name": name,
        "proj_type": proj_type,
        "author": author,
        "start_time": start_time,
        "dirs": dirs,
        "files": files,
        "apps": apps
      },
      "reply_q": self.reply_q
    }
    return self.add_job(job)

  def new_file(self, path=None):
    "Create new file"
    raise NotImplementedError

  def open_file(self, file, app=""):
    "Open file with app"
    if app == "": cmd = f'Invoke-Item "{file.index[0]}"'
    else: cmd = f'& "{app}" "{file.index[0]}"'
    PSClient.run_powershell(cmd)
    job = {
      "method": "opened_file",
      "args": {
        "file": file,
        "app": app,
      },
    }
    return self.add_job(job)

  def open_app(self, name=None, path=None):
    "Open an app"
    raise NotImplementedError

  def new_note(self, text, link=None):
    "Create new note"
    # I may want to offer the links, instead of just getting them
    raise NotImplementedError

  def remove_sub_dir(self, path):
    job = {
      "method": "remove_sub_dir",
      "args": {
        "path": path
      },
      "reply_q": self.reply_q
    }
    return self.add_job(job)

  # Get:
  def get_open(self):
    "Get the open project, files, apps and more"
    job = {
      "method": "get_open",
      "args": {},
      "reply_q": self.reply_q
    }
    return self.add_job(job)

  def get_current(self):
    "Get the current project"
    job = {
      "method": "get_current",
      "args": {},
      "reply_q": self.reply_q
    }
    return self.add_job(job)

  def get_data(self, member, n=1, sort_by="Relevance"):
    "Get top n of member (by relevance)"
    try:
      assert n > 0
    except AssertionError:
      raise AssertionError("number must be greater than 0")

    job = {
      "method": "get_project_data",
      "args": {
        "member": member,
        "sort_by": sort_by
      },
      "reply_q": self.reply_q
    }
    data = self.add_job(job)
    if isinstance(data, pd.DataFrame):
      self.data[member] = data
      self.bookmarks[member] = min(n, len(data))
      return self.data[member][:n]
    elif isinstance(data, list):
      self.data[member] = data
      self.bookmarks[member] = min(n, len(data))
      return self.data[member][:n]
    return None

  def get_more(self, member, n=1): # can also get previous if n<0
    max = len(self.data[member])
    n0 = self.bookmarks[member]
    n1 = n0 + n
    self.bookmarks[member] = n1
    if n < 0:
      n0 = n0 + n1
      n1 = n0 - n1
      n0 = n0 - n1
    if n1 > max:
      n0 = n1 - abs(n)
      n1 = max
    return self.data[member][n0:n1]

  def stop(self):
    self.running = False
