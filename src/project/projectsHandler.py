import sys
import os

parent = os.path.abspath('./src')
sys.path.insert(1, parent)
from project import Project

class ProjectsHandler:
  def __init__(self, projects_paths, os="windows"):
    self.os = os
    self.projects_paths = projects_paths
    self.current = None
    self.projects = {}
    self.init_projects()

  def init_projects(self):
    for ind, path in enumerate(self.projects_paths):
      try:
        path = os.path.normpath(path)
        project = Project.load(path)
      except FileNotFoundError as err:
        print("Error: path '" + path + "' is not  a rarian project")
        del self.projects_paths[ind]
        continue
      if project.name in self.projects.keys():
        print("Error: duplicate project name -", project.name)
        continue
      self.projects[project.name] = project

  def set_current(self, name=None, path=None):
    if (not name) and (not path): return
    if (not name) and path:
      path = os.path.normpath(path)
      for proj_name in self.projects:
        if path == self.projects[proj_name].path(): name = proj_name

    if name not in self.projects.keys():
      raise ValueError("Project doesn't exist")
    # Turn previous project off:
    if self.current: self.projects[self.current].turn_off()
    self.current = name
    # Turn new project on:
    self.projects[self.current].turn_on()
    print(self.current, "is now the current project")

  def get_current(self):
    return self.current

  def save(self):
    if self.current is None: return None
    self.projects[self.current].save()

  def update(self, open_files, open_apps):
    if self.current is None: return None
    self.projects[self.current].update(open_files, open_apps)

  def get_proj_paths(self):
    if self.current is None: return None
    return self.projects[self.current].paths

  def get_proj_start_time(self):
    if self.current is None: return None
    return self.projects[self.current].start_time

  def get_all_projects(self):
    return list(self.projects.keys())

if __name__ == '__main__':
  handler = ProjectsHandler([os.path.abspath('.'), os.path.abspath('.'), "C:/"])
  handler.set_current(name="workspacesManager")
  print("current project:", handler.get_current())
  print("projects:", handler.get_all_projects())
  try:
    handler.set_current(name="rest")
  except BaseException as err:
    print("undefined project passed to set_current")

  handler.set_current(path=os.path.abspath('.'))
