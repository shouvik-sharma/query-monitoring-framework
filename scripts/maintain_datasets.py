"""Maintain public datasets used for the query monitoring framework.

The script reads `data/dataset_manifest.json`, verifies local assets, and can
refresh missing files. It keeps the pulled CSVs organized under `data/raw/` and
handles archive extraction for the Wi-Fi dataset mirror and UCI Online Retail
xlsx-to-CSV conversion.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import urllib.request
import zipfile
from dataclasses import dataclass, field
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
    derived_tables: dict[str, str] = field(default_factory=dict)


def load_manifest() -> list[Dataset]:
    with MANIFEST.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    datasets: list[Dataset] = []
    for item in payload.get("datasets", []):
        derived = item.get("derived_tables", {})
        datasets.append(
            Dataset(
                name=item["name"],
                source_url=item["source_url"],
                local_path=ROOT / item["local_path"],
                format=item.get("format", "csv"),
                archive_path=(ROOT / item["archive_path"]) if item.get("archive_path") else None,
                derived_tables={k: str(ROOT / v) for k, v in derived.items()},
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


def convert_xlsx_to_csv(xlsx_path: Path, products_csv: Path, orders_csv: Path) -> None:
    """Convert UCI Online Retail xlsx to products.csv and orders.csv."""
    import openpyxl

    print(f"  Converting {xlsx_path.name} to CSV...")

    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active

    rows = list(ws.iter_rows(values_only=True))
    header = [str(c).strip() if c else f"col_{i}" for i, c in enumerate(rows[0])]
    data_rows = rows[1:]

    print(f"  Read {len(data_rows)} rows from xlsx")

    # Build products table: unique StockCode -> product details
    products: dict[str, dict] = {}
    orders: list[dict] = []

    for row in data_rows:
        if len(row) < 8:
            continue
        inv_no, stock_code, description, qty, inv_date, unit_price, cust_id, country = row[:8]

        if inv_no is None or stock_code is None:
            continue
        inv_no = str(inv_no).strip()
        stock_code = str(stock_code).strip()

        # Skip cancelled orders (InvoiceNo starting with 'C')
        if inv_no.startswith("C") or inv_no.startswith("c"):
            continue

        # Skip rows with non-numeric quantities or prices
        try:
            qty = int(qty) if qty else 0
            price = float(unit_price) if unit_price else 0.0
        except (ValueError, TypeError):
            continue

        if qty <= 0 or price <= 0:
            continue

        # Collect product info
        if stock_code not in products:
            products[stock_code] = {
                "product_id": stock_code,
                "product_name": str(description).strip() if description else f"Product {stock_code}",
                "category": "General",
                "price": price,
                "stock_qty": max(100, qty),
            }
        else:
            products[stock_code]["stock_qty"] += qty

        # Build order row
        cust_id_str = str(int(cust_id)) if cust_id and cust_id != "None" else "0"
        orders.append({
            "order_id": inv_no,
            "customer_id": cust_id_str,
            "total_amount": round(qty * price, 2),
            "order_date": str(inv_date)[:10] if inv_date else "2011-01-01",
            "status": "completed",
        })

    wb.close()

    # Write products.csv
    ensure_parent(products_csv)
    with products_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "price", "stock_qty"])
        writer.writeheader()
        for p in products.values():
            writer.writerow(p)
    print(f"  Wrote {len(products)} products to {products_csv.name}")

    # Write orders.csv
    ensure_parent(orders_csv)
    with orders_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["order_id", "customer_id", "total_amount", "order_date", "status"])
        writer.writeheader()
        for o in orders:
            writer.writerow(o)
    print(f"  Wrote {len(orders)} orders to {orders_csv.name}")


def verify_dataset(ds: Dataset) -> bool:
    if ds.local_path.exists():
        if ds.derived_tables:
            return all(Path(p).exists() for p in ds.derived_tables.values())
        return True
    if ds.archive_path and ds.archive_path.exists():
        if ds.derived_tables:
            return all(Path(p).exists() for p in ds.derived_tables.values())
        return ds.local_path.exists()
    return False


def sync_dataset(ds: Dataset) -> None:
    if ds.local_path.exists() and (not ds.derived_tables or all(Path(p).exists() for p in ds.derived_tables.values())):
        return

    if ds.archive_path is not None:
        if not ds.archive_path.exists():
            download(ds.source_url, ds.archive_path)
        extracted = extract_zip(ds.archive_path, ds.archive_path.parent / "extracted")
        if not ds.local_path.exists() and extracted:
            # Find the xlsx or csv file in extracted contents
            candidate = next(
                (p for p in extracted if p.suffix.lower() in (".csv", ".xlsx")),
                extracted[0]
            )
            if candidate != ds.local_path:
                ensure_parent(ds.local_path)
                shutil.copy2(candidate, ds.local_path)
        return

    download(ds.source_url, ds.local_path)


def sync_derived_tables(ds: Dataset) -> None:
    """Convert source file to derived CSV tables if needed."""
    if not ds.derived_tables:
        return
    if all(Path(p).exists() for p in ds.derived_tables.values()):
        return

    if ds.format == "xlsx" and ds.local_path.exists():
        products_csv = Path(ds.derived_tables["products"])
        orders_csv = Path(ds.derived_tables["orders"])
        convert_xlsx_to_csv(ds.local_path, products_csv, orders_csv)


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
            sync_derived_tables(ds)
        emit_inventory(datasets)
        print("Datasets synchronized and inventory updated.")
        return 0

    emit_inventory(datasets)
    print("Inventory written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
