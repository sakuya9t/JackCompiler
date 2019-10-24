import unittest

from default.JackTokenizer import JackTokenizer, Token


class TokenizerTest(unittest.TestCase):
    def test_tokenizer_array(self):
        tknzr = JackTokenizer('/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/ArrayTest/Main.jack')
        tknzr.output_tokens("arraytest.xml")

    def test_tokenizer_squaregame(self):
        tknzr = JackTokenizer('/home/sakuya/Dev/Nand2Tetris/nand2tetris/projects/10/Square/SquareGame.jack')
        tknzr.output_tokens("squaregametest.xml")

    def test_load_xml(self):
        string = '<integerConstant>30</integerConstant>'
        token = Token.load_xml(string)
        self.assertEqual(token.to_xml(), string)


if __name__ == '__main__':
    unittest.main()
