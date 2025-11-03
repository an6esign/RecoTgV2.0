# /app/src/services/etl/load_csv.py
import os
import csv
import asyncio
from typing import Tuple, List, Dict

import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table
from sqlalchemy import Integer, BigInteger, SmallInteger, Boolean, Float, Numeric, Date, DateTime, String, Text

# --- настройки ---
CSV_DIR = "/app/src/services/etl/app/data"      # папка с CSV
TABLE_NAME = "channels"                          # целевая таблица
DATABASE_URL = "postgresql+asyncpg://recotg:recopassword@db:5432/recotg_db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
CANDIDATE_DELIMS = [",", ";", "\t", "|"]


# ---------------- CSV utils ----------------
def sniff_delimiter(path: str) -> str:
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        sample = f.read(100_000)
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters="".join(CANDIDATE_DELIMS))
        return dialect.delimiter
    except Exception:
        header = sample.splitlines()[0] if sample else ""
        best = ","
        best_cnt = header.count(best)
        for d in CANDIDATE_DELIMS:
            cnt = header.count(d)
            if cnt > best_cnt:
                best, best_cnt = d, cnt
        return best


def read_csv_strict(path: str) -> Tuple[pd.DataFrame, List[Dict]]:
    """Читает CSV, отбрасывая строки с неправильным числом столбцов."""
    delim = sniff_delimiter(path)
    bad: List[Dict] = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delim, quotechar='"', escapechar="\\")
        try:
            header = next(reader)
        except StopIteration:
            return pd.DataFrame(), bad
        n_cols = len(header)
        good_rows: List[List[str]] = []
        for row in reader:
            if len(row) == n_cols:
                good_rows.append(row)
            else:
                bad.append({
                    "line_num": reader.line_num,
                    "reason": f"expected {n_cols} columns, got {len(row)}",
                    "reconstructed_row": delim.join(row),
                })
    df = pd.DataFrame(good_rows, columns=header)
    return df, bad


def write_bad_file(original_path: str, bad_rows: List[Dict]) -> str | None:
    if not bad_rows:
        return None
    bad_path = original_path + ".bad.csv"
    with open(bad_path, "w", encoding="utf-8", newline="") as bf:
        w = csv.writer(bf)
        w.writerow(["line_num", "reason", "reconstructed_row"])
        for item in bad_rows:
            w.writerow([item["line_num"], item["reason"], item["reconstructed_row"]])
    return bad_path


# ---------------- helpers ----------------
def _parse_subscribers(val):
    if pd.isna(val):
        return pd.NA
    s = str(val).strip().lower()
    s = s.replace(" ", "").replace(",", ".")
    s = s.replace("к", "k").replace("м", "m")
    if s.count(".") > 1:
        first = s.find(".")
        s = s[:first + 1] + s[first + 1:].replace(".", "")
    mult = 1
    if s.endswith("k"):
        mult, s = 1_000, s[:-1]
    elif s.endswith("m"):
        mult, s = 1_000_000, s[:-1]
    try:
        return int(float(s) * mult)
    except Exception:
        return pd.NA


# ---------------- DB utils ----------------
def _coerce_df_to_table_schema(df: pd.DataFrame, table) -> pd.DataFrame:
    df = df.copy()
    for col in table.columns:
        name = col.name
        if name not in df.columns:
            continue
        coltype = col.type

        if isinstance(coltype, (Integer, BigInteger, SmallInteger)):
            df[name] = pd.to_numeric(df[name], errors="coerce").astype("Int64")

        elif isinstance(coltype, (Float, Numeric)):
            df[name] = pd.to_numeric(df[name], errors="coerce")

        elif isinstance(coltype, Boolean):
            df[name] = (
                df[name]
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({
                    "true": True, "t": True, "1": True, "yes": True, "y": True,
                    "false": False, "f": False, "0": False, "no": False, "n": False,
                    "none": np.nan, "nan": np.nan, "": np.nan
                })
            )

        elif isinstance(coltype, Date):
            df[name] = pd.to_datetime(df[name], errors="coerce").dt.date

        elif isinstance(coltype, DateTime):
            df[name] = pd.to_datetime(df[name], errors="coerce")

        elif isinstance(coltype, (String, Text)):
            df[name] = df[name].where(~pd.isna(df[name]), None)

        else:
            df[name] = df[name].where(~pd.isna(df[name]), None)

    return df


