"""Canonical, gap-checked merge of locally downloaded public crypto history."""
import argparse,csv,hashlib,json
from pathlib import Path
from .history import load_csv

def merge(inputs,output):
    rows=[];records=[];symbols=set();currencies=set()
    for name in inputs:
        p=Path(name);meta=json.loads(p.with_suffix('.provenance.json').read_text())
        symbols.add(meta['symbol']);currencies.add(meta['quote_currency'])
        rows.extend(load_csv(p));records.append(dict(file=p.name,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),sources=meta['sources']))
    if len(symbols)!=1 or currencies!={'USDT'}:raise ValueError('Source symbols or quote currencies differ')
    rows.sort(key=lambda r:r['timestamp'])
    if any((b['timestamp']-a['timestamp']).total_seconds()!=3600 for a,b in zip(rows,rows[1:])):raise ValueError('Duplicate or noncontiguous hourly bars')
    p=Path(output);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['timestamp','open','high','low','close','volume']);w.writeheader()
        for row in rows:w.writerow({**row,'timestamp':row['timestamp'].isoformat()})
    result=dict(symbol=next(iter(symbols)),quote_currency='USDT',rows=len(rows),input_files=records,
        normalized_csv_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),note='Canonical float/UTC CSV merge of checksum-verified archive downloads; no synthetic bars. Local input hashes and archive provenance retained.')
    p.with_suffix('.provenance.json').write_text(json.dumps(result,indent=2)+'\n');return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--inputs',nargs='+',required=True);p.add_argument('--output',required=True);a=p.parse_args();r=merge(a.inputs,a.output)
    print(json.dumps({k:v for k,v in r.items() if k!='input_files'}))
if __name__=='__main__':main()
