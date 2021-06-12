from subprocess import Popen, PIPE
import dateutil.parser
import os

def run_powershell(cmd):
  return str(Popen(["powershell", cmd], stdout=PIPE).communicate() [0])

def pipe_PS_to_List(cmd):
  out_str = run_powershell(cmd)
  out = out_str.split("\\r\\n")
  out = out[2:len(out) - 3]
  out = [row.strip() for row in out]
  return out

def get_PS_table(cmd, items):
  full_cmd = cmd + " | Format-Table " + ", ".join(items) + " -AutoSize | Out-String -Width 1024"
  rows_list = run_powershell(full_cmd).split("\\r\\n")[1:-2]
  if len(rows_list) == 0: return []
  places = [rows_list[0].lower().find(item.lower()) for item in items]
  if len(items) == 1: table_list = [[row] for row in rows_list]
  else: table_list = [[row[:places[1]]] + [row[places[ind + 1]:places[ind + 2]] for ind in range(len(places) - 2)] + [row[places[-1]:]] for row in rows_list]
  table_list = [[cell.strip() for cell in row] for row in table_list]
  table_list = list(filter(lambda row: (row != items) and not (row[0].startswith("-")) and (row != [""] * len(items)), table_list))
  table_list.sort(key=lambda row: " ".join(row)) # sort the table alphebatically
  table_list = reslash(table_list)
  return table_list

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

def parse_time(df, items):
  for item in items:
    try:
        df[item] = df[item].map(lambda timeStr: \
          dateutil.parser.parse(timeStr).isoformat())
    except Exception as err:
      print("Failed to parse start time field, with error: " + str(err))
      raise err

  return df