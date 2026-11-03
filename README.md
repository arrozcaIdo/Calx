# Calx-.clx-

Clean separation between UI (HTML/CSS/JS) and backend lexical analyzer (`calx_lexer.py`).

## File Structure
- `index.html`: UI terminal interface
- `style.css`: Terminal scrollbars and animation styling
- `app.js`: Frontend logic, keyboard handling, preset chips, and API caller (`fetch('/tokenize')`)
- `calx_lexer.py`: The exact manual lexical analyzer (Pure Python, character-by-character DFA scanner)
- `server.py`: Standard library HTTP server (no Flask/pip needed) routing frontend requests to `calx_lexer.py`

## How to Run
In your terminal / PowerShell:
```bash
python server.py
```
Then open:
```
http://localhost:8000
```
