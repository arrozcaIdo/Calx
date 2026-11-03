# Calx: Statically Typed DSL for Computational Chemistry

Calx (.clx), pronounced kahl-eks, is a compiled, statically typed domain-specific programming language designed for computational chemistry, quantum modelling, and high-performance molecular simulations. In the modern computational chemistry field, the "two-language problem" refers to needing to use different languages for different stages of a workflow, such as having to write in Python for data preparation then transfer to Fortran for intensive calculations. This separation can cause extra complexities in the integration of code and transfer of data from one component to another. Calx aims to solve this problem by creating a single framework to build chemical systems, run scientific calculations, and run computationally intensive simulations without requiring users to rely on other scripting languages or workflow tools.


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
