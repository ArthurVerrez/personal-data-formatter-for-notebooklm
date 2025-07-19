import csv
import os

def process(config):
    cfg = config['PATHS']['GOOGLE_CONTACTS']
    base_input_dir = config['BASE_INPUT_DIR']
    base_output_dir = config['BASE_OUTPUT_DIR']
    word_limit = config['WORD_LIMIT_PER_FILE']

    contacts_csv_path = os.path.join(base_input_dir, cfg['INPUT_FILE'])
    output_dir = os.path.join(base_output_dir, cfg['OUTPUT_DIR'])
    
    os.makedirs(output_dir, exist_ok=True)
    print(f"\n--- Processing Google Contacts ---")

    all_contacts = []
    with open(contacts_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text, count = _format_contact(row)
            if text: all_contacts.append((text, count))

    _chunk_and_write(output_dir, "formatted_contacts", all_contacts, word_limit)

def _format_contact(c):
    name = " ".join(filter(None, [c.get('First Name'), c.get('Middle Name'), c.get('Last Name')])).strip() or c.get('File As') or "Unnamed"
    lines = [f"## {name}"]
    
    org = f"{c.get('Organization Title', '').strip()} at {c.get('Organization Name', '').strip()}" if c.get('Organization Name') and c.get('Organization Title') else c.get('Organization Name', '').strip()
    if org: lines.append(f"* **Organization**: {org}")

    for i in range(1, 6):
        if c.get(f'E-mail {i} - Value'): lines.append(f"* **{c.get(f'E-mail {i} - Label') or 'Email'}**: {c[f'E-mail {i} - Value']}")
        if c.get(f'Phone {i} - Value'):
            for num in c[f'Phone {i} - Value'].split(' ::: '): lines.append(f"* **{c.get(f'Phone {i} - Label') or 'Phone'}**: {num.strip()}")

    if c.get('Birthday'): lines.append(f"* **Birthday**: {c['Birthday']}")
    if c.get('Notes'): lines.append(f"* **Notes**:\n  > {c['Notes'].strip().replace('\n', '\n  > ')}")
    if c.get('Labels'): lines.append(f"* **Labels**: {c['Labels'].replace('* myContacts', '').replace('*', '').replace(':::', ',').strip()}")
    
    text = "\n".join(lines)
    return text, len(text.split())

def _chunk_and_write(output_dir, base_name, items, word_limit):
    current_chunk, current_count, counter = [], 0, 1
    for text, count in items:
        if current_count + count > word_limit and current_chunk:
            fname = f"{base_name}_{counter}.md"
            with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f: f.write("\n\n---\n\n".join(current_chunk))
            print(f"  - Wrote chunk to {fname} ({current_count} words).")
            counter += 1
            current_chunk, current_count = [], 0
        current_chunk.append(text)
        current_count += count
    
    if current_chunk:
        fname = f"{base_name}.md" if counter == 1 else f"{base_name}_{counter}.md"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f: f.write("\n\n---\n\n".join(current_chunk))
        print(f"  - Wrote final chunk to {fname} ({current_count} words).")
