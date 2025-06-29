import hashlib
import os


def get_latest_version(folder, prefix):
    files = os.listdir(folder)
    files = [f for f in files if f.startswith(prefix) and f.endswith('.jsonl')]
    if not files:
        raise ValueError(f"No files found with prefix '{prefix}' in folder '{folder}'")

    return max([f[len(prefix):-6] for f in files])


def compute_hash(path):
    with open(path, 'r', encoding='utf-8') as f:
        msg = f.read()
        return hashlib.md5(msg.encode()).hexdigest()

def valid_file(path):
    path_hash = path + ".hash"
    if not os.path.exists(path) or not os.path.exists(path_hash):
        return False

    with open(path_hash, 'r', encoding='utf-8') as f:
        res = compute_hash(path) == f.read()
        if not res:
            print(f"Hash mismatch for '{path}'")

        return res
    
def generate_hash(path):
    path_hash = path + ".hash"
    with open(path_hash, 'w', encoding='utf-8') as f:
        f.write(compute_hash(path))