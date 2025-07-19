# Personal Data Formatter for NotebookLM

A Python utility to parse and format personal data exports from various services (Google Contacts, Messenger, WhatsApp, etc.) into clean, word-count-limited files, ready for use with [NotebookLM](https://notebooklm.google.com/) that can handle up to 500k sources.

## Setup

### 1. Prerequisites

- Python 3.8+

### 2. Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/ArthurVerrez/personal-data-formatter-for-notebooklm
cd personal-data-formatter-for-notebooklm
python -m venv env
# On Windows, use: env\Scripts\activate
# On macOS/Linux, use the following command:
source env/bin/activate
pip install -r requirements.txt
```

## How to Use

### Step 1: Place Your Data Exports

Place your exported data into the corresponding folders within the `raw_sources/` directory. The script will automatically detect which data sources are present.

- **ChatGPT**: Place `conversations.json` in `raw_sources/chatgpt/`.

  - _Export via `Settings` \> `Data controls` \> `Export data`._

- **Google Contacts**: Place `contacts.csv` in `raw_sources/google_contacts/`.

  - _Export from [Google Contacts](https://contacts.google.com/) using the "Google CSV" format._

- **Google Keep**: Place all exported `.json` files in `raw_sources/google_keep/`.

  - _Export from [Google Takeout](https://takeout.google.com/), selecting only Keep._

- **Google Tasks**: Place `Tasks.json` in `raw_sources/google_tasks/`.

  - _Export from [Google Takeout](https://takeout.google.com/), selecting only Tasks._

- **Messenger & Instagram**: Place the contents of your `inbox`, `archived_threads`, and `message_requests` folders into `raw_sources/messenger/` and `raw_sources/instagram/`.

  - _Export from the [Meta Accounts Center](https://accountscenter.facebook.com/info_and_permissions/dyi) by requesting your "Messages" in JSON format._

- **WhatsApp**: Place your exported `.txt` chat files in `raw_sources/whatsapp/`.

  - _Export individual chats via `More` \> `Export chat` \> "Without media"._

- **Other Files**: Any other files or folders you place in `raw_sources/` will be treated as plain text, copied as-is, and split by word count.

### Step 2: Configure

Open `config.yaml` and update the `EXPORT_OWNER_NAMES` list with all possible names you use across different platforms (e.g., "Arthur Verrez", "Arthur"). This is crucial for correctly formatting chat logs.

### Step 3: Run the Script

Execute the main script from the root of the project:

```bash
python main.py
```

The script will process all available data and generate two directories:

1.  `/sources/`: Contains the formatted files, organized into subdirectories for each data source.
2.  `/sources-to-copy/`: Contains a flat copy of all generated files, ready for easy drag-and-drop into NotebookLM.
