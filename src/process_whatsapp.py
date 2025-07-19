import os


def process(config):
    cfg = config["PATHS"]["WHATSAPP"]
    base_input_dir = config["BASE_INPUT_DIR"]
    base_output_dir = config["BASE_OUTPUT_DIR"]

    input_dir = os.path.join(base_input_dir, cfg["INPUT_DIR"])
    output_dir = os.path.join(base_output_dir, cfg["OUTPUT_DIR"])

    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Processing WhatsApp ---")

    for fname in os.listdir(input_dir):
        if fname.endswith(".txt"):
            _process_file(
                os.path.join(input_dir, fname),
                output_dir,
                config["WORD_LIMIT_PER_FILE"],
            )


def _clean_line(line):
    if (
        "Messages and calls are end-to-end encrypted" in line
        or "<Media omitted>" in line
        or line.strip().endswith(": null")
    ):
        return None
    return line.strip()


def _process_file(fpath, out_dir, word_limit):
    base_name = os.path.splitext(os.path.basename(fpath))[0]
    print(f"  - Processing: {os.path.basename(fpath)}...")

    with open(fpath, "r", encoding="utf-8") as f:
        lines = [_clean_line(line) for line in f.readlines()]
    lines = [l for l in lines if l]

    if not lines:
        return

    total_words = len("\n".join(lines).split())
    if total_words <= word_limit:
        with open(
            os.path.join(out_dir, f"{base_name}.txt"), "w", encoding="utf-8"
        ) as f:
            f.write("\n".join(lines))
        return

    current_chunk, current_count, counter = [], 0, 1
    for line in lines:
        line_count = len(line.split())
        if current_count + line_count > word_limit and current_chunk:
            with open(
                os.path.join(out_dir, f"{base_name}_part_{counter}.txt"),
                "w",
                encoding="utf-8",
            ) as f:
                f.write("\n".join(current_chunk))
            counter += 1
            current_chunk, current_count = [], 0
        current_chunk.append(line)
        current_count += line_count

    if current_chunk:
        with open(
            os.path.join(out_dir, f"{base_name}_part_{counter}.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("\n".join(current_chunk))