def _rows_with_nones(df: pd.DataFrame, cols: List[str]) -> List[dict]:
    records = df[cols].to_dict(orient="records")
    for r in records:
        for k, v in list(r.items()):
            if v is pd.NA or (isinstance(v, float) and np.isnan(v)):
                r[k] = None
    return records


def _upsert_direct_sync(conn, df: pd.DataFrame, table_name: str):
    """UPSERT по username."""
    md = MetaData()
    table = Table(table_name, md, autoload_with=conn)
    pk = "username"

    if pk not in df.columns:
        raise RuntimeError("Ожидается колонка 'username' для UPSERT.")

    # убираем столбец id, если есть
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    # только колонки, существующие в таблице
    table_cols = [c.name for c in table.columns]
    use_cols = [c for c in table_cols if c in df.columns]

    # приведение типов
    df = _coerce_df_to_table_schema(df, table)

    # дедуп по username
    before = len(df)
    df = df.drop_duplicates(subset=[pk], keep="last").copy()
    if before != len(df):
        print(f"🧹 Drop duplicates по {pk}: {before} -> {len(df)}")

    rows = _rows_with_nones(df, use_cols)
    if not rows:
        return

    from sqlalchemy.dialects.postgresql import insert as pg_insert
    chunk = 1000
    for i in range(0, len(rows), chunk):
        part = rows[i:i + chunk]
        stmt = pg_insert(table).values(part)
        update_cols = {c: stmt.excluded[c] for c in use_cols if c != pk}
        stmt = stmt.on_conflict_do_update(index_elements=[table.c[pk]], set_=update_cols)
        conn.execute(stmt)


# ---------------- main ----------------
async def main():
    frames: List[pd.DataFrame] = []
    bad_summary: List[Tuple[str, int, str | None]] = []
    total_rows = 0

    for fname in sorted(os.listdir(CSV_DIR)):
        if not fname.lower().endswith(".csv"):
            continue
        fpath = os.path.join(CSV_DIR, fname)
        df, bad_rows = read_csv_strict(fpath)
        bad_path = write_bad_file(fpath, bad_rows)
        bad_summary.append((fname, len(bad_rows), bad_path))
        total_rows += len(df)
        frames.append(df)
        print(f"{'⚠️' if bad_rows else '✅'} {fname}: проблемных строк — {len(bad_rows)}")

    if not frames:
        raise RuntimeError("Нет успешно прочитанных CSV в директории.")

    all_cols = sorted(set().union(*[set(df.columns) for df in frames]))
    frames = [df.reindex(columns=all_cols) for df in frames]
    big_df = pd.concat(frames, ignore_index=True)

    # фильтр subscribers > 30 000
    if "subscribers" in big_df.columns:
        subs_num = big_df["subscribers"].apply(_parse_subscribers)
        big_df = big_df.assign(_subs=subs_num)
        before_cnt = len(big_df)
        big_df = big_df[big_df["_subs"].notna() & (big_df["_subs"] > 30_000)].copy()
        big_df["subscribers"] = big_df["_subs"].astype(int)
        big_df.drop(columns=["_subs"], inplace=True)
        print(f"🔎 Фильтр subscribers>30000: {before_cnt} -> {len(big_df)}")
    else:
        print("⚠️ Колонка 'subscribers' не найдена — фильтр не применён.")

    print("Dtypes перед UPSERT:")
    print(big_df.dtypes)

    async with engine.begin() as conn:
        await conn.run_sync(lambda sc: _upsert_direct_sync(sc, big_df, TABLE_NAME))

    print("\n===== Итог =====")
    print(f"Таблица: {TABLE_NAME}")
    print(f"Строк обработано: {len(big_df)} (good≈{total_rows})")
    print(f"Колонки: {list(big_df.columns)}")
    print("\nФайлы с проблемными строками:")
    for fname, cnt, path in bad_summary:
        if cnt > 0:
            print(f"  - {fname}: {cnt} строк → {path}")
    print("  — готово.")


if __name__ == "__main__":
    asyncio.run(main())
