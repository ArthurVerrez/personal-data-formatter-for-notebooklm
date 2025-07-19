import os
import json
from datetime import datetime

def process(config):
    for platform in config['PATHS']['MESSENGER_INSTAGRAM']['PLATFORMS']:
        _process_platform(platform, config)

def _process_platform(platform, config):
    base_input_dir = config['BASE_INPUT_DIR']
    base_output_dir = config['BASE_OUTPUT_DIR']
    word_limit = config['WORD_LIMIT_PER_FILE']
    owner_names = config['EXPORT_OWNER_NAMES']
    
    input_dir = os.path.join(base_input_dir, platform)
    output_dir = os.path.join(base_output_dir, platform)

    if not os.path.exists(input_dir):
        print(f"\nSkipping {platform.title()}: Directory not found.")
        return

    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Processing {platform.title()} ---")

    convo_dirs = _find_convo_dirs(input_dir)
    if not convo_dirs: return

    current_chunk, current_count, file_counter = [], 0, 1

    for dir_path in convo_dirs:
        header, lines = _process_convo_folder(dir_path, owner_names)
        if not header or not lines: continue

        current_chunk.append("\n---\n" + header)
        current_count += len(header.split())

        for line in lines:
            line_count = len(line.split())
            if current_count + line_count > word_limit and current_chunk:
                _write_chat_chunk(output_dir, platform, file_counter, current_chunk, current_count, header)
                file_counter += 1
                current_chunk = [f"(Continuation of conversation with: {header.split(': ')[1].strip()})\n"]
                current_count = len(current_chunk[0].split())
            
            current_chunk.append(line)
            current_count += line_count

    if current_chunk:
        _write_chat_chunk(output_dir, platform, file_counter, current_chunk, current_count, header, is_final=(file_counter==1))

def _write_chat_chunk(output_dir, platform, counter, content, word_count, header, is_final=False):
    fname = f"conversations_{platform}.md" if is_final else f"conversations_{platform}_{counter}.md"
    with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f: f.write("\n".join(content))
    print(f"  - Wrote chunk to {fname} ({word_count} words).")

def _fix_encoding(text):
    try: return text.encode("latin1").decode("utf-8")
    except: return text

def _find_convo_dirs(root):
    dirs = []
    for subdir in ['inbox', 'archived_threads', 'message_requests']:
        path = os.path.join(root, subdir)
        if os.path.isdir(path):
            dirs.extend([os.path.join(path, item) for item in os.listdir(path) if os.path.isdir(os.path.join(path, item))])
    return dirs

def _process_convo_folder(dir_path, owner_names):
    msg_files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.startswith('message_') and f.endswith('.json')]
    if not msg_files: return None, None

    all_msgs = []
    recipient = "Unknown"
    
    try:
        with open(msg_files[0], 'r', encoding='utf-8') as f: data = json.load(f)
        title = _fix_encoding(data.get('title', os.path.basename(dir_path)))
        participants = [_fix_encoding(p.get('name', '')) for p in data.get('participants', [])]
        others = [p for p in participants if p not in owner_names and p]
        recipient = title if len(participants) > 2 else (others[0] if others else "Unknown")
    except Exception as e:
        print(f"  - Warning: Could not read metadata from {os.path.basename(msg_files[0])}. Error: {e}")

    for fpath in msg_files:
        try:
            with open(fpath, 'r', encoding='utf-8') as f: data = json.load(f)
            all_msgs.extend([m for m in data.get('messages', []) if 'content' in m and 'timestamp_ms' in m])
        except: continue
    
    all_msgs.sort(key=lambda m: m.get('timestamp_ms', 0))
    header = f"# Conversation with: {recipient}\n"
    lines = []
    for msg in all_msgs:
        sender = _fix_encoding(msg.get('sender_name', ''))
        ts = datetime.fromtimestamp(msg['timestamp_ms'] / 1000).strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {sender}: {_fix_encoding(msg['content'])}"
        if sender in owner_names:
            line = f"[{ts}] {owner_names[0]} TO {recipient}: {_fix_encoding(msg['content'])}"
        lines.append(line)
        
    return header, lines