from datetime import datetime
import pandas as pd

# from time import sleep
from asyncio import sleep
import asyncio
import os
from handlersManager import HandlersManager

class Gatherer:
  def __init__(self, log_dir):
    self.log_dir = log_dir
    self.handlers_manager = HandlersManager([os.path.abspath('.')])
    self.run = False
    self.log_file = self.log_dir + "log-" + datetime.now().strftime('%Y-%m-%dT%H-%M-%S') + ".csv"
    self.SLEEP_TIME = 30 # time to sleep between data collection - note that gathering the apps takes about 2 seconds

  async def init(self):
    await self.handlers_manager.init()

  async def gather(self):
    self.run = True
    try:
      await self.handlers_manager.gather()
      await self.handlers_manager.save()
      self.data = self.handlers_manager.get_apps()
    except Exception as err:
      print("Failed to gather data with err: " + str(err))
      print("Waiting a bit, and trying to gather again")
      await asyncio.sleep(self.SLEEP_TIME)
      return await self.gather()

    self.data.to_csv(self.log_file, index=False)
    while self.run:
      await asyncio.sleep(self.SLEEP_TIME)
      print("Gathering data")
      try:
        await self.handlers_manager.gather()
        await self.handlers_manager.save()
        data = self.handlers_manager.get_apps()
      except Exception as err:
        print("Failed to gather data with err: " + str(err))
        print("Waiting a bit, and trying to gather again")
        continue
      else:
        self.compare_data(data)
        self.data.to_csv(self.log_file, index=False)

  def compare_data(self, data):
    # find rows from the old that are duplicated in the new:
    concat_df = pd.concat([data, self.data], ignore_index=True)
    duplicated = concat_df.duplicated(keep='first')
    ended = [not dup for dup in duplicated[len(data):]] # these are the old apps that have ended
    now = datetime.now().isoformat()[:-7]
    for ind in [i for i, e in enumerate(ended) if e]:
      if concat_df.loc[ind + len(data.index)]["EndTime"] == "":
        concat_df.loc[ind + len(data.index)]["EndTime"] = now

    duplicated_start = concat_df.duplicated(keep='last')
    started = [not dup for dup in duplicated_start[:len(data)]] # these are the new apps that have started
    for ind in [i for i, e in enumerate(started) if e]:
      concat_df.loc[ind]["StartTime"] = now
    self.data = concat_df.drop_duplicates().sort_values(["App", "Name", "StartTime", "EndTime"], ignore_index=True)

  def stop(self):
    self.run = False

if __name__ == '__main__':
  gatherer = Gatherer("C:/Users/GiladHecht/Workspace/workspacesManager/logs/")
  asyncio.run(gatherer.init())
  asyncio.run(gatherer.gather())
