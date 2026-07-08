"""Maintain public datasets used for the query monitoring framework.

The script reads `data/dataset_manifest.json`, verifies local assets, and can
refresh missing files. It keeps the pulled CSVs organized under `data/raw/` and
handles archive extraction for the Wi-Fi dataset mirror.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "dataset_manifest.json"


@dataclass
class Dataset:
    name: str
    source_url: str
    local_path: Path
    format: str
    archive_path: Path | None = None


def load_manifest() -> list[Dataset]:
    with MANIFEST.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    datasets: list[Dataset] = []
    for item in payload.get("datasets", []):
        datasets.append(
            Dataset(
                name=item["name"],
                source_url=item["source_url"],
                local_path=ROOT / item["local_path"],
                format=item.get("format", "csv"),
                archive_path=(ROOT / item["archive_path"]) if item.get("archive_path") else None,
            )
        )
    return datasets


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def download(url: str, dest: Path) -> None:
    ensure_parent(dest)
    urllib.request.urlretrieve(url, dest)


def extract_zip(archive_path: Path, extract_dir: Path) -> list[Path]:
    extract_dir.mkdir(parents=True, exist_ok=True)
    extracted: list[Path] = []
    with zipfile.ZipFile(archive_path, "r") as zf:
        for member in zf.namelist():
            if member.endswith("/"):
                continue
            zf.extract(member, extract_dir)
            extracted.append(extract_dir / member)
    return extracted


def verify_dataset(ds: Dataset) -> bool:
    if ds.local_path.exists():
        return True
    if ds.archive_path and ds.archive_path.exists():
        return ds.local_path.exists()
    return False


def sync_dataset(ds: Dataset) -> None:
    if ds.local_path.exists():
        return

    if ds.archive_path is not None:
        if not ds.archive_path.exists():
            download(ds.source_url, ds.archive_path)
        extracted = extract_zip(ds.archive_path, ds.archive_path.parent / "extracted")
        if not ds.local_path.exists() and extracted:
            # Some archives contain a single canonical CSV that we keep as the local asset.
            candidate = next((p for p in extracted if p.suffix.lower() == ".csv"), extracted[0])
            if candidate != ds.local_path:
                ensure_parent(ds.local_path)
                shutil.copy2(candidate, ds.local_path)
        return

    download(ds.source_url, ds.local_path)


def emit_inventory(datasets: Iterable[Dataset]) -> None:
    out = ROOT / "data" / "dataset_inventory.csv"
    ensure_parent(out)
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "local_path", "exists", "size_bytes", "sha256"])
        for ds in datasets:
            exists = ds.local_path.exists()
            size = ds.local_path.stat().st_size if exists else 0
            digest = sha256(ds.local_path) if exists else ""
            writer.writerow([ds.name, str(ds.local_path.relative_to(ROOT)), exists, size, digest])


def main() -> int:
    parser = argparse.ArgumentParser(description="Maintain query-monitoring datasets")
    parser.add_argument("action", choices=["verify", "sync", "inventory"], help="Maintenance action")
    args = parser.parse_args()

    datasets = load_manifest()

    if args.action == "verify":
        failed = [ds.name for ds in datasets if not verify_dataset(ds)]
        if failed:
            print("Missing datasets:")
            for name in failed:
                print(f"- {name}")
            return 1
        print("All datasets are present.")
        return 0

    if args.action == "sync":
        for ds in datasets:
            sync_dataset(ds)
        emit_inventory(datasets)
        print("Datasets synchronized and inventory updated.")
        return 0

    emit_inventory(datasets)
    print("Inventory written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
