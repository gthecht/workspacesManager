import sys
import os
import json
import threading
import queue

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
from rarian.project.project import Project

class ProjectsHandler(threading.Thread):
  def __init__(self, data_path, os="windows"):
    self.os = os
    self.data_path = data_path
    self.load_data()
    self.projects = {}
    self.init_projects()
    self.running = True
    self.q = queue.Queue()
    super().__init__(name="projectHandler", daemon=True)

  def run(self):
    while self.running:
      job = self.q.get()
      method = getattr(self, job["method"])
      value = method(**job["args"])
      # return the value if its supposed to be returned:
      if "reply_q" in job.keys(): job["reply_q"].put(value)
      self.q.task_done()

  def load_data(self):
    with open(self.data_path, 'r') as data_file:
      data_str = data_file.read()
    data = json.loads(data_str)
    self.projects_paths = data["projects"]
    self.current = None
    self.default_author = data["default author"]

  def init_projects(self):
    for ind, path in enumerate(self.projects_paths):
      try:
        path = os.path.normpath(path)
        project = Project.load(path)
      except FileNotFoundError:
        print("Error: path '" + path + "' is not  a rarian project")
        del self.projects_paths[ind]
        continue
      if project.name in self.projects.keys():
        print("Error: duplicate project name -", project.name)
        continue
      self.projects[project.name] = project

  # Open and close:
  def set_current(self, name=None, path=None):
    if (not name) and (not path): return
    if (not name) and path:
      path = os.path.normpath(path)
      for proj_name in self.projects:
        if path == self.projects[proj_name].path(): name = proj_name

    if name not in self.projects.keys():
      raise ValueError("Project doesn't exist")
    # Turn previous project off:
    if name == self.current: return
    if self.current: self.projects[self.current].turn_off()
    self.current = name
    # Turn new project on:
    self.projects[self.current].turn_on()
    print(self.current, "is now the current project")

  def get_current(self):
    return self.current

  def save(self):
    data_dict = {
      "projects": self.projects_paths,
      "current": self.current,
      "default author": self.default_author,
    }
    with open(self.data_path, 'w') as data_path:
      json.dump(data_dict, data_path, sort_keys=True, indent=2)
    if self.current is None: return None
    self.projects[self.current].save()

  def close_project(self):
    if self.current:
      self.projects[self.current].turn_off()
      self.current = None

  # Insert:
  def new_project(
    self,
    paths,
    name=None,
    proj_type=None,
    author=None,
    start_time=None,
    dirs=None,
    files=None,
    apps=[]
  ):
    """Create new project"""
    if name in self.projects.keys():
      raise ValueError(f"project of name {name} already exists")
    else:
      project = Project(paths, name, proj_type, author, start_time, dirs, files, apps)
      self.projects[project.name] = project
      self.projects_paths.append(paths[0])

  def remove_sub_dir(self, path):
    """Removes sub directories, for instance when a sub directory is a project"""
    if self.current: self.projects[self.current].remove_sub_dir(path)
    else: print("Assign project before you remove a directory")

  def add_sub_dir(self, path):
    """Adds a sub directory - that possibly was removed"""
    raise NotImplementedError

  # Gather:
  def update(self, open_files, open_apps):
    if self.current is None: return None
    self.projects[self.current].update(open_files, open_apps)
    self.save()

  # Get:
  def get_open(self):
    """Get the open project, files, apps and more"""
    if self.current is None: return None
    return self.projects[self.current].get_open()

  def get_proj_dirs(self):
    if self.current is None: return None
    return self.projects[self.current].dirs

  def get_proj_start_time(self):
    if self.current is None: return None
    return self.projects[self.current].start_time

  def get_project_data(self, member, sort_by="Relevance"):
    if member == "projects": return list(self.projects.keys())
    if self.current is None: return None
    if member == "files":
      data = self.projects[self.current].files
      data.sort_values(by=sort_by, ascending=False, inplace=False)
    elif member == "apps": data = self.projects[self.current].apps
    elif member == "notes": data = self.projects[self.current].notes
    elif member == "urls": data = self.projects[self.current].urls
    else: raise ValueError("undefined data member")
    return data

  def stop(self):
    self.save()
    self.running = False
