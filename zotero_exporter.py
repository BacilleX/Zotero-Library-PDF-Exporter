"""
This script copies the entire Zotero library, preserving collection and subcollection structure,
including all attached PDF files. The files are copied into a new folder that mirrors the
collection hierarchy.

Usage:
    python3 zotero_exporter.py --zotero-base-path "/Users/you/Zotero" --destination-dir "directoryname"

Author: Adapted by ChatGPT, based on Jaime Ruiz Serra's script, published as a GitHub Gist: https://gist.github.com/RuizSerra/6a657f6f0b2ce1e5d14a74a29fa68b8d
"""

import sqlite3
import os
import shutil
import glob
import argparse

def get_collection_tree(cursor):
    cursor.execute("SELECT collectionID, collectionName, parentCollectionID FROM collections")
    rows = cursor.fetchall()
    tree = {}
    for col_id, name, parent_id in rows:
        tree[col_id] = {"name": name, "parent": parent_id, "children": []}
    for col_id, info in tree.items():
        parent_id = info["parent"]
        if parent_id in tree:
            tree[parent_id]["children"].append(col_id)
    return tree

def build_collection_path(tree, col_id):
    path_parts = []
    current = col_id
    while current:
        path_parts.insert(0, tree[current]["name"].replace("/", "_"))
        current = tree[current]["parent"]
    return os.path.join(*path_parts)

def get_item_ids_for_collection(cursor, col_id):
    cursor.execute("SELECT itemID FROM collectionItems WHERE collectionID = ?", (col_id,))
    return [row[0] for row in cursor.fetchall()]

def get_pdf_attachments(cursor, item_ids):
    if not item_ids:
        return []
    placeholders = ','.join('?' * len(item_ids))
    cursor.execute(
        f'''
        SELECT path FROM itemAttachments 
        WHERE parentItemID IN ({placeholders})
        AND contentType LIKE '%pdf'
        ''',
        item_ids
    )
    return [
        row[0].replace("storage:", "", 1)
        for row in cursor.fetchall()
        if row[0]
    ]

def find_file(storage_path, filename):
    matches = glob.glob(f"{storage_path}/**/{filename}", recursive=True)
    return matches[0] if matches else None

def copy_files(files, storage_path, dest_dir):
    os.makedirs(dest_dir, exist_ok=True)
    for filename in files:
        src_file = find_file(storage_path, filename)
        if src_file:
            shutil.copy(src_file, dest_dir)

def process_collection(cursor, tree, col_id, storage_path, dest_base_dir):
    collection_rel_path = build_collection_path(tree, col_id)
    dest_dir = os.path.join(dest_base_dir, collection_rel_path)

    item_ids = get_item_ids_for_collection(cursor, col_id)
    attachments = get_pdf_attachments(cursor, item_ids)
    copy_files(attachments, storage_path, dest_dir)

    for child_id in tree[col_id]["children"]:
        process_collection(cursor, tree, child_id, storage_path, dest_base_dir)

def main(zotero_base_path, destination_dir):
    database_path = os.path.join(zotero_base_path, "zotero.sqlite")
    storage_path = os.path.join(zotero_base_path, "storage")

    if not os.path.exists(database_path):
        raise FileNotFoundError(f"Zotero database not found at {database_path}")

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    tree = get_collection_tree(cursor)
    root_collections = [cid for cid, info in tree.items() if info["parent"] is None]

    for col_id in root_collections:
        process_collection(cursor, tree, col_id, storage_path, destination_dir)

    conn.close()
    print(f"Zotero library copied to: {destination_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Copy Zotero library with full collection hierarchy.")
    parser.add_argument(
        "--zotero-base-path",
        required=True,
        help="Path to Zotero data directory (contains zotero.sqlite and 'storage')."
    )
    parser.add_argument(
        "--destination-dir",
        required=True,
        help="Destination directory where Zotero collection structure will be copied."
    )
    args = parser.parse_args()
    main(args.zotero_base_path, args.destination_dir)

