from subprocess import Popen, PIPE
import dateutil.parser
import os

def runPowershell(cmd):
  return str(Popen(["powershell", cmd], stdout=PIPE).communicate() [0])

def pipePS2List(cmd):
  outStr = runPowershell(cmd)
  out = outStr.split("\\r\\n")
  out = out[2:len(out) - 3]
  out = [row.strip() for row in out]
  return out

def getPSTable(cmd, items):
  fullCmd = cmd + " | Format-Table " + ", ".join(items) + " -AutoSize | Out-String -Width 1024"
  rowsList = runPowershell(fullCmd).split("\\r\\n")[1:-2]
  if len(rowsList) == 0: return []
  places = [rowsList[0].lower().find(item.lower()) for item in items]
  if len(items) == 1: tableList = [[row] for row in rowsList]
  else: tableList = [[row[:places[1]]] + [row[places[ind + 1]:places[ind + 2]] for ind in range(len(places) - 2)] + [row[places[-1]:]] for row in rowsList]
  tableList = [[cell.strip() for cell in row] for row in tableList]
  tableList = list(filter(lambda row: (row != items) and not (row[0].startswith("-")) and (row != [""] * len(items)), tableList))
  tableList.sort(key=lambda row: " ".join(row)) # sort the table alphebatically
  tableList = reslash(tableList)
  return tableList

def reslash(data_list, slash="\\"):
  for ind, element in enumerate(data_list):
    try:
      if type(element) == list:
        element = reslash(element, slash)
        data_list[ind] = element
      elif "\\" in element:
        data_list[ind] = os.path.normpath(element)
    except TypeError as err:
      # value wasn't a string
      continue
  return data_list

def parseTime(df, items):
  for item in items:
    try:
        df[item] = df[item].map(lambda timeStr: \
          dateutil.parser.parse(timeStr).isoformat())
    except Exception as err:
      print("Failed to parse start time field, with error: " + str(err))
      raise err

  return df