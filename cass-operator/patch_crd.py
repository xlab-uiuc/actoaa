import re
import yaml
from logger import logger, YELLOW, PLAIN, RED

CRD = "data/bundle.yaml"
CASS_SCHEMA = "data/cassandra-yaml-typed.yaml"
OUTPUT = "data/cassdc.patched.crd.yaml"
HUGE_NUM = 9999999999

# TIME_UNITS = {"ms": 1, "s": 1000, "h": 3600000, "d": 86400000}
# SIZE_UNITS = {"KiB": 1, "MiB": 1024}

with open(CRD, 'r') as f:
    items = yaml.load_all(f, Loader=yaml.FullLoader)
    for cass_conf_item in items:
        if cass_conf_item["kind"] == "CustomResourceDefinition" and cass_conf_item["metadata"]["name"] == "cassandradatacenters.cassandra.datastax.com":
            crd = cass_conf_item
            break

with open(CASS_SCHEMA, "r") as f:
    cass_schema = yaml.load(f, Loader=yaml.FullLoader)

cass_spec = {}
for cass_conf_item in cass_schema:
    default_value: str = cass_conf_item["default_value"]
    guessed_type: str = cass_conf_item["guessed_type"]
    name: str =  cass_conf_item["name"]
    json_schema_type: str
    try:
        if guessed_type == "boolean":
            cass_spec[name] = {"type": "boolean"}
            logger.info("Processed %s%s%s %s", YELLOW, guessed_type, PLAIN, name)
            continue
        is_integer,                is_float,                is_size,                         is_time =\
        guessed_type == "integer", guessed_type == "float", guessed_type.startswith("size"), guessed_type.startswith("time")
        if is_integer or is_float or is_size or is_time:
            if is_float:
                json_schema_type = "number"
                reference_value: float = 0.9 if default_value == "<UNKNOWN>" else float(default_value)
            elif is_size or is_time:
                json_schema_type = "string"
                open_angle_bracket, close_angle_bracket = guessed_type.find("<"), guessed_type.rfind(">")
                guessed_unit = guessed_type[open_angle_bracket+1:close_angle_bracket]
                if default_value == "<UNKNOWN>":
                    reference_value = 1
                    unit = guessed_unit
                else:
                    match = re.match(r"(\d+)(.*)", default_value)
                    reference_value: int = int(match[1])
                    unit: str = match[2]
            else:
                assert is_integer
                json_schema_type = "integer"
                reference_value: int = 1 if default_value == "<UNKNOWN>" else int(default_value)
            values = set([reference_value, reference_value*2, reference_value/2,
                          HUGE_NUM, -HUGE_NUM, 0])
            if is_size or is_time:
                # append units
                values = [str(int(v))+unit for v in values]
            elif is_float:
                # take the values literally
                values = list(values)
            else:
                assert is_integer
                values.add(-reference_value)
                values.add(-reference_value*2)
                values.add(-reference_value/2)
                # val/2 might not be integer, convert
                values = [int(v) for v in values]
            cass_spec[name] = {"type": json_schema_type, "enum": values}
            logger.info("Processed %s%s%s %s", YELLOW, guessed_type, PLAIN, name)
            continue
        if guessed_type.startswith("enum"):
            open_angle_bracket, close_angle_bracket = guessed_type.find("<"), guessed_type.rfind(">")
            enumstr: str = guessed_type[open_angle_bracket+1:close_angle_bracket]
            values = enumstr.split("|")
            cass_spec[name] = {"type": "string", "enum": values}
            logger.info("Processed %s%s%s %s", YELLOW, guessed_type, PLAIN, name)
            continue
        if guessed_type == "string":
            values = [default_value, "alt_string"]
            cass_spec[name] = {"type": "string", "enum": values}
            logger.info("Processed %s%s%s %s", YELLOW, guessed_type, PLAIN, name)
            continue
        logger.warning("Ignoring %s%s%s %s", RED, guessed_type, PLAIN, name)
    except Exception as e:
        __import__('ipdb').set_trace()
        logger.error("Failed to process %s%s%s %s: %s", RED, guessed_type, PLAIN, name, e)

crd["spec"]["versions"][0]["schema"]["openAPIV3Schema"]["properties"]["spec"]["properties"] = {
    "config": {
        "type": "object",
        "properties": {
            "cassandra-yaml": {
                "type": "object",
                "properties": cass_spec
            }
        }
    }
}

crd["metadata"]["name"] = "xcassandradatacenters.cassandra.datastax.com"
crd["spec"]["names"] = {
    "kind": "XCassandraDatacenter",
    "listKind": "XCassandraDatacenterList",
    "plural": "xcassandradatacenters",
    "shortNames": ["xcassdc", "xcassdcs"],
    "singular": "xcassandradatacenter"
}

with open(OUTPUT, "w") as f:
    yaml.dump(crd, f)
