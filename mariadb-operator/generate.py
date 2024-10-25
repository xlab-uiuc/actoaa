#!/usr/bin/env python3
import json
import yaml
import random

INPUT = "data/mariadb-docs.yaml"
OUTPUT = "data/mariadb.json"

LARGE = 999999999999

def rand_float_or_int(begin, end):
    if isinstance(begin, int) and isinstance(end, int):
        return random.randint(begin, end)
    return begin + random.random() * (end-begin)

def float_or_int(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def not_out_of_range(rmin, rmax, val):
    if rmin and rmin > val:
        return False
    if rmax and rmax < val:
        return False
    return True

def avg(a, b):
    if isinstance(a, int) and isinstance(b, int):
        return (a+b)//2
    return (a+b)/2

with open(INPUT, "r") as f:
    items = yaml.load(f, Loader=yaml.FullLoader)

properties = {}

for item in items:
    if "Removed" in item or "Deprecated" in item:
        continue
    name = item["name"]
    kind = item.get("Data Type") or item.get("Type") # no item has both
    defval = item.get("Default Value")
    oapi_type = None
    if kind in ["directory name", "enum", "filename", "path name", "string"]:
        oapi_type = "string"
    if item.get("Valid Values") is not None:
        vals = item["Valid Values"].split(", ")
    else:
        match kind:
            case None:
                print("SKIPPED:", name)
                continue
            case "set":
                print("SKIPPED:", name)
                continue
            case "boolean":
                vals = ["0", "1"]
                oapi_type = "boolean"
            case "string":
                vals = [defval, ""]
            case k if k in ["number", "numeric"]:

                # Parse range
                range_txt = item.get("Range - 64 bit") or item.get("Range")
                rmin, rmax = None, None
                if range_txt is not None:
                    if " to " in range_txt:
                        rmin_, rmax_ = range_txt.split(" to ")
                        rmin = float_or_int(rmin_)
                        rmax = float_or_int(rmax_)
                    elif upwards_text_loc := range_txt.find(" upwards") != -1:
                        rmin = float_or_int(range_txt[:upwards_text_loc])

                # Now, rmin and rmax can either be None, int or float

                # Parse default value
                if defval is None or isinstance(defval, (float, int)):
                    pass
                elif isinstance(defval, str):
                    extra_stuff_loc = defval.find(" (")
                    if extra_stuff_loc != -1:
                        defval = defval[:defval.find(" (")]
                    defval = float_or_int(defval)

                # Now, defval can either be None, int or float

                # Fact: no item has a range but no default, so safe to not handle

                vals = set([0])
                if defval:
                    if rmin:
                        vals.add(rand_float_or_int(rmin, defval))
                    else:
                        vals.add(avg(0, defval))
                    if rmax:
                        vals.add(rand_float_or_int(defval, rmax))
                    else:
                        vals.add(2*defval)

                if rmin:
                    vals.add(rmin-1)
                elif rmax:
                    vals.add(rmax+1)

                vals = list(vals)

                # Edge case
                if not rmin and not rmax and defval == 0:
                    vals = [-1, 0, 1]


                oapi_type = "number" \
                        if isinstance(rmin, float) \
                        or isinstance(rmax, float) \
                        or isinstance(defval, float) \
                        else "integer"

            case k if k in ["path name", "directory name", "file name"]:
                vals = [defval, "/tmp/tmpfile", "/dev/null", "/dev/zero", "/invalid"]

    if oapi_type == "string":
        vals += ["ACTOKEY"]
    properties[name] = {
        "type": oapi_type,
        "default": defval,
        "enum": vals
    }

with open(OUTPUT, "w") as f:
    json.dump(properties, f, indent=2)
