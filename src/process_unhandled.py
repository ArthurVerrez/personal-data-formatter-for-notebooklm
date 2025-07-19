import os
import shutil


def process(config):
    base_input_dir = config["BASE_INPUT_DIR"]
    base_output_dir = config["BASE_OUTPUT_DIR"]
    word_limit = config["WORD_LIMIT_PER_FILE"]

    # The output directory for all unhandled files and folders
    unhandled_base_output_dir = os.path.join(
        base_output_dir, config["PATHS"]["UNHANDLED"]["OUTPUT_DIR"]
    )

    # Get a set of top-level directories handled by other modules
    handled_dirs = set()
    for key, val in config["PATHS"].items():
        if key == "UNHANDLED":
            continue
        if "INPUT_DIR" in val:
            handled_dirs.add(val["INPUT_DIR"])
        elif "INPUT_FILE" in val:
            # e.g., 'chatgpt/conversations.json' -> 'chatgpt'
            dir_name = os.path.normpath(val["INPUT_FILE"]).split(os.sep)[0]
            handled_dirs.add(dir_name)
        elif "PLATFORMS" in val:
            handled_dirs.update(val["PLATFORMS"])

    print(f"\n--- Processing Unhandled Files & Directories ---")

    # Walk through the entire raw_sources directory
    for root, dirs, files in os.walk(base_input_dir, topdown=True):
        # At the top level, remove handled directories from the list of dirs to visit
        if root == base_input_dir:
            dirs[:] = [
                d for d in dirs if d not in handled_dirs and not d.startswith(".")
            ]

        # Process all files in the current directory (which is guaranteed to be unhandled)
        for filename in files:
            if filename.startswith("."):
                continue

            file_path = os.path.join(root, filename)

            # Create a corresponding output directory structure inside 'sources/unhandled/'
            relative_path = os.path.relpath(root, base_input_dir)

            if relative_path == ".":
                # Files directly in raw_sources go to sources/unhandled/
                target_dir = unhandled_base_output_dir
            else:
                # Files in subdirectories go to sources/unhandled/subdirectory/
                target_dir = os.path.join(unhandled_base_output_dir, relative_path)

            os.makedirs(target_dir, exist_ok=True)

            _process_text_file(file_path, target_dir, word_limit)


def _process_text_file(fpath, out_dir, word_limit):
    base_name, ext = os.path.splitext(os.path.basename(fpath))
    print(f"  - Processing: {os.path.basename(fpath)}...")

    try:
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
    except Exception as e:
        print(f"    - Could not read file: {e}")
        return

    words = content.split()
    if not words:
        return

    # If the file is within the limit, just copy it
    if len(words) <= word_limit:
        shutil.copy(fpath, os.path.join(out_dir, os.path.basename(fpath)))
        return

    # If the file is too large, split it by line
    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    current_chunk, current_count, counter = [], 0, 1
    for line in lines:
        line_count = len(line.split())
        if current_count + line_count > word_limit and current_chunk:
            with open(
                os.path.join(out_dir, f"{base_name}_part_{counter}{ext}"),
                "w",
                encoding="utf-8",
            ) as f:
                f.writelines(current_chunk)
            print(f"    - Wrote part {counter} for {os.path.basename(fpath)}")
            counter += 1
            current_chunk, current_count = [], 0
        current_chunk.append(line)
        current_count += line_count

    if current_chunk:
        with open(
            os.path.join(out_dir, f"{base_name}_part_{counter}{ext}"),
            "w",
            encoding="utf-8",
        ) as f:
            f.writelines(current_chunk)
        print(f"    - Wrote part {counter} for {os.path.basename(fpath)}")
