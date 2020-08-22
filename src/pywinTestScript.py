import pywinauto as pwa
from pywinauto import Desktop
from pywinauto import Application

# openApps = pwa.findwindows.find_elements()
# for app in openApps:
#   print(app.class_name)
#   print("details: ", app)
#   app = Application().connect(handle=app.handle)

#%%

app = Application(backend="win32").connect(path="C:\\Program Files\\Mozilla Firefox\\firefox.exe")
dlg = app.Firefox
