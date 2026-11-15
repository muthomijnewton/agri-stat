import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'overpass-download.sh'
DATA = b'realistic binary fixture\x00' * 10000

class ResumeDownloadTest(unittest.TestCase):
    def run_download(self, legacy=None, drop=False):
        requests = []
        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_HEAD(self):
                if self.path == '/latest.pbf':
                    self.send_response(302); self.send_header('Location', '/dated.pbf')
                else: self.send_response(200)
                self.end_headers()
            def do_GET(self):
                if self.path.endswith('.md5'):
                    body = (hashlib.md5(DATA).hexdigest() + '  dated.pbf\n').encode()
                    self.send_response(200); self.send_header('Content-Length', str(len(body))); self.end_headers(); self.wfile.write(body); return
                start = int(self.headers.get('Range', 'bytes=0-').split('=')[1].split('-')[0])
                requests.append(start)
                if start >= len(DATA):
                    self.send_response(416); self.end_headers(); return
                self.send_response(206 if start else 200)
                self.send_header('Content-Length', str(len(DATA)-start))
                if start: self.send_header('Content-Range', f'bytes {start}-{len(DATA)-1}/{len(DATA)}')
                self.end_headers()
                body = DATA[start:]
                if drop and len(requests) == 1: body = body[:len(body)//2]
                self.wfile.write(body)
                self.close_connection = True
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                if legacy is not None: (root/'planet.osm.bz2').write_bytes(legacy)
                env = dict(os.environ, OVERPASS_DB_DIR=directory, OVERPASS_PLANET_URL=f'http://127.0.0.1:{server.server_port}/latest.pbf', OVERPASS_DOWNLOAD_RETRY_DELAY='0')
                result = subprocess.run(['bash', '-e', '-c', 'source "$1"', 'test', str(SCRIPT)], env=env, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
                self.assertEqual((root/'download-cache/kenya.osm.pbf').read_bytes(), DATA)
                self.assertTrue((root/'download-cache/source.url').read_text().endswith('/dated.pbf'))
                return requests
        finally: server.shutdown(); server.server_close(); thread.join()
    def test_connection_reset_resumes_partial(self):
        requests = self.run_download(drop=True)
        self.assertEqual(requests, [0, len(DATA)//2])
    def test_existing_partial_is_kept(self):
        self.assertEqual(self.run_download(legacy=DATA[:1234]), [1234])
    def test_incompatible_legacy_file_is_replaced_only_after_validation(self):
        self.assertEqual(self.run_download(legacy=b'x'*(len(DATA)+10)), [len(DATA)+10, 0])

if __name__ == '__main__': unittest.main()
