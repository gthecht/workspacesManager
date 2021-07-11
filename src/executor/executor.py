import pandas as pd
class Executor:
  def __init__(self, projects_handler, os="windows") -> None:
    self.projects_handler = projects_handler
    self.os = os
    self.data = {
      "files": None,
      "apps": None,
      "urls": None,
      "notes": None,
      "projects": None
    }
    self.bookmarks = self.data.copy() #empty dictionary

  # Open and close:
  def set_current(self, name=None, path=None):
    "Set current project"
    self.projects_handler.set_current(name, path)

  def save(self):
    "Save the projects"
    self.projects_handler.save()

  def close_project(self):
    "Close current project"
    self.projects_handler.close_project()

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
    return self.projects_handler.new_project(
      paths, name, proj_type, author, start_time, dirs, files, apps
    )

  def new_file(self, path=None):
    "Create new file"
    raise NotImplementedError

  def open_app(self, name=None, path=None):
    "Create new app"
    raise NotImplementedError

  def new_note(self, text, link=None):
    "Create new note"
    # I may want to offer the links, instead of just getting them
    raise NotImplementedError

  def remove_sub_dir(self, path):
    self.projects_handler.remove_sub_dir(path)

  # Get:
  def get_open(self):
    "Get the open project, files, apps and more"
    return self.projects_handler.get_open()

  def get_current(self):
    "Get the current project"
    return self.projects_handler.get_current()

  def get_data(self, member, n=1, sort_by="Relevance"):
    "Get top n of member (by relevance)"
    try:
      assert n > 0
    except AssertionError:
      raise AssertionError("number must be greater than 0")
    data = self.projects_handler.get_project_data(member, sort_by)
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
    n0 = self.bookmarks[member]
    n1 = n0 + n
    self.bookmarks[member] = n1
    if n < 0:
      n0 = n0 + n1
      n1 = n0 - n1
      n0 = n0 - n1
    return self.data[member][n0:n1]

if __name__ == '__main__':
  import os
  import sys
  project = os.path.abspath('./src/project')
  sys.path.insert(1, project)
  from projectsHandler import ProjectsHandler

  projects_handler = ProjectsHandler([os.path.abspath('.')], "windows")
  executor = Executor(projects_handler)

  executor.set_current(name="workspacesManager")
  assert executor.get_current() == "workspacesManager"
  executor.close_project()
  assert executor.get_current() == None
  assert executor.get_data("files", 3) == None

  executor.set_current(name="workspacesManager")
  print("open:")
  print(executor.get_open())
  print("files:")
  print(executor.get_data("files", 3))
  print("apps:")
  print(executor.get_data("apps", 3))
  print("notes:")
  print(executor.get_data("notes", 3))
  print("urls:")
  print(executor.get_data("urls", 3))
  print("projects:")
  print(executor.get_data("projects", 3))
