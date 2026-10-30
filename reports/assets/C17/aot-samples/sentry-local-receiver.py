import http.server, gzip, json, sys, zlib
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get('Content-Length',0)); b=self.rfile.read(n)
        enc=self.headers.get('Content-Encoding','')
        if enc=='gzip': b=gzip.decompress(b)
        elif enc=='deflate': b=zlib.decompress(b)
        elif enc=='br': pass
        open(sys.argv[1],'ab').write(b+b'\n----\n')
        self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b'{}')
    def log_message(self,*a): pass
http.server.HTTPServer(('127.0.0.1',8765),H).serve_forever()
