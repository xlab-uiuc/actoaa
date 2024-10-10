import ollama
import yaml
from tqdm import tqdm

OLLAMA_ENDPOINT = "http://localhost:11434"
MODEL = "llama3.1:70b"
PROMPTS_IDX = "cassandra"
EXAMPLES_PROLOGUE = "\nHere are some examples you may refer to:\n"

INPUT_FILE = "data/cassandra-yaml.yaml"
OUTPUT_FILE = "data/cassandra-yaml-types.csv"

YELLOW = "\x1b[38;5;3m"
PLAIN = "\x1b[0m"

llm = ollama.Client(host=OLLAMA_ENDPOINT)

with open("prompts.yaml", "r") as f:
    prompts = yaml.load(f, Loader=yaml.FullLoader)[PROMPTS_IDX]

prompt_prefix = prompts["rules"] + EXAMPLES_PROLOGUE + "\n".join(f"""
Task: {example['task']}
Answer: {example['answer']}
"""
    for example in prompts["examples"]) + "Here is your task:"

with open(INPUT_FILE, "r") as f:
    tasks = yaml.load(f, Loader=yaml.FullLoader)


with open(OUTPUT_FILE, "w") as f:
    for task in tqdm(tasks):
        llm_response = llm.chat(model=MODEL, messages=[
            {
                "role": "user",
                "content": prompt_prefix + task["description"]
            }
        ])
        guessed_type = llm_response["message"]["content"]
        tqdm.write(f"{task['name']}: {YELLOW}{guessed_type}{PLAIN}")
        f.write(f"{task['name']},{guessed_type}\n")
        f.flush()
