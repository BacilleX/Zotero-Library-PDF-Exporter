# Zotero Library PDF Exporter

This Python script exports all PDF files from a specified Zotero collection — including its subcollections — by querying the Zotero SQLite database and locating the corresponding files in the local `storage/` directory. The script then copies those files into an organized folder structure for easier backup, migration, or offline access.

---

## 📜 Based on Original Work

This project is based on a script originally written by **Jaime Ruiz Serra**, published as a GitHub Gist:  
🔗 https://gist.github.com/RuizSerra/6a657f6f0b2ce1e5d14a74a29fa68b8d

The original script retrieved files from a Zotero collection and copied them to a destination folder.

---

## ✨ Modifications & Contributions

This version was generated and extended using **OpenAI's ChatGPT**, with my guidance and intent. I used ChatGPT to:

- Add support for nested collections (subfolders)
- Automate folder naming to avoid overwrites
- Improve file discovery logic using `glob`
- Enhance command-line usability with better defaults and documentation

These modifications were implemented through iterative prompts, testing, and manual adjustments.

---

## 🚀 Usage

### Requirements

- Python 3.x
- Local access to your Zotero directory (must include `zotero.sqlite` and `storage/`)

### Run the script

- Don't forget to close Zotero before running the command

```bash
python zotero_exporter.py --zotero-base-path "/Users/you/Zotero" --destination-dir "/Users/you/Downloads/ZoteroBackup"
