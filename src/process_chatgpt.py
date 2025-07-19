import json
import os
from datetime import datetime


def process(config):
    cfg = config["PATHS"]["CHATGPT"]
    base_input_dir = config["BASE_INPUT_DIR"]
    base_output_dir = config["BASE_OUTPUT_DIR"]
    word_limit = config["WORD_LIMIT_PER_FILE"]

    conversations_json_path = os.path.join(base_input_dir, cfg["INPUT_FILE"])
    output_dir = os.path.join(base_output_dir, cfg["OUTPUT_DIR"])

    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Processing ChatGPT ---")

    with open(conversations_json_path, "r", encoding="utf-8") as f:
        all_conversations = json.load(f)

    current_chunk = []
    current_word_count = 0
    start_time, end_time = None, None

    for convo in all_conversations:
        convo_time = convo.get("create_time")
        if not convo_time:
            continue

        text, count = _parse_conversation(convo)
        if not text:
            continue

        if current_word_count + count > word_limit and current_chunk:
            _write_chunk(
                output_dir,
                "chatgpt",
                start_time,
                end_time,
                current_chunk,
                current_word_count,
            )
            current_chunk, current_word_count, start_time = [], 0, None

        if not current_chunk:
            start_time = convo_time

        current_chunk.append(text)
        current_word_count += count
        end_time = convo_time

    if current_chunk:
        _write_chunk(
            output_dir,
            "chatgpt",
            start_time,
            end_time,
            current_chunk,
            current_word_count,
        )


def _write_chunk(output_dir, prefix, start_ts, end_ts, content, word_count):
    filename = f"conversations_{prefix}_{int(start_ts)}_{int(end_ts)}.md"
    with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
        f.write("\n---\n\n".join(content))
    print(f"  - Wrote chunk to {filename} ({word_count} words).")


def _parse_conversation(convo_data):
    title = convo_data.get("title", "Untitled")
    mapping = convo_data.get("mapping", {})
    if not mapping:
        return "", 0

    root_id = next((k for k, v in mapping.items() if v.get("parent") is None), None)
    if not root_id:
        return "", 0

    parts = [f"# Conversation: {title}\n"]

    # Safely get the first message ID
    root_node = mapping.get(root_id, {})
    children = root_node.get("children", [])
    current_id = children[0] if children else None

    while current_id:
        node = mapping.get(current_id)
        if not node or not node.get("message"):
            break

        msg = node["message"]
        role = msg.get("author", {}).get("role")
        content_parts = msg.get("content", {}).get("parts")

        if (
            role in ["user", "assistant"]
            and content_parts
            and isinstance(content_parts[0], str)
            and content_parts[0]
        ):
            author = "Arthur" if role == "user" else "ChatGPT"
            ts = (
                datetime.fromtimestamp(msg["create_time"]).strftime("%Y-%m-%d %H:%M:%S")
                if msg.get("create_time")
                else "Unknown Time"
            )
            parts.append(f"### {author} ({ts}):\n" + "\n".join(content_parts) + "\n")

        # Safely get the next message ID to handle conversation branches that end
        children = node.get("children", [])
        current_id = children[0] if children else None

    # Only return text if there's more than just the title
    if len(parts) > 1:
        text = "\n".join(parts)
        return text, len(text.split())

    return "", 0
