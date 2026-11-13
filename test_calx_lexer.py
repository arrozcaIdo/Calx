import unittest

from calx_lexer import tokenize


class LexerErrorRecoveryTests(unittest.TestCase):
    def test_complete_duration_is_one_token(self):
        self.assertEqual(
            tokenize("walltime: 24:00:00"),
            [
                ("KW_SIM", "walltime"),
                ("DELIM_COLON", ":"),
                ("DURATION", "24:00:00"),
            ],
        )

    def test_incomplete_duration_is_one_error_and_scanning_continues(self):
        self.assertEqual(
            tokenize("24:00:0 next"),
            [
                ("LEXICAL_ERROR", "24:00:0 -> Invalid duration (expected HH:MM:SS)"),
                ("IDENTIFIER", "next"),
            ],
        )

    def test_triple_quoted_fstring_is_one_error_and_scanning_continues(self):
        self.assertEqual(
            tokenize('f"""text""" next'),
            [
                ("LEXICAL_ERROR", 'f"""text""" -> Triple-quoted f-strings are not supported'),
                ("IDENTIFIER", "next"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
