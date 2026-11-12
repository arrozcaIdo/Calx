
# evaluates input against multiple DFA transition tables; longest valid match wins 

GROUPS = {
    "ALPHABET":           lambda c: ("a" <= c <= "z") or ("A" <= c <= "Z"),
    "DIGITS":             lambda c: "0" <= c <= "9",
    "ANY_CHAR":           lambda c: True,
    "NOT_NEWLINE":        lambda c: c != "\n" and c != "\r",
    "NOT_QUOTE":          lambda c: c != '"',
    "NOT_DOUBLE_STRING":  lambda c: c not in ('"', "\\", "\n", "\r"),
    "NOT_SINGLE_STRING":  lambda c: c not in ("'", "\\", "\n", "\r"),
}


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


def symbol_table(symbol):
    table = {}
    for i, ch in enumerate(symbol):
        table["Q" + str(i + 1)] = {ch: "Q" + str(i + 2)}
    last = "Q" + str(len(symbol) + 1)
    table[last] = {}
    return table, [last]


# =============================================================================
# VOCABULARIES & TRANSITION TABLES
# =============================================================================

DOMAIN_KEYWORDS = [
    "reaction", "theory", "task", "run", "compound", "contract",
    "on_success", "on_failure"
]

SIMULATION_KEYWORDS = [
    "equation", "method", "basis", "solvent",
    "scheduler", "cpus", "memory", "walltime"
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

KW_DOMAIN_TABLE, KW_DOMAIN_ACCEPT               = word_table(DOMAIN_KEYWORDS)
KW_PROJECTION_TABLE, KW_PROJECTION_ACCEPT       = word_table(["to"])
KW_MOL_ATTRIBUTE_TABLE, KW_MOL_ATTRIBUTE_ACCEPT = word_table(["formula", "molecular_weight"])
KW_CONTROL_TABLE, KW_CONTROL_ACCEPT             = word_table(CONTROL_KEYWORDS)
KW_IO_TABLE, KW_IO_ACCEPT                       = word_table(IO_KEYWORDS)
KW_MODULE_TABLE, KW_MODULE_ACCEPT               = word_table(MODULE_KEYWORDS)
KW_LOGICAL_TABLE, KW_LOGICAL_ACCEPT             = word_table(LOGICAL_KEYWORDS)
KW_SIM_TABLE, KW_SIM_ACCEPT                     = word_table(SIMULATION_KEYWORDS)
TYPE_SPEC_TABLE, TYPE_SPEC_ACCEPT               = word_table(TYPE_SPECS)
DIM_CLASS_TABLE, DIM_CLASS_ACCEPT               = word_table(DIM_CLASSES)
UNIT_TABLE, UNIT_ACCEPT                         = word_table(UNITS)
STATE_FLAG_TABLE, STATE_FLAG_ACCEPT             = word_table(STATE_FLAGS)
NOISE_WORD_TABLE, NOISE_WORD_ACCEPT             = word_table(NOISE_WORDS)


IDENTIFIER_TABLE = {
    "Q1": {"ALPHABET": "Q2", "_": "Q2"},
    "Q2": {"ALPHABET": "Q2", "DIGITS": "Q2", "_": "Q2"},
}
IDENTIFIER_ACCEPT = ["Q2"]

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
    "Q1": {'"': "Q2", "'": "Q6"},
    "Q2": {"NOT_DOUBLE_STRING": "Q2", "\\": "Q3", '"': "Q4"},
    "Q3": {"NOT_NEWLINE": "Q2"},
    "Q4": {},
    "Q6": {"NOT_SINGLE_STRING": "Q6", "\\": "Q7", "'": "Q8"},
    "Q7": {"NOT_NEWLINE": "Q6"},
    "Q8": {},
}
STRING_ACCEPT = ["Q4", "Q8"]

FSTRING_TABLE = {
    "Q1": {"f": "Q2", "F": "Q2"},
    "Q2": {'"': "Q3", "'": "Q7"},
    "Q3": {"NOT_DOUBLE_STRING": "Q3", "\\": "Q4", '"': "Q5"},
    "Q4": {"NOT_NEWLINE": "Q3"},
    "Q5": {},
    "Q7": {"NOT_SINGLE_STRING": "Q7", "\\": "Q8", "'": "Q9"},
    "Q8": {"NOT_NEWLINE": "Q7"},
    "Q9": {},
}
FSTRING_ACCEPT = ["Q5", "Q9"]

