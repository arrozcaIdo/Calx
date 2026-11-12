# WILL FIX: Multi-line comments; tulog muna bye

# operators are chunked and validated against recognized symbols (VALID_OPERATORS)
# spaces optional around operators but required between words
# evaluates input against multiple DFA transition tables; longest valid match (Maximal Munch tawag)

# all machines as tables
# runs all state machines and selects the one reading the farthest.

# defines the DFA lookup tables used by the lexer to group valid lexemes.

GROUPS = {
    "ALPHABET":          lambda c: ("a" <= c <= "z") or ("A" <= c <= "Z"),
    "DIGITS":            lambda c: "0" <= c <= "9",
    "NOT_NEWLINE":       lambda c: c != "\n" and c != "\r",
    "NOT_QUOTE_NEWLINE": lambda c: c != '"' and c != "\n" and c != "\r",
    "NOT_APOST_NEWLINE": lambda c: c != "'" and c != "\n" and c != "\r",
}

# builds the table for a list of words
def word_table(words):
    table = {"Q1": {}}
    accept = []
    state_after = {"": "Q1"}
    for word in words:
        so_far = ""
        for ch in word:
            longer = so_far + ch
            if longer not in state_after:
                new_state = "Q" + str(len(state_after) + 1)
                state_after[longer] = new_state
                table[new_state] = {}
                table[state_after[so_far]][ch] = new_state
            so_far = longer
        accept.append(state_after[so_far])
    return table, accept

# builds the table for symbols 
def symbol_table(symbol):
    table = {}
    for i, ch in enumerate(symbol):
        table["Q" + str(i + 1)] = {ch: "Q" + str(i + 2)}
    last = "Q" + str(len(symbol) + 1)
    table[last] = {}
    return table, [last]


# list of keywords, noise, reserved
# specific types of keywords
DOMAIN_KEYWORDS = [
    "reaction", "theory", "task", "run", "compound", "contract",
    "on_success", "on_failure"
]

SIMULATION_KEYWORDS = [
    "equation", "method", "basis", "solvent", 
    "scheduler", "cpus", "memory",  "walltime"
]

CONTROL_KEYWORDS = ["if", "elif", "else", "for", "in", "range"]
IO_KEYWORDS      = ["print", "read"]
MODULE_KEYWORDS  = ["from", "import"]
LOGICAL_KEYWORDS = ["is", "not", "and", "or"]

TYPE_SPECS = ["Float", "Integer", "Boolean", "String", "mol", "Vector", "Matrix"]
DIM_CLASSES = ["Length", "Mass", "Time", "Temp", "Pressure", "Energy", "Amount", "Volume", "Dipole", "Data"]
UNITS = [
    "kcal/mol", "kJ/mol",
    "Kelvin", "Celsius", "kg", "g", "mg", "m", "km", "cm", "nm", "Angstrom",
    "mmol", "L", "mL", "Joule", "Debye", "kJ", "Hartree", "eV", "s", "fs",
    "ps", "ns", "bar", "atm", "Pa", "GB", "MB", "mol"
]
STATE_FLAGS = ["converged", "stationary", "radical"]
NOISE_WORDS = ["the"]

KW_DOMAIN_TABLE, KW_DOMAIN_ACCEPT     = word_table(DOMAIN_KEYWORDS)
KW_CONTROL_TABLE, KW_CONTROL_ACCEPT   = word_table(CONTROL_KEYWORDS)
KW_IO_TABLE, KW_IO_ACCEPT             = word_table(IO_KEYWORDS)
KW_MODULE_TABLE, KW_MODULE_ACCEPT     = word_table(MODULE_KEYWORDS)
KW_LOGICAL_TABLE, KW_LOGICAL_ACCEPT   = word_table(LOGICAL_KEYWORDS)
KW_SIM_TABLE, KW_SIM_ACCEPT           = word_table(SIMULATION_KEYWORDS)
TYPE_SPEC_TABLE, TYPE_SPEC_ACCEPT     = word_table(TYPE_SPECS)
DIM_CLASS_TABLE, DIM_CLASS_ACCEPT     = word_table(DIM_CLASSES)
UNIT_TABLE, UNIT_ACCEPT               = word_table(UNITS)
STATE_FLAG_TABLE, STATE_FLAG_ACCEPT   = word_table(STATE_FLAGS)
NOISE_WORD_TABLE, NOISE_WORD_ACCEPT   = word_table(NOISE_WORDS)

# also sets the rules for an identifier 
# (1) must start w letter or underscore
# (2) can contain letters, digits, underscores
# (3) kapag nasa q2 na, loop sa letters, digits, _, hanggang may humarang na space or symbol
IDENTIFIER_TABLE = {
    "Q1": {"ALPHABET": "Q2", "_": "Q2"},
    "Q2": {"ALPHABET": "Q2", "DIGITS": "Q2", "_": "Q2"},
}
IDENTIFIER_ACCEPT = ["Q2"]

# for integer literals
INTEGER_TABLE = {
    "Q1": {"DIGITS": "Q2"},
    "Q2": {"DIGITS": "Q2"},
}
INTEGER_ACCEPT = ["Q2"]

FLOAT_TABLE = {
    "Q1": {"DIGITS": "Q2"},
    "Q2": {"DIGITS": "Q2", ".": "Q3"},
    "Q3": {"DIGITS": "Q4"},
    "Q4": {"DIGITS": "Q4"},
}
FLOAT_ACCEPT = ["Q4"]

# duration token 
DURATION_TABLE = {
    "Q1": {"DIGITS": "Q2"},
    "Q2": {"DIGITS": "Q3"},
    "Q3": {"DIGITS": "Q3", ":": "Q4"},
    "Q4": {"DIGITS": "Q5"},
    "Q5": {"DIGITS": "Q6"},
    "Q6": {":": "Q7"},
    "Q7": {"DIGITS": "Q8"},
    "Q8": {"DIGITS": "Q9"},
    "Q9": {},
}
DURATION_ACCEPT = ["Q9"]

# valid operators para sa chunk checking
VALID_OPERATORS = {
    "<=>": "REL_OP",
    "=>":  "REL_OP",
    "->":  "REL_OP",
    "==":  "REL_OP",
    "!=":  "REL_OP",
    "<=":  "REL_OP",
    ">=":  "REL_OP",
    "<":   "REL_OP",
    ">":   "REL_OP",
    "+=":  "COMP_ASSIGN",
    "-=":  "COMP_ASSIGN",
    "*=":  "COMP_ASSIGN",
    "/=":  "COMP_ASSIGN",
    "=":   "ASSIGN",
    "@":   "MATMUL",
    "^":   "EXPONENT",
    "+":   "ARITH_OP",
    "-":   "ARITH_OP",
    "*":   "ARITH_OP",
    "/":   "ARITH_OP",
    "%":   "ARITH_OP",
}

# delimiters and brackets
DELIM_LPAREN_TABLE, DELIM_LPAREN_ACCEPT     = symbol_table("(")
DELIM_RPAREN_TABLE, DELIM_RPAREN_ACCEPT     = symbol_table(")")
DELIM_LBRACKET_TABLE, DELIM_LBRACKET_ACCEPT = symbol_table("[")
DELIM_RBRACKET_TABLE, DELIM_RBRACKET_ACCEPT = symbol_table("]")
DELIM_LBRACE_TABLE, DELIM_LBRACE_ACCEPT     = symbol_table("{")
DELIM_RBRACE_TABLE, DELIM_RBRACE_ACCEPT     = symbol_table("}")
DELIM_COLON_TABLE, DELIM_COLON_ACCEPT       = symbol_table(":")
DELIM_COMMA_TABLE, DELIM_COMMA_ACCEPT       = symbol_table(",")
DELIM_DOT_TABLE, DELIM_DOT_ACCEPT           = symbol_table(".")

