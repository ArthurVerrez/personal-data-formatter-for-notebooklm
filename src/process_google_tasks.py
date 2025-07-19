import os
import json
from datetime import datetime
from .process_google_contacts import _chunk_and_write


def process(config):
    cfg = config["PATHS"]["GOOGLE_TASKS"]
    base_input_dir = config["BASE_INPUT_DIR"]
    base_output_dir = config["BASE_OUTPUT_DIR"]
    word_limit = config["WORD_LIMIT_PER_FILE"]

    tasks_path = os.path.join(base_input_dir, cfg["INPUT_FILE"])
    output_dir = os.path.join(base_output_dir, cfg["OUTPUT_DIR"])

    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Processing Google Tasks ---")

    try:
        with open(tasks_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"  - Skipped: {tasks_path} not found.")
        return

    all_lists = [_format_task_list(l) for l in data.get("items", [])]
    _chunk_and_write(output_dir, "formatted_tasks", all_lists, word_limit)


def _format_task_list(task_list):
    lines = [f"# {task_list.get('title', 'Untitled List')}"]
    tasks = task_list.get("items", [])
    if not tasks:
        return "", 0

    task_map = {t["id"]: t for t in tasks}
    parent_map = {tid: [] for tid in task_map}
    root_tasks = [
        t for t in tasks if not t.get("parent") or t.get("parent") not in parent_map
    ]
    for t in tasks:
        if t.get("parent") in parent_map:
            parent_map[t["parent"]].append(t)

    def format_recursive(task, level=0):
        indent = "  " * level
        status = "x" if task.get("status") == "completed" else " "
        due = (
            f" (Due: {datetime.fromisoformat(task['due'].replace('Z', '+00:00')).strftime('%Y-%m-%d')})"
            if task.get("due")
            else ""
        )

        task_lines = [
            f"{indent}- [{status}] {task.get('title', 'No Title').strip()}{due}"
        ]
        if task.get("notes"):
            task_lines.append(
                f"{indent}  > {task['notes'].strip().replace('\n', f'\n{indent}  > ')}"
            )

        for child in parent_map.get(task["id"], []):
            task_lines.extend(format_recursive(child, level + 1))
        return task_lines

    for task in root_tasks:
        lines.extend(format_recursive(task))

    text = "\n".join(lines)
    return text, len(text.split())
