import os
import json
from .process_google_contacts import _chunk_and_write


def process(config):
    cfg = config["PATHS"]["GOOGLE_KEEP"]
    base_input_dir = config["BASE_INPUT_DIR"]
    base_output_dir = config["BASE_OUTPUT_DIR"]
    word_limit = config["WORD_LIMIT_PER_FILE"]

    keep_dir = os.path.join(base_input_dir, cfg["INPUT_DIR"])
    output_dir = os.path.join(base_output_dir, cfg["OUTPUT_DIR"])

    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Processing Google Keep ---")

    all_notes = []
    for fname in os.listdir(keep_dir):
        if fname.endswith(".json"):
            with open(os.path.join(keep_dir, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            text, count = _format_note(data)
            if text:
                all_notes.append((text, count))

    _chunk_and_write(output_dir, "formatted_notes", all_notes, word_limit)


def _format_note(data):
    if data.get("isTrashed"):
        return None, 0
    title = data.get("title", "").strip() or "Untitled Note"
    content = data.get("textContent", "").strip()
    if not title and not content:
        return None, 0

    text = f"## {title}\n\n{content}"
    return text, len(text.split())
