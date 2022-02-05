import pandas as pd
import threading


class CLIent(threading.Thread):
    def __init__(self, executor, batch=5):
        self.executor = executor
        self.batch = batch
        self.end_segment = "------------------------------------------------\n"
        self.running = True
        self.actions = {
            "open_project": "Assign a project",
            "get_open": "Get what's open",
            "open_file": "Open a file",
            "get_files": "Get files",
            "open_app": "Open an app",
            "get_apps": "Get apps",
            "insert_note": "Write a note",
            "get_notes": "Read notes",
            "create_project": "Create a new project",
            "quit": "quit"
        }
        self.more = ['m', 'more', 'mor']
        self.cancel = ['c', 'cancel', 'cancl']
        super().__init__(name="client")

    def run(self):
        while self.running:
            print(self.end_segment)
            self.action = self.choose_action()
            if self.action is None:
                continue
            else:
                method = getattr(self, self.action)
                method()

    def quit(self):
        print("Byebye")
        self.executor.quit()

    def stop(self):
        self.running = False

    def choose_action(self):
        print("Actions:")
        print("--------")
        counter = 0
        for action in self.actions:
            print("{0}. {1}".format(counter, self.actions[action]))
            counter += 1

        while True:
            user_input = input("Type [number] of your chosen action:\n")
            try:
                action = int(user_input)
                if action < counter and action > -1:
                    break
                else:
                    print("Illegal action number. Try again...\n")
            except ValueError:
                print("Your input wasn't a number. Try again...\n")

        return list(self.actions.keys())[action]

    def print_selected(self, selected, plural):
        if isinstance(selected, pd.DataFrame):
            print("Recent " + plural + ":")
            for num, member in enumerate(selected.index):
                print(str(num) + ".", member)
        elif isinstance(selected, list):
            print("Recent " + plural + ":")
            for num, member in enumerate(selected):
                print(str(num) + ".", member)
        else:
            print("There are currently no", plural)
            return False
        return True

    def choose_data(self, plural, singular=None):
        if singular.lower()[0] in ['a', 'e', 'i', 'o', 'u']:
            singular = "an " + singular
        elif singular:
            singular = "a " + singular
        else:
            singular = plural

        print("Open " + singular + "...")
        selected = self.executor.get_data(plural, self.batch)
        printable = self.print_selected(selected, plural)
        if not printable:
            return None

        while True:
            user_input = input("Type the number of the one you wish to open,\n"
                               "or 'm\more' for more options, or 'c\cancel' "
                               "to cancel:\n")
            if user_input.lower() in self.cancel:
                print("You have chosen not to open " + singular)
                print(self.end_segment)
                return None
            elif user_input.lower() in self.more:
                selected = self.executor.get_more(plural, self.batch)
                print("Less recent " + plural + ":")
                printable = self.print_selected(selected, plural)
                if not printable:
                    return None
                continue
            try:
                selected_num = int(user_input)
                if selected_num < len(selected):
                    break
            except ValueError:
                print("Your input wasn't a number. Try again...\n")

        if isinstance(selected, pd.DataFrame):
            print("Your choice:", selected.index[selected_num])
            print(self.end_segment)
            return selected.iloc[[selected_num]]
        elif isinstance(selected, list):
            print("Your choice:", selected[selected_num])
            print(self.end_segment)
            return selected[selected_num]

    # Actions:
    def get_open(self):
        open = self.executor.get_open()
        self.display_data(open)

    def display_data(self, data):
        if isinstance(data, pd.DataFrame):
            if data.empty:
                return
            for name in list(data["Name"]):
                print(f'- {name}')
            print('\n')
        elif isinstance(data, dict):
            for key in data.keys():
                print(f'{key}:')
                self.display_data(data[key])
        elif isinstance(data, list):
            if len(data) >= 1:
                for el in data:
                    print(f'- {el}')
            else:
                print('[]')
        else:
            print(data)

    def open_project(self):
        project_name = self.choose_data("projects", "project")
        if project_name:
            self.executor.set_current(project_name)

    def create_project(self):
        paths = input("Project paths (split with a comma):")
        paths = paths.split(",")
        paths = [path.strip() for path in paths]
        name = input("Name:")
        proj_type = input("Project type:")
        author = input("Author:")
        self.executor.new_project(paths, name, proj_type, author)

    def open_file(self):
        file = self.choose_data("files", "file")
        if file is None:
            return
        app = self.choose_data("apps", "app")
        if app is None:
            app = file.App[0]
        else:
            app = app.Path[0]
        print(f'opening {file.index[0]} with {app}')
        self.executor.open_file(file, app)

    def get_files(self):
        self.get_data("file")

    def open_app(self):
        # apps = self.choose_data("apps", "app")
        pass

    def get_apps(self):
        self.get_data("app")

    def get_data(self, data_type):
        data = self.choose_data(data_type + 's', data_type)
        if isinstance(data, pd.Series) or isinstance(data, list):
            print(data)
            accept = input(f'Do you want to another {data_type}?(y/n): ')
            if accept.lower() == "y":
                return self.get_data(data_type)

    def insert_note(self):
        print("Type in your note and hit ENTER...")
        user_input = input(">> ")
        if user_input == "cancel":
            print("You have canceled the note.")
            print(self.end_segment)
            return None
        else:
            print("You have typed:\n", user_input)
            accept = input("Do you want to publish?(y/n): ")
            if accept.lower() == "y":
                print(self.end_segment)
                return user_input
            else:
                return self.insert_note()

    def get_notes(self):
        return
        notes = self.choose_data("notes", "note")
        counter = 0
        for note in notes:
            print(str(counter) + ".\n", note)
            print(self.end_segment)
            counter += 1
