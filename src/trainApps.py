import os
import pandas as pd
from datetime import datetime
import numpy as np

logFiles = os.listdir("./logs")
logsDf = pd.DataFrame()
for file in logFiles:
  currLogs = pd.read_csv("./logs/" + file)
  logsDf = pd.concat([logsDf, currLogs])

logsDf = logsDf.drop_duplicates(ignore_index=True)