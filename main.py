import yaml
import os
import shutil
from src import (
    process_chatgpt,
    process_google_contacts,
    process_google_keep,
    process_google_tasks,
    process_messenger_instagram,
    process_whatsapp,
    process_unhandled,
)


def copy_sources_to_flat_directory(config):
    """Copies all generated files from the structured sources dir to a flat dir."""
    base_output_dir = config["BASE_OUTPUT_DIR"]
    flat_output_dir = config["FLAT_OUTPUT_DIR"]

    if not os.path.exists(base_output_dir):
        print(f"Source directory '{base_output_dir}' not found. Nothing to copy.")
        return

    # This function already cleans its own directory, so this is robust
    if os.path.exists(flat_output_dir):
        shutil.rmtree(flat_output_dir)
    os.makedirs(flat_output_dir, exist_ok=True)

    print(f"\n--- Copying all generated files to '{flat_output_dir}' ---")

    copy_count = 0
    for root, _, files in os.walk(base_output_dir):
        for file in files:
            if file.endswith((".md", ".txt")):
                source_path = os.path.join(root, file)
                shutil.copy(source_path, flat_output_dir)
                copy_count += 1

    print(f"Copied {copy_count} files.")


def main():
    """
    Main orchestrator to run all data processing scripts based on the config file.
    """
    print("--- Starting Personal Data Aggregation Process ---")

    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("FATAL: config.yaml not found.")
        return
    except yaml.YAMLError as e:
        print(f"FATAL: Error parsing config.yaml: {e}")
        return

    base_output_dir = config["BASE_OUTPUT_DIR"]
    flat_output_dir = config["FLAT_OUTPUT_DIR"]

    # --- Clean up previous output before starting ---
    print(
        f"--- Clearing output directories: '{base_output_dir}' and '{flat_output_dir}' ---"
    )
    if os.path.exists(base_output_dir):
        shutil.rmtree(base_output_dir)
    if os.path.exists(flat_output_dir):
        shutil.rmtree(flat_output_dir)

    # Recreate the base output directory for processing modules
    os.makedirs(base_output_dir)
    # -----------------------------------------------

    base_input_dir = config["BASE_INPUT_DIR"]

    # --- Run each processing module if its source data exists ---

    if os.path.exists(
        os.path.join(base_input_dir, config["PATHS"]["CHATGPT"]["INPUT_FILE"])
    ):
        process_chatgpt.process(config)

    if os.path.exists(
        os.path.join(base_input_dir, config["PATHS"]["GOOGLE_CONTACTS"]["INPUT_FILE"])
    ):
        process_google_contacts.process(config)

    if os.path.exists(
        os.path.join(base_input_dir, config["PATHS"]["GOOGLE_KEEP"]["INPUT_DIR"])
    ):
        process_google_keep.process(config)

    if os.path.exists(
        os.path.join(base_input_dir, config["PATHS"]["GOOGLE_TASKS"]["INPUT_FILE"])
    ):
        process_google_tasks.process(config)

    process_messenger_instagram.process(config)

    if os.path.exists(
        os.path.join(base_input_dir, config["PATHS"]["WHATSAPP"]["INPUT_DIR"])
    ):
        process_whatsapp.process(config)

    # --- Process any remaining files ---
    process_unhandled.process(config)

    # --- Final Step: Copy all sources to a flat directory ---
    copy_sources_to_flat_directory(config)

    print("\n--- All processing complete. ---")


if __name__ == "__main__":
    main()
