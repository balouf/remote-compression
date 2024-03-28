from pathlib import Path
import gzip
from remote_compression.settings import default_extensions
from remote_compression.compression import compress
import dill as pickle

log_keep = ".keep"


def get_files_and_subdirs(path):
    path = Path(path)
    entries = [e for e in path.iterdir()]
    files = [f for f in entries if f.suffix in default_extensions and f.is_file()]
    dirs = [d for d in entries if d.is_dir()]
    return files, dirs


def get_keeps(path):
    keep_file = path / log_keep
    if keep_file.exists():
        print(f"Reading from {keep_file}")
        with gzip.open(keep_file, 'rb') as f:
            return pickle.load(f)
    return set()


def recurse(path, settings):
    keeps = get_keeps(path)
    files, dirs = get_files_and_subdirs(path)
    f_names = {f.name: f for f in files}
    keeps = {k for k in keeps if k in f_names}
    for name, file in f_names.items():
        if name not in keeps:
            keeps.update(compress(file, settings))
    keep_file = path / log_keep
    if len(keeps) > 0:
        with gzip.open(keep_file, 'wb') as f:
            pickle.dump(keeps, f)
    elif keep_file.exists():
        keep_file.unlink()
    print(f"Directory {path} processed.")
    for subd in dirs:
        recurse(subd, settings)
