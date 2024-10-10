import ollama
import yaml
from tqdm import tqdm

OLLAMA_ENDPOINT = "http://localhost:11434"
MODEL = "llama3.1:70b-instruct-q6_K"
EXAMPLES_PROLOGUE = "\nHere are some examples you may refer to:\n"

PROMPTS = [
'''
You are provided with a list of variable names, their corresponding descriptions and default values sometimes. Later you will be asked about their types.

''',
'''
Reply with the verbatim string "ack" to indicate that you understand the task.
''',
'''
Acceptable types include "boolean", "integer", "float", "string", "enum", "rString", "hostname", "port", "path", "size", "time", "object", "array" and "unknown".
For "enum", list all mentioned options separated by the character "|" in angle brackets, e.g. "enum<A|B>".
Only list options mentioned in the description. Never list options that do not appear in the description. For example, there is no KerberosAuthenticator or InternalRoleManager.
Always prefer "boolean" over "enum" if the only options are true and false.
Always use "time" or "size" when the default value contains a unit e.g. "1024KiB".
Always use "time" or "size" when the default value contains a unit e.g. "1024KiB".
Always use "time" or "size" when the default value contains a unit e.g. "1024KiB".
When you think a variable represents time or size, put the recommended unit in angle brackets, e.g. "time<ms>" or "size<MiB>".
Any variable with the term "threshold" in its name is likely a float rather than integer.
"rString" means string where some limitations apply.
For arrays, put the type of elements in angle brackets, e.g. "array<integer>" or "array<enum<A|B>>".
Use "unknown" when you are not sure. Do not randomly guess and always say "unknown" when you are not completely sure. It is better to say "unknown" than producing a wrong guess.
Anything more complex is considered an "object".
You may use your previous responses to help with current tasks. For example, you may believe that a variable named "coordinator_read_size_fail_threshold" has the same type as "coordinator_read_size_warn_threshold". However, always prefer information from the direct description and default value over information about other variables.

Here are some examples to get you started. You may use these examples to help you with your task.

query: cluster_name
answer: string

query: network_authorizer
answer: enum<AllowAllNetworkAuthorizer|CassandraNetworkAuthorizer>

query: disk_failure_policy
answer: enum<die|stop_paranoid|stop|best_effort|ignore>

query: commit_failure_policy
answer: enum<die|stop|stop_commit|ignore>

query: traverse_auth_from_root
answer: boolean

query: commitlog_sync_batch_window_in_ms
answer: integer

query: max_hint_window
answer: time<ms>

query: commitlog_total_space
answer: size<MiB>

query: cdc_raw_directory
answer: path

query: listen_address
answer: hostname

query: native_transport_port
answer: port

query: audit_logging_options
answer: unknown

query: listen_interface
answer: rString

query: hinted_handoff_disabled_datacenters
answer: object

query: table_properties_warned
answer: array<unknown>

Now, tell me the type of %s. Your answer should only contain the type name and nothing else.
'''
]

INPUT_FILE = "data/cassandra-yaml.yaml"
OUTPUT_FILE = "data/cassandra-yaml-types.csv"

YELLOW = "\x1b[38;5;3m"
PLAIN = "\x1b[0m"

llm = ollama.Client(host=OLLAMA_ENDPOINT)

with open(INPUT_FILE, "r") as f:
    tasks = yaml.load(f, Loader=yaml.FullLoader)

first_prompt = PROMPTS[0]
for task in tasks:
    first_prompt += f'''
Variable Name: {task["name"]}
Description: {task["description"]}
'''
    if task["default_value"] != "<UNKNOWN>":
        first_prompt += f'''
Default Value: {task["default_value"]}
'''
    first_prompt += "\n"
first_prompt += PROMPTS[1]

messages = [{
    "role": "user",
    "content": first_prompt
}]

first_response = llm.chat(model=MODEL, messages=messages)
messages.append(first_response["message"])

with open(OUTPUT_FILE, "w") as f:
    for task in tqdm(tasks):
        messages.append({
            "role": "user",
            "content": PROMPTS[2] % task["name"]
        })
        llm_response = llm.chat(model=MODEL, messages=messages)
        messages.append(llm_response["message"])
        guessed_type = llm_response["message"]["content"]
        tqdm.write(f"{task['name']}: {YELLOW}{guessed_type}{PLAIN}")
        f.write(f"{task['name']},{guessed_type}\n")
        f.flush()