STRING_TABLE = {
    "Q1": {'"': "Q2", "'": "Q3"},
    "Q2": {"NOT_QUOTE_NEWLINE": "Q2", '"': "Q4"},
    "Q3": {"NOT_APOST_NEWLINE": "Q3", "'": "Q4"},
    "Q4": {},
}
STRING_ACCEPT = ["Q4"]

# for comments
SINGLE_COMMENT_TABLE = {
    "Q1": {"#": "Q2"},                  # "#" then text
    "Q2": {"NOT_NEWLINE": "Q2"},        # ... end of the line
}
SINGLE_COMMENT_ACCEPT = ["Q2"]

MULTI_COMMENT_TABLE = {
    "Q1": {'"': "Q2"},
    "Q2": {'"': "Q3"},
    "Q3": {'"': "Q4"},
    "Q4": {"NOT_QUOTE": "Q4", '"': "Q5"},
    "Q5": {"NOT_QUOTE": "Q4", '"': "Q6"},
    "Q6": {"NOT_QUOTE": "Q4", '"': "Q7"},
    "Q7": {},
}
MULTI_COMMENT_ACCEPT = ["Q7"]

NEWLINE_TABLE = {"Q1": {"\n": "Q2"}, "Q2": {}}
NEWLINE_ACCEPT = ["Q2"]

BLANK_TABLE = {
    "Q1": {" ": "Q2", "\t": "Q2"},
    "Q2": {" ": "Q2", "\t": "Q2"},
}
BLANK_ACCEPT = ["Q2"]

# lahat ng machines
MACHINES = [
    # words
    ("UNIT",              UNIT_ACCEPT,            UNIT_TABLE),
    ("KW_DOMAIN",         KW_DOMAIN_ACCEPT,       KW_DOMAIN_TABLE),
    ("KW_CONTROL",        KW_CONTROL_ACCEPT,      KW_CONTROL_TABLE),
    ("KW_IO",             KW_IO_ACCEPT,           KW_IO_TABLE),
    ("KW_MODULE",         KW_MODULE_ACCEPT,       KW_MODULE_TABLE),
    ("KW_LOGICAL",        KW_LOGICAL_ACCEPT,      KW_LOGICAL_TABLE),
    ("KW_SIM",            KW_SIM_ACCEPT,          KW_SIM_TABLE),
    ("TYPE_SPEC",         TYPE_SPEC_ACCEPT,       TYPE_SPEC_TABLE),
    ("DIM_CLASS",         DIM_CLASS_ACCEPT,       DIM_CLASS_TABLE),
    ("STATE_FLAG",        STATE_FLAG_ACCEPT,      STATE_FLAG_TABLE),
    ("NOISE_WORD",        NOISE_WORD_ACCEPT,      NOISE_WORD_TABLE),
    # literals
    ("DURATION",           DURATION_ACCEPT,          DURATION_TABLE),
    ("FLOAT_LIT",         FLOAT_ACCEPT,           FLOAT_TABLE),
    ("INT_LIT",           INTEGER_ACCEPT,         INTEGER_TABLE),
    ("IDENTIFIER",        IDENTIFIER_ACCEPT,      IDENTIFIER_TABLE),
    ("STRING_LIT",        STRING_ACCEPT,          STRING_TABLE),
    # delimiters
    ("DELIM_LPAREN",      DELIM_LPAREN_ACCEPT,    DELIM_LPAREN_TABLE),
    ("DELIM_RPAREN",      DELIM_RPAREN_ACCEPT,    DELIM_RPAREN_TABLE),
    ("DELIM_LBRACKET",    DELIM_LBRACKET_ACCEPT,  DELIM_LBRACKET_TABLE),
    ("DELIM_RBRACKET",    DELIM_RBRACKET_ACCEPT,  DELIM_RBRACKET_TABLE),
    ("DELIM_LBRACE",      DELIM_LBRACE_ACCEPT,    DELIM_LBRACE_TABLE),
    ("DELIM_RBRACE",      DELIM_RBRACE_ACCEPT,    DELIM_RBRACE_TABLE),
    ("DELIM_COLON",       DELIM_COLON_ACCEPT,     DELIM_COLON_TABLE),
    ("DELIM_COMMA",       DELIM_COMMA_ACCEPT,     DELIM_COMMA_TABLE),
    ("DELIM_DOT",         DELIM_DOT_ACCEPT,       DELIM_DOT_TABLE),
    # comments, newlines, blanks
    ("COMMENT",           SINGLE_COMMENT_ACCEPT,  SINGLE_COMMENT_TABLE),
    ("NEWLINE",           NEWLINE_ACCEPT,         NEWLINE_TABLE),
    ("BLANK",             BLANK_ACCEPT,           BLANK_TABLE),
]

