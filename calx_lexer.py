# =====================================================================
# Calx Lexical Analyzer 
# =====================================================================

class LexicalError(Exception):
    """Raised when the scanner encounters an invalid token, character, or lexical pattern."""
    pass


class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, line={self.line}, col={self.column})"


class CalxLexer:
    KEYWORDS = {
        "reaction", "theory", "task", "run", "compound", "contract",
        "if", "elif", "else", "for", "in", "print", "read", "range",
        "from", "import", "on_success", "on_failure", "is", "not", "and", "or"
    }

    TYPE_SPECS = {
        "Float", "Integer", "Boolean", "String", "mol", "Vector", "Matrix"
    }

    DIM_CLASSES = {
        "Length", "Mass", "Time", "Temp", "Pressure", "Energy",
        "Amount", "Volume", "Dipole", "Data"
    }

    UNITS = {
        "Kelvin", "Celsius", "kg", "g", "mg", "m", "km", "cm", "nm", "Angstrom",
        "mol", "mmol", "L", "mL", "Joule", "Debye", "kJ", "kcal/mol",
        "kJ/mol", "Hartree", "eV", "s", "fs", "ps", "ns", "bar", "atm",
        "Pa", "GB", "MB"
    }

    STATE_FLAGS = {
        "converged", "stationary", "radical"
    }

    NOISE_WORDS = {
        "the"
    }

    ALL_RESERVED = KEYWORDS | TYPE_SPECS | DIM_CLASSES | UNITS | STATE_FLAGS | NOISE_WORDS

    def __init__(self, source_code):
        self.source = source_code
        self.pos = 0
        self.length = len(source_code)
        self.line = 1
        self.col = 1
        self.tokens = []
        self.indent_stack = [0]
        self.bracket_depth = 0
        self.at_line_start = True

    def peek(self, offset=0):
        index = self.pos + offset
        if index < self.length:
            return self.source[index]
        return ""

    def advance(self):
        ch = self.peek()
        self.pos += 1
        self.col += 1
        return ch

    def match_str(self, target):
        end_idx = self.pos + len(target)
        if end_idx <= self.length and self.source[self.pos:end_idx] == target:
            self.pos += len(target)
            self.col += len(target)
            return True
        return False

    def tokenize(self):
        while self.pos < self.length:
            # ---------------------------------------------------------
            # 1. Indentation & Off-side Rule Processing
            # ---------------------------------------------------------
            if self.at_line_start:
                spaces = 0
                start_col = self.col

                while self.peek() in (" ", "\t"):
                    if self.peek() == " ":
                        spaces += 1
                    else:
                        spaces += 4
                    self.pos += 1
                    self.col += 1

                ch = self.peek()
                if ch in ("\r", "\n") or ch == "#":
                    if ch == "\r" and self.peek(1) == "\n":
                        self.pos += 2
                    elif ch in ("\r", "\n"):
                        self.pos += 1
                    elif ch == "#":
                        while self.peek() and self.peek() not in ("\r", "\n"):
                            self.advance()
                        if self.peek() == "\r" and self.peek(1) == "\n":
                            self.pos += 2
                        elif self.peek() in ("\r", "\n"):
                            self.pos += 1
                    self.line += 1
                    self.col = 1
                    continue

                if self.pos >= self.length:
                    break

                self.at_line_start = False

                if self.bracket_depth == 0:
                    current_indent = spaces
                    if current_indent > self.indent_stack[-1]:
                        if current_indent % 4 != 0:
                            raise IndentationError(
                                f"Line {self.line}: Indentation must be in increments of 4 spaces (found {current_indent} spaces)."
                            )
                        self.indent_stack.append(current_indent)
                        self.tokens.append(Token("INDENT", " " * (current_indent - self.indent_stack[-2]), self.line, start_col))
                    else:
                        while current_indent < self.indent_stack[-1]:
                            self.indent_stack.pop()
                            self.tokens.append(Token("DEDENT", "", self.line, start_col))
                        if current_indent != self.indent_stack[-1]:
                            raise IndentationError(
                                f"Line {self.line}: Unaligned dedent matching no outer indentation level."
                            )

            # ---------------------------------------------------------
            # 2. Token Formation
            # ---------------------------------------------------------
            start_line = self.line
            start_col = self.col
            ch = self.peek()

            # Skip horizontal whitespace
            if ch in (" ", "\t"):
                self.advance()
                continue

            # Newlines
            if ch in ("\r", "\n"):
                if ch == "\r" and self.peek(1) == "\n":
                    self.pos += 2
                else:
                    self.pos += 1
                self.line += 1
                self.col = 1
                self.at_line_start = True
                if self.bracket_depth == 0:
                    self.tokens.append(Token("NEWLINE", "\\n", start_line, start_col))
                continue

            # Comments
            if ch == "#":
                while self.peek() and self.peek() not in ("\r", "\n"):
                    self.advance()
                continue

            # Multi-line comment/docstring
            if self.match_str('"""'):
                val = '"""'
                while self.pos < self.length:
                    if self.match_str('"""'):
                        val += '"""'
                        break
                    c = self.advance()
                    val += c
                    if c == "\n":
                        self.line += 1
                        self.col = 1
                else:
                    raise LexicalError(f"Line {start_line}: Unterminated multi-line comment.")
                self.tokens.append(Token("STRING_LIT", val, start_line, start_col))
                continue

            # Strings & f-strings
            is_fstring = False
            if ch == "f" and self.peek(1) in ('"', "'"):
                is_fstring = True
                self.advance()
                ch = self.peek()

            if ch in ('"', "'"):
                quote_type = self.advance()
                val = "f" + quote_type if is_fstring else quote_type
                closed = False
                while self.pos < self.length:
                    c = self.advance()
                    val += c
                    if c == "\\":
                        if self.pos < self.length:
                            val += self.advance()
                    elif c == quote_type:
                        closed = True
                        break
                    elif c in ("\r", "\n"):
                        raise LexicalError(f"Line {start_line}: EOL while scanning string literal.")

                if not closed:
                    raise LexicalError(f"Line {start_line}: Unterminated string literal.")

                self.tokens.append(Token("STRING_LIT", val, start_line, start_col))
                continue

            # Multi-character Operators
            if self.match_str("<=>"):
                self.tokens.append(Token("<=>", "<=>", start_line, start_col))
                continue
            if self.match_str("=>"):
                self.tokens.append(Token("=>", "=>", start_line, start_col))
                continue
            if self.match_str("->"):
                self.tokens.append(Token("->", "->", start_line, start_col))
                continue
            if self.match_str("<="):
                self.tokens.append(Token("REL_OP", "<=", start_line, start_col))
                continue
            if self.match_str(">="):
                self.tokens.append(Token("REL_OP", ">=", start_line, start_col))
                continue
            if self.match_str("=="):
                self.tokens.append(Token("REL_OP", "==", start_line, start_col))
                continue
            if self.match_str("!="):
                self.tokens.append(Token("REL_OP", "!=", start_line, start_col))
                continue
            if self.match_str("+="):
                self.tokens.append(Token("COMP_ASSIGN", "+=", start_line, start_col))
                continue
            if self.match_str("-="):
                self.tokens.append(Token("COMP_ASSIGN", "-=", start_line, start_col))
                continue
            if self.match_str("*="):
                self.tokens.append(Token("COMP_ASSIGN", "*=", start_line, start_col))
                continue
            if self.match_str("/="):
                self.tokens.append(Token("COMP_ASSIGN", "/=", start_line, start_col))
                continue

            # Compound Units
            if self.match_str("kcal/mol"):
                self.tokens.append(Token("UNIT", "kcal/mol", start_line, start_col))
                continue
            if self.match_str("kJ/mol"):
                self.tokens.append(Token("UNIT", "kJ/mol", start_line, start_col))
                continue

            # Numbers: Floats and Integers
            if ch.isdigit():
                num_str = ""
                has_dot = False

                while self.peek().isdigit() or (self.peek() == "." and not has_dot and self.peek(1).isdigit()):
                    if self.peek() == ".":
                        has_dot = True
                    num_str += self.advance()

                # Catch identifiers starting with digits (e.g., 1mol, 2x, 3_energy)
                if self.peek().isalpha() or self.peek() == "_":
                    bad_id = num_str
                    while self.peek().isalnum() or self.peek() == "_":
                        bad_id += self.advance()
                    raise LexicalError(
                        f"Lexical error at line {start_line}, col {start_col}: "
                        f"Invalid identifier '{bad_id}'. Rule 1 violated: Identifiers cannot begin with a digit."
                    )

                if has_dot:
                    self.tokens.append(Token("FLOAT_LIT", num_str, start_line, start_col))
                else:
                    self.tokens.append(Token("INT_LIT", num_str, start_line, start_col))
                continue

            # Identifiers and Reserved Words
            if ch.isalpha() or ch == "_":
                word = ""
                while self.peek().isalnum() or self.peek() == "_":
                    word += self.advance()

                # Rule 5: Hyphens inside identifiers
                if self.peek() == "-" and (self.peek(1).isalnum() or self.peek(1) == "_"):
                    self.advance()  # consume '-'
                    word += "-"
                    while self.peek().isalnum() or self.peek() == "_" or self.peek() == "-":
                        word += self.advance()
                    raise LexicalError(
                        f"Lexical error at line {start_line}, col {start_col}: "
                        f"Invalid identifier '{word}'. Rule 5 violated: Hyphens are not allowed inside identifiers."
                    )

                # Categorization
                if word in self.ALL_RESERVED:
                    if word in self.KEYWORDS:
                        self.tokens.append(Token("KEYWORD", word, start_line, start_col))
                    elif word in self.TYPE_SPECS:
                        self.tokens.append(Token("TYPE_SPEC", word, start_line, start_col))
                    elif word in self.DIM_CLASSES:
                        self.tokens.append(Token("DIM_CLASS", word, start_line, start_col))
                    elif word in self.UNITS:
                        self.tokens.append(Token("UNIT", word, start_line, start_col))
                    elif word in self.STATE_FLAGS:
                        self.tokens.append(Token("STATE_FLAG", word, start_line, start_col))
                    elif word in self.NOISE_WORDS:
                        self.tokens.append(Token("NOISE_WORD", word, start_line, start_col))
                else:
                    self.tokens.append(Token("IDENTIFIER", word, start_line, start_col))
                continue

            # Delimiters and Brackets
            if ch in ("(", "[", "{"):
                self.bracket_depth += 1
                self.tokens.append(Token(ch, self.advance(), start_line, start_col))
                continue

            if ch in (")", "]", "}"):
                if self.bracket_depth > 0:
                    self.bracket_depth -= 1
                self.tokens.append(Token(ch, self.advance(), start_line, start_col))
                continue

            # Single-character operators and punctuation (including '.')
            single_tokens = {
                "@": "MATMUL",
                "^": "EXPONENT",
                "=": "ASSIGN",
                "<": "REL_OP",
                ">": "REL_OP",
                "+": "ARITH_OP",
                "-": "ARITH_OP",
                "*": "ARITH_OP",
                "/": "ARITH_OP",
                "%": "ARITH_OP",
                ":": ":",
                ",": ",",
                ".": "."
            }

            if ch in single_tokens:
                self.tokens.append(Token(single_tokens[ch], self.advance(), start_line, start_col))
                continue

            raise LexicalError(
                f"Lexical error at line {start_line}, col {start_col}: "
                f"Unexpected character {repr(ch)}. Not a valid member of character set."
            )

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token("DEDENT", "", self.line, self.col))

        self.tokens.append(Token("EOF", "", self.line, self.col))
        return self.tokens

if __name__ == "__main__":
    print("=== Calx Strict Lexical Analyzer ===")
    print("Type Calx statements to inspect tokens. Type 'exit' to quit.\n")

    while True:
        try:
            line = input("calx> ")
            if line.strip().lower() in ("exit", "quit"):
                break
            if not line.strip():
                continue

            lexer = CalxLexer(line)
            tokens = lexer.tokenize()

            print(f"{'TYPE':<20} {'VALUE'}")
            print("-" * 35)
            for tok in tokens:
                if tok.type != "EOF":
                    print(f"{tok.type:<20} {repr(tok.value)}")
            print()

        except (LexicalError, IndentationError) as err:
            print(f"Error: {err}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
