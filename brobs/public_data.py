"""Download checksum-verified Binance public hourly archives, no credentials/orders."""
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from datetime import datetime,timezone
from pathlib import Path
from .history import load_csv

BASE='https://data.binance.vision/data/spot/monthly/klines'

def normalize_archive(data):
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names=archive.namelist()
        if len(names)!=1 or not names[0].endswith('.csv') or archive.getinfo(names[0]).file_size>2000000:
            raise ValueError('Unexpected archive contents')
        raw=archive.read(names[0]).decode()
    rows=[]
    for values in csv.reader(io.StringIO(raw)):
        stamp=int(values[0]);seconds=stamp/(1000000 if stamp>=10**14 else 1000)
        rows.append([datetime.fromtimestamp(seconds,timezone.utc).isoformat()]+values[1:6])
    return rows

def fetch_bytes(url):
    with urllib.request.urlopen(url,timeout=20) as r:
        data=r.read(2000001)
    if len(data)>2000000:raise ValueError('Archive too large')
    return data

def download(symbol,months,output,fetch=fetch_bytes):
    if symbol not in ('BTCUSDT','ETHUSDT'):raise ValueError('Only BTCUSDT/ETHUSDT archives enabled')
    rows=[];sources=[]
    ordered=sorted(set(months))
    if not ordered:raise ValueError('At least one month required')
    for month in ordered:
        if not re.fullmatch(r'20\d{2}-(0[1-9]|1[0-2])',month):raise ValueError('Month must be YYYY-MM')
    urls=[f'{BASE}/{symbol}/1h/{symbol}-1h-{month}.zip'+suffix for month in ordered for suffix in ('','.CHECKSUM')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        cache=dict(zip(urls,pool.map(fetch,urls)))
    for month in ordered:
        if not re.fullmatch(r'20\d{2}-(0[1-9]|1[0-2])',month):raise ValueError('Month must be YYYY-MM')
        url=f'{BASE}/{symbol}/1h/{symbol}-1h-{month}.zip'
        data=cache[url];expected=cache[url+'.CHECKSUM'].decode().split()[0]
        digest=hashlib.sha256(data).hexdigest()
        if expected!=digest:raise ValueError('Archive checksum mismatch')
        rows.extend(normalize_archive(data));sources.append(dict(url=url,sha256=digest))
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    # Validate before publishing the requested output.
    import tempfile
    with tempfile.TemporaryDirectory() as folder:
        candidate=Path(folder)/'prices.csv'
        with candidate.open('w',newline='') as f:
            w=csv.writer(f);w.writerow(['timestamp','open','high','low','close','volume']);w.writerows(rows)
        loaded=load_csv(candidate)
        if any((b['timestamp']-a['timestamp']).total_seconds()!=3600 for a,b in zip(loaded,loaded[1:])):
            raise ValueError('Hourly series has gaps; request consecutive months')
        p.write_bytes(candidate.read_bytes())
    provenance=dict(symbol=symbol,quote_currency='USDT',rows=len(rows),sources=sources,
        note='Public Binance spot historical klines. USDT is not USD; results are in USDT. No synthetic bars or precomputed indicators. Checksums prove file integrity, not future trading performance.')
    p.with_suffix('.provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
    return provenance

def main():
    p=argparse.ArgumentParser();p.add_argument('--symbol',choices=['BTCUSDT','ETHUSDT'],default='BTCUSDT');p.add_argument('--months',nargs='+',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    print(json.dumps(download(a.symbol,a.months,a.output),indent=2))
if __name__=='__main__':main()
