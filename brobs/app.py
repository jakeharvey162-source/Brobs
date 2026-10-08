"""BROBS local dashboard. Read-only, loopback-only, no credential inputs."""
import argparse
import json
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .fx import FXBook, FXConfig

def open_book(path):
    import sqlite3
    if Path(path).exists():
        with sqlite3.connect(path) as db:
            if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='fx_state'").fetchone():
                row=db.execute('SELECT data FROM fx_state WHERE id=1').fetchone()
                if row:return FXBook(path,FXConfig(**json.loads(row[0])['config']))
    return FXBook(path)

def make_server(db_path,port=8767):
    book=open_book(db_path)
    page=Path(__file__).with_name('web').joinpath('index.html').read_bytes()
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path not in ('/','/api/state','/health'):self.send_error(404);return
            try:
                if self.path=='/':body=page;mime='text/html; charset=utf-8'
                else:
                    state=book.snapshot()
                    value=state if self.path=='/api/state' else dict(status='ok',runner=state['health'])
                    body=json.dumps(value,allow_nan=False).encode();mime='application/json'
                self.send_response(200)
                for k,v in [('Content-Type',mime),('Content-Length',str(len(body))),('Cache-Control','no-store'),
                    ('X-Content-Type-Options','nosniff'),('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'"),('Referrer-Policy','no-referrer')]:self.send_header(k,v)
                self.end_headers();self.wfile.write(body)
            except (ValueError, OSError):self.send_error(503,'State unavailable')
        def log_message(self,*args):pass
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)

def main():
    p=argparse.ArgumentParser();p.add_argument('--db',default='brobs_fx.db');p.add_argument('--port',type=int,default=8767);a=p.parse_args()
    server=make_server(a.db,a.port);print(f'Open http://127.0.0.1:{server.server_port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
