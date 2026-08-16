import unittest

import lexane


class LexaneTests(unittest.TestCase):
    def test_arithmetic_precedence(self):
        self.assertEqual(lexane.execute("2 + 3 * 4")["result"], 14)

    def test_parentheses(self):
        self.assertEqual(lexane.execute("(2 + 3) * 4")["result"], 20)

    def test_let_bindings(self):
        result = lexane.execute("let x = 7; let y = x * 3; y + 1")
        self.assertEqual(result["result"], 22)
        self.assertEqual(result["variables"], {"x": 7, "y": 21})

    def test_unary_minus(self):
        self.assertEqual(lexane.execute("-5 + 2")["result"], -3)

    def test_integer_division(self):
        self.assertEqual(lexane.execute("7 / 2")["result"], 3)
        self.assertEqual(lexane.execute("-7 / 2")["result"], -3)

    def test_undefined_variable(self):
        with self.assertRaises(lexane.LexaneError) as ctx:
            lexane.execute("missing + 1")
        self.assertEqual(ctx.exception.code, "SEM001")

    def test_division_by_zero(self):
        with self.assertRaises(lexane.LexaneError) as ctx:
            lexane.execute("10 / 0")
        self.assertEqual(ctx.exception.code, "RUN001")

    def test_syntax_error_has_stable_code(self):
        with self.assertRaises(lexane.LexaneError) as ctx:
            lexane.execute("let x = ;")
        self.assertEqual(ctx.exception.code, "PAR003")

    def test_unexpected_character(self):
        with self.assertRaises(lexane.LexaneError) as ctx:
            lexane.tokenize("1 @ 2")
        self.assertEqual(ctx.exception.code, "LEX001")

    def test_ir_is_deterministic(self):
        source = "let x = 2 + 3; x * 4"
        self.assertEqual(lexane.compile_ir(source), lexane.compile_ir(source))
        self.assertEqual(
            lexane.canonical_json(lexane.compile_ir(source)),
            lexane.canonical_json(lexane.compile_ir(source)),
        )

    def test_receipt_is_reproducible(self):
        source = "let a = 5; a * a"
        first = lexane.compile_receipt(source)
        second = lexane.compile_receipt(source)
        self.assertEqual(first, second)
        self.assertEqual(len(first["source_sha256"]), 64)
        self.assertEqual(len(first["ir_sha256"]), 64)
        self.assertEqual(len(first["receipt_sha256"]), 64)

    def test_receipt_changes_with_source(self):
        a = lexane.compile_receipt("1 + 2")
        b = lexane.compile_receipt("1 + 3")
        self.assertNotEqual(a["receipt_sha256"], b["receipt_sha256"])

    def test_compatibility_label_preserved(self):
        receipt = lexane.compile_receipt("1")
        self.assertEqual(receipt["language"], "Lexane")
        self.assertEqual(receipt["compatibility"], "HuobzLang")


if __name__ == "__main__":
    unittest.main()