WORD_TOKENS = {
    "KW_DOMAIN", "KW_CONTROL", "KW_IO", "KW_MODULE", "KW_LOGICAL", "KW_SIM",
    "TYPE_SPEC", "DIM_CLASS", "UNIT", "STATE_FLAG", "NOISE_WORD", "IDENTIFIER"
}

OPERATOR_CHARS = set("+-*/%^=<>!@")
DELIMITER_CHARS = set("()[]{},:.")

# SCANNER 
class LexicalError(Exception):
    pass


def is_word_char(c):
    return c.isascii() and (c.isalnum() or c == "_")

def end_of_word(text, pos): # san natatapos 
    while pos < len(text) and is_word_char(text[pos]):
        pos += 1
    return pos

def starts_unit(text, pos):
    return any(
        text.startswith(unit, pos)
        and (pos + len(unit) == len(text) or not is_word_char(text[pos + len(unit)]))
        for unit in UNITS
    )

# function to check if a space is inside a .to() projection
def has_spaced_projection(text, pos):
    cursor = pos + 1
    has_space = False
    while cursor < len(text) and text[cursor].isspace():
        has_space = True
        cursor += 1
    if not text.startswith("to", cursor):
        return False
    cursor += 2
    if cursor < len(text) and is_word_char(text[cursor]):
        return False
    while cursor < len(text) and text[cursor].isspace():
        has_space = True
        cursor += 1
    return has_space and cursor < len(text) and text[cursor] == "("

# function helper to scans for matching quotes
def fstring_end(text, pos):
    quote = text[pos + 1]
    delimiter = quote * 3 if text.startswith(quote * 3, pos + 1) else quote
    cursor = pos + 1 + len(delimiter)
    while cursor < len(text):
        if text.startswith(delimiter, cursor):
            return cursor + len(delimiter)
        if len(delimiter) == 1 and text[cursor] in "\r\n":
            raise LexicalError("End of line while scanning f-string literal")
        if text[cursor] == "\\":
            cursor += 2
        else:
            cursor += 1
    raise LexicalError("Unterminated f-string literal")


def next_state(table, state, ch): # san next based sa table
    if state not in table:
        return None
    for label, target in table[state].items():
        if label in GROUPS:
            if GROUPS[label](ch):
                return target
        elif label == ch:
            return target
    return None


def longest_match(accept, table, text, pos):
    state = "Q1"
    longest = -1
    i = pos
    while i < len(text):
        state = next_state(table, state, text[i])
        if state is None:
            break
        i += 1
        if state in accept:
            longest = i
    return longest


