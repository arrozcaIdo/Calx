# =====================================================================
# Calx Web Server
# =====================================================================

import http.server
import socketserver
import json
import os
from calx_lexer import CalxLexer, LexicalError

PORT = 8000

class CalxRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/tokenize':
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_body.decode('utf-8'))
                code = data.get('code', '')
                
                lexer = CalxLexer(code)
                tokens = lexer.tokenize()

                tokens_dict = [
                    {
                        "type": t.type,
                        "value": t.value,
                        "line": t.line,
                        "column": t.column
                    }
                    for t in tokens
                ]
                response_payload = {
                    "success": True,
                    "tokens": tokens_dict
                }
            except (LexicalError, IndentationError) as err:
                response_payload = {
                    "success": False,
                    "error_type": err.__class__.__name__,
                    "error": str(err)
                }
            except Exception as e:
                response_payload = {
                    "success": False,
                    "error_type": "ServerError",
                    "error": str(e)
                }
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_payload).encode('utf-8'))
        else:
            self.send_error(404, "Endpoint not found")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == '__main__':
    # Serve files from the current directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), CalxRequestHandler) as httpd:
        print(f"\n=======================================================")
        print(f"  Calx Interactive Lexical Analyzer Web Terminal")
        print(f"  Running at: http://localhost:{PORT}")
        print(f"  Backend: calx_lexer.py")
        print(f"=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
