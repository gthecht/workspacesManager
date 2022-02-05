from subprocess import Popen, PIPE
import dateutil.parser
import os


def run_powershell(cmd):
    """Run a command in powershell and return string"""
    out = Popen(["powershell", cmd], stdout=PIPE).communicate()[0]
    return out.decode('windows-1252')


def get_PS_table_from_list(cmd, items):
    """Run a command in powershell and output with Format-List,
    and return pd.dataFrame"""
    full_cmd = cmd + " | Format-List " + \
        ", ".join(items) + " | Out-String -Width 1024"
    cluster_list = run_powershell(full_cmd).split("\r\n\r\n")[1:-2]
    table_list = []
    for group in cluster_list:
        row_list = [""] * len(items)
        for row in group.split("\r\n"):
            pair = row.split(" : ")
            pair = [cell.strip() for cell in pair]
            if pair[0] in items:
                row_list[items.index(pair[0])] = pair[1]
        table_list.append(row_list)
    # sort the table alphebatically
    table_list.sort(key=lambda row: " ".join(row))
    table_list = reslash(table_list)
    return table_list


def reslash(data_list, slash="\\"):
    """Make sure path's slashes are correct"""
    for ind, element in enumerate(data_list):
        try:
            if type(element) == list:
                element = reslash(element, slash)
                data_list[ind] = element
            elif slash in element:
                data_list[ind] = os.path.normpath(element)
        except TypeError:
            # value wasn't a string
            continue
    return data_list


def parse_time(df, items):
    """Parse powershell times in pd.DataFrame to iso-format"""
    for item in items:
        try:
            df[item] = df[item].map(lambda timeStr:
                                    dateutil.parser.parse(timeStr).isoformat())
        except Exception as err:
            print("Failed to parse start time field, with error: " + str(err))
            raise err

    return df
