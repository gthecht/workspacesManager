
class CLIent:
  def __init__(self):
    self.Batch = 5
    self.end_segment = "------------------------------------------------\n"

  def choose_action(self):
    print("Choose what you want to do...")
    print("0. Assign a project")
    print("1. Write a note")
    print("2. Read notes")
    print("3. Create a new project")

    while True:
      user_input = input("Type the number of the action you wish to choose, or 'cancel' to cancel:\n")
      if user_input == "cancel":
        print("You have chosen not to take an action")
        print(self.end_segment)
        return None
      try:
        action = int(user_input)
        break
      except ValueError:
        print("Your input wasn't a number. Try again...\n")

    if action == 0: return "open_project"
    if action == 1: return "insert_note"
    if action == 2: return "get_note"
    if action == 3: return "create_project"

  def assign_project(self, projects):
    print("Open a project...")
    k = self.Batch
    selected = projects[:k]
    print("Recent projects:")
    for num, project in enumerate(selected):
      print(str(num) + ".", project)

    while True:
      user_input = input("Type the number of the project you wish to open,\n" +
                      "or 'more' for more projects, or 'cancel' to cancel:\n")
      if user_input == "cancel":
        print("You have chosen not to open a project")
        print(self.end_segment)
        return None
      elif user_input == "more":
        selected = projects[k: k+self.Batch]
        k = k+self.Batch
        print("Less recent projects:")
        for num, project in enumerate(selected):
          print(str(num) + ".", project)
        continue
      try:
        proj_num = int(user_input)
        break
      except ValueError:
        print("Your input wasn't a number. Try again...\n")

    print("Starting up:", selected[proj_num])
    print(self.end_segment)
    return selected[proj_num]

  def create_project(self):
    pass

  def insert_note(self):
    print("Type in your note and hit ENTER...")
    user_input = input(">> ")
    if user_input == "cancel":
      print("You have canceled the note.")
      print(self.end_segment)
      return None
    else:
      print("You have types:\n", user_input)
      accept = input("Do you want to publish?(y/n): ")
      if accept.lower() == "y":
        print(self.end_segment)
        return user_input
      else:
        return self.insert_note()

  def get_notes(self, notes):
    counter = 0
    for note in notes:
      print(str(counter) + ".\n", note)
      print(self.end_segment)
      counter += 1


if __name__ == '__main__':
  client = CLIent()
  project = client.assign_project(["first", "second", "third", "fourth", "fifth", "six", "seven"])
  project = client.assign_project(["first", "second", "third"])
  note = client.insert_note()
  client.get_notes([note, note, note])
