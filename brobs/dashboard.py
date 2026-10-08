"""Read-only local dashboard for an exported JSON backtest report."""
import argparse,json,html
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path

class Handler(BaseHTTPRequestHandler):
    report_path=None
    def do_GET(self):
        if self.path not in ("/","/report.json"):
            self.send_error(404);return
        try: report=json.loads(Path(self.report_path).read_text())
        except (OSError,ValueError): self.send_error(503,"Report unavailable");return
        if self.path=="/report.json":
            body=json.dumps(report).encode();ctype="application/json"
        else:
            cells="".join("<tr><th>"+html.escape(str(k))+"</th><td>"+html.escape(str(v))+"</td></tr>" for k,v in report.items())
            body=("<!doctype html><meta name='viewport' content='width=device-width'><title>BROBS AI</title><style>body{background:#0b1220;color:#dfffee;font:18px system-ui;max-width:800px;margin:8vh auto;padding:20px}table{width:100%;border-collapse:collapse}td,th{text-align:left;padding:14px;border-bottom:1px solid #304b4b}h1{color:#54e7ac}</style><h1>BROBS AI</h1><p>Historical research report — no live trading</p><table>"+cells+"</table>").encode();ctype="text/html; charset=utf-8"
        self.send_response(200);self.send_header("Content-Type",ctype);self.send_header("Content-Length",str(len(body)));self.end_headers();self.wfile.write(body)

def main():
    p=argparse.ArgumentParser();p.add_argument("--report",required=True);p.add_argument("--port",type=int,default=8765);a=p.parse_args()
    Handler.report_path=a.report
    print("Dashboard: http://127.0.0.1:"+str(a.port))
    HTTPServer(("127.0.0.1",a.port),Handler).serve_forever()
if __name__=="__main__":main()
