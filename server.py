# web server (PORT: 8800)

import http.server
import socketserver
import json
import os
from calx_lexer import tokenize, LexicalError

PORT = 8000


class CalxRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/tokenize':
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length)

            try:
                data = json.loads(post_body.decode('utf-8'))
                code = data.get('code', '')

                # Returns [(token_type, lexeme), ...]
                tokens = tokenize(code)
                token_list = [{"type": t[0], "value": t[1]} for t in tokens]
                
                tokens_dict = [
                    {
                        "type": tok_type,
                        "value": tok_val
                    }
                    for tok_type, tok_val in tokens
                ]

                response_payload = {
                    "success": True,
                    "tokens": tokens_dict
                }

            except LexicalError as err:
                response_payload = {
                    "success": False,
                    "error_type": "LexicalError",
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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("", PORT), CalxRequestHandler) as httpd:
        print("\n=======================================================")
        print(f"  Calx Lexical Analyzer Terminal")
        print(f"  Running at: http://localhost:{PORT}")
        print("=======================================================\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