SINGLE_COMMENT_TABLE = {
    "Q1": {"#": "Q2"},
    "Q2": {"NOT_NEWLINE": "Q2"},
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

MACHINES = [
    ("UNIT",              UNIT_ACCEPT,             UNIT_TABLE),
    ("KW_DOMAIN",         KW_DOMAIN_ACCEPT,        KW_DOMAIN_TABLE),
    ("KW_PROJECTION",     KW_PROJECTION_ACCEPT,    KW_PROJECTION_TABLE),
    ("KW_MOL_ATTRIBUTE",  KW_MOL_ATTRIBUTE_ACCEPT, KW_MOL_ATTRIBUTE_TABLE),
    ("KW_CONTROL",        KW_CONTROL_ACCEPT,       KW_CONTROL_TABLE),
    ("KW_IO",             KW_IO_ACCEPT,            KW_IO_TABLE),
    ("KW_MODULE",         KW_MODULE_ACCEPT,        KW_MODULE_TABLE),
    ("KW_LOGICAL",        KW_LOGICAL_ACCEPT,       KW_LOGICAL_TABLE),
    ("KW_SIM",            KW_SIM_ACCEPT,           KW_SIM_TABLE),
    ("TYPE_SPEC",         TYPE_SPEC_ACCEPT,        TYPE_SPEC_TABLE),
    ("DIM_CLASS",         DIM_CLASS_ACCEPT,        DIM_CLASS_TABLE),
    ("STATE_FLAG",        STATE_FLAG_ACCEPT,       STATE_FLAG_TABLE),
    ("NOISE_WORD",        NOISE_WORD_ACCEPT,       NOISE_WORD_TABLE),

    ("DURATION",          DURATION_ACCEPT,         DURATION_TABLE),
    ("FLOAT_LIT",         FLOAT_ACCEPT,            FLOAT_TABLE),
    ("INT_LIT",           INTEGER_ACCEPT,          INTEGER_TABLE),
    ("FSTRING_LIT",       FSTRING_ACCEPT,          FSTRING_TABLE),
    ("IDENTIFIER",        IDENTIFIER_ACCEPT,       IDENTIFIER_TABLE),
    ("MULTI_COMMENT",     MULTI_COMMENT_ACCEPT,    MULTI_COMMENT_TABLE),
    ("STRING_LIT",        STRING_ACCEPT,           STRING_TABLE),

    ("DELIM_LPAREN",      DELIM_LPAREN_ACCEPT,     DELIM_LPAREN_TABLE),
    ("DELIM_RPAREN",      DELIM_RPAREN_ACCEPT,     DELIM_RPAREN_TABLE),
    ("DELIM_LBRACKET",    DELIM_LBRACKET_ACCEPT,   DELIM_LBRACKET_TABLE),
    ("DELIM_RBRACKET",    DELIM_RBRACKET_ACCEPT,   DELIM_RBRACKET_TABLE),
    ("DELIM_LBRACE",      DELIM_LBRACE_ACCEPT,     DELIM_LBRACE_TABLE),
    ("DELIM_RBRACE",      DELIM_RBRACE_ACCEPT,     DELIM_RBRACE_TABLE),
    ("DELIM_COLON",       DELIM_COLON_ACCEPT,      DELIM_COLON_TABLE),
    ("DELIM_COMMA",       DELIM_COMMA_ACCEPT,      DELIM_COMMA_TABLE),
    ("DELIM_DOT",         DELIM_DOT_ACCEPT,        DELIM_DOT_TABLE),

# Comments, newlines, tabs, blanks
    ("COMMENT",           SINGLE_COMMENT_ACCEPT,   SINGLE_COMMENT_TABLE),
    ("NEWLINE",           NEWLINE_ACCEPT,          NEWLINE_TABLE),
    ("BLANK",             BLANK_ACCEPT,            BLANK_TABLE),
]

WORD_TOKENS = {
    "KW_DOMAIN", "KW_CONTROL", "KW_IO", "KW_MODULE", "KW_LOGICAL", "KW_SIM",
    "KW_PROJECTION", "KW_MOL_ATTRIBUTE", "TYPE_SPEC", "DIM_CLASS", "UNIT",
    "STATE_FLAG", "NOISE_WORD", "IDENTIFIER"
}

OPERATOR_CHARS = set("+-*/%^=<>!@")
DELIMITER_CHARS = set("()[]{},:.")


# =============================================================================
# SCANNER ENGINE
# =============================================================================

class LexicalError(Exception):
    pass


def is_word_char(c):
    return c.isascii() and (c.isalnum() or c == "_")


def end_of_word(text, pos):
    while pos < len(text) and is_word_char(text[pos]):
        pos += 1
    return pos


def end_of_line(text, pos):
    nl = text.find("\n", pos)
    return len(text) if nl == -1 else nl


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


def next_state(table, state, ch):
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


def validate_candidate(text, pos, token_type, end):
    lexeme = text[pos:end]

    # 1. Unterminated multi-line comment (consumes to EOF)
    if text.startswith('"""', pos) and token_type != "MULTI_COMMENT":
        return (
            "LEXICAL_ERROR",
            f"{text[pos:]} -> Unterminated multi-line comment (missing closing '\"\"\"')",
            len(text),
        )

    # 2. .to() projection check
    if token_type == "DELIM_DOT" and has_spaced_projection(text, pos):
        return (
            "LEXICAL_ERROR",
            ". -> Whitespace is not allowed inside a .to(...) projection",
            end,
        )

    # 3. Duration literal for HH:MM:SS
    if token_type == "DURATION" and end < len(text) and (
        is_word_char(text[end]) or text[end] == ":"
    ):
        bad_end = end
        while bad_end < len(text) and (is_word_char(text[bad_end]) or text[bad_end] == ":"):
            bad_end += 1
        return (
            "LEXICAL_ERROR",
            f"{text[pos:bad_end]} -> Invalid duration (expected HH:MM:SS)",
            bad_end,
        )

    # 4. Calx Rule 1: Identifiers cannot begin with a digit
    if token_type in ("INT_LIT", "FLOAT_LIT") and end < len(text) and (
        text[end].isalpha() or text[end] == "_"
    ):
        bad_end = end_of_word(text, end)
        bad_id = text[pos:bad_end]
        return (
            "LEXICAL_ERROR",
            f"{bad_id} -> Rule 1 violated: Identifiers cannot begin with a digit",
            bad_end,
        )

    # 5. Unterminated f-string (matched 'f' or 'F' followed by an unclosed quote)
    if token_type == "IDENTIFIER" and lexeme in ("f", "F") and end < len(text) and text[end] in ('"', "'"):
        eol = end_of_line(text, pos)
        return (
            "LEXICAL_ERROR",
            f"{text[pos:eol]} -> Unterminated f-string literal",
            eol,
        )

    # 6. Triple-quoted f-strings disallowed
    if token_type == "FSTRING_LIT" and pos + 3 < len(text) and (
        text[pos] in ("f", "F")
        and text[pos + 1] in ('"', "'")
        and text.startswith(text[pos + 1] * 3, pos + 1)
    ):
        return (
            "LEXICAL_ERROR",
            f"{lexeme} -> Triple-quoted f-strings are not supported",
            end,
        )

    # 7. Missing delimiter/space between adjacent word tokens
    if token_type in WORD_TOKENS and end < len(text) and is_word_char(text[end]):
        bad_end = end_of_word(text, end)
        return (
            "LEXICAL_ERROR",
            f"{text[pos:bad_end]} -> Invalid word token (missing delimiter/blank between words)",
            bad_end,
        )

    # 8. Contextual check: 'to', 'formula', 'molecular_weight' are only keywords after '.'
    if token_type in ("KW_PROJECTION", "KW_MOL_ATTRIBUTE") and (
        pos == 0 or text[pos - 1] != "."
    ):
        return ("IDENTIFIER", lexeme, end)

    return (token_type, lexeme, end)


def tokenize(text):
    text = text.replace("\r\n", "\n")
    tokens = []
    pos = 0

    while pos < len(text):
        ch = text[pos]

        # 1. Whole-Operator Chunking
        if ch in OPERATOR_CHARS:
            end = pos
            while end < len(text) and text[end] in OPERATOR_CHARS:
                end += 1
            op_chunk = text[pos:end]

            if op_chunk in VALID_OPERATORS:
                tokens.append((VALID_OPERATORS[op_chunk], op_chunk))
            else:
                tokens.append((
                    "LEXICAL_ERROR",
                    f"{op_chunk} -> Invalid operator (not a recognized symbol)"
                ))
            pos = end
            continue

        # 2. Table-driven DFA matching
        best_token, best_end = None, pos
        for token_type, accept, table in MACHINES:
            end = longest_match(accept, table, text, pos)
            if end > best_end:
                best_token, best_end = token_type, end

        # Unrecognized character or unterminated string/comment
        if best_token is None:  
            if ch == "\\":
                tokens.append((
                    "LEXICAL_ERROR",
                    f"{ch} -> Misplaced escape character"
                ))
                pos += 1
                
            elif text.startswith('"""', pos):
                tokens.append((
                    "LEXICAL_ERROR",
                    f"{text[pos:]} -> Unterminated multi-line comment (missing closing '\"\"\"')"
                ))
                pos = len(text)
            elif ch in ('"', "'"):
                eol = end_of_line(text, pos)
                tokens.append((
                    "LEXICAL_ERROR",
                    f"{text[pos:eol]} -> Unterminated string literal"
                ))
                pos = eol
            else:
                tokens.append((
                    "LEXICAL_ERROR",
                    f"{ch} -> Unexpected character (not in Calx character set)"
                ))
                pos += 1
            continue

        # 3. Validate matched token and recover past any errors
        resolved_type, lexeme, next_pos = validate_candidate(text, pos, best_token, best_end)

        if resolved_type not in ("BLANK", "COMMENT", "MULTI_COMMENT"):
            tokens.append((resolved_type, lexeme))

        pos = next_pos

    return tokens


# =============================================================================
# TERMINAL
# =============================================================================

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

            print(f"{'TOKEN TYPE':<20} {'LEXEMES'}")
            print("-" * 55)
            for tok_type, tok_val in tokens:
                print(f"{tok_type:<20} {repr(tok_val)}")
            print()

        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break