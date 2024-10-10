import yaml

SCHEMA_INPUT = "data/cassandra-yaml.yaml"
TYPE_INPUT = "data/cassandra-yaml-types.csv"
OUTPUT = "data/cassandra-yaml-typed.yaml"

with open(SCHEMA_INPUT, "r") as fp:
    schema = yaml.load(fp, Loader=yaml.FullLoader)

with open(TYPE_INPUT, "r") as fp:
    types = {}
    for line in fp:
        key, value = line.strip().split(",", 1)
        types[key] = value

for item in schema:
    guessed_type = types.get(item["name"])
    if guessed_type is not None:
        item["guessed_type"] = guessed_type
    else:
        item["guessed_type"] = "unknown"

with open(OUTPUT, "w") as fp:
    yaml.dump(schema, fp)