def tokenize(text):
    text = text.replace("\r\n", "\n")   # carriage return before newline
    tokens = []
    pos = 0

    while pos < len(text): # ask every machine; longest match wins
        ch = text[pos]

        # detect f and F prefix find the end, and tag everything before it as one f-string token
        if ch in ("f", "F") and pos + 1 < len(text) and text[pos + 1] in ('"', "'"):
            end = fstring_end(text, pos)
            tokens.append(("FSTRING_LIT", text[pos:end]))
            pos = end
            continue

        # detect if there's a space inside .to() projection
        if ch == "." and has_spaced_projection(text, pos):
            raise LexicalError("Whitespace is not allowed inside a .to(...) projection")

        # reads the entire continuous sequence of operator characters until
        # hitting whitespace, an alphanumeric character, or a bracket/delimiter
        if ch in OPERATOR_CHARS:
            end = pos
            while end < len(text) and text[end] in OPERATOR_CHARS:
                end += 1
            op_chunk = text[pos:end]

            # validate; Error? record and skip
            if op_chunk in VALID_OPERATORS:
                tokens.append((VALID_OPERATORS[op_chunk], op_chunk))
                pos = end
                continue
            else:
                raise LexicalError(
                    f"Invalid operator '{op_chunk}'. Not a recognized operator symbol."
                )
       
        # In tokenize(), before the DFA loop:
        if text.startswith('"""', pos):
            closing_idx = text.find('"""', pos + 3)
            if closing_idx == -1:
                raise LexicalError("Unterminated multi-line comment: missing closing '\"\"\"'")
            
            end = closing_idx + 3
            lexeme = text[pos:end]
            
            # If you want comments displayed in the token table:
            tokens.append(("COMMENT", lexeme))
            
            # (If you want comments silently discarded, just don't append to tokens)
            pos = end
            continue

        # Table-driven DFA matching
        best_token, best_end = None, pos
        for token_type, accept, table in MACHINES:
            end = longest_match(accept, table, text, pos)
            if end > best_end:
                best_token, best_end = token_type, end

        if best_token is None:
            if ch in ('"', "'"):
                raise LexicalError("Unterminated string literal")
            raise LexicalError(f"Unexpected character {repr(ch)}. Not a valid member of character set.")

        if best_token == "DURATION" and best_end < len(text) and (
            is_word_char(text[best_end]) or text[best_end] == ":"
        ):
            raise LexicalError(
                f"Invalid duration '{text[pos:end_of_word(text, best_end)]}'. Expected HH:MM:SS."
            )

        # Rule 1: Identifiers cannot begin with a digit
        if best_token in ("INT_LIT", "FLOAT_LIT") and best_end < len(text) and (
            text[best_end].isalpha() or text[best_end] == "_"
        ) and not starts_unit(text, best_end):
            bad_end = end_of_word(text, best_end)
            bad_id = text[pos:bad_end]
            raise LexicalError(f"Invalid identifier '{bad_id}'. Rule 1 violated: Identifiers cannot begin with a digit.")

        # adjacent words require spaces
        if best_token in WORD_TOKENS and best_end < len(text) and is_word_char(text[best_end]):
            raise LexicalError("Invalid word token (missing delimiter/blank between words)")

        # contextual keywords checker, change their token if character before the word is a .
        lexeme = text[pos:best_end]
        if best_token == "IDENTIFIER" and pos > 0 and text[pos - 1] == ".":
            if lexeme == "to":
                best_token = "KW_PROJECTION"
            elif lexeme in ("formula", "molecular_weight"):
                best_token = "KW_MOL_ATTRIBUTE"

        if best_token not in ("BLANK", "NEWLINE", "COMMENT"):
            tokens.append((best_token, lexeme))

        pos = best_end 

    return tokens

# TERMINAL REPL
if __name__ == "__main__":
    print("=== Calx Lexical Analyzer ===")
    print("Enter Calx statements to inspect tokens. Type 'exit' to quit.\n")

    while True:
        try:
            line = input("calx> ")
            if line.strip().lower() in ("exit", "quit"):
                break
            if not line.strip():
                continue

            tokens = tokenize(line)

            print(f"{'TYPE':<20} {'VALUE'}")
            print("-" * 35)
            for tok_type, tok_val in tokens:
                print(f"{tok_type:<20} {repr(tok_val)}")
            print()

        except LexicalError as err:
            print(f"Error: {err}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break
