from enum import Enum
from typing import Tuple

from constants import GROOVY_PUNCTUATION, GROOVY_KEYWORDS, GROOVY_WHITESPACE, GROOVY_QUOTE


class TokenType(Enum):
    ID = 0
    KEYWORD = 1
    PUNCTUATION = 2
    SPACE = 3
    STRING_LITERAL = 4
    NUMERIC_LITERAL = 5
    LINE_COMMENT = 6
    MULTILINE_COMMENT = 7


class GroovyLexer(object):

    def __init__(self):
        language_extension = '.groovy'

    @staticmethod
    def lex(path_to_file: str):
        f = open(path_to_file, 'r')
        try:
            string = f.read()
        finally:
            f.close()

        tokens = []

        while len(string):
            check, tmp_s = GroovyLexer.lex_id(string)
            if check != "":
                string = tmp_s
                if GroovyLexer.is_keyword(check):
                    tokens.append((TokenType.KEYWORD, check))
                else:
                    tokens.append((TokenType.ID, check))
                continue

            check, tmp_s = GroovyLexer.lex_line_comment(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.LINE_COMMENT, check))
                continue

            check, tmp_s = GroovyLexer.lex_multiline_comment(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.MULTILINE_COMMENT, check))
                continue

            check, tmp_s = GroovyLexer.lex_number(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.NUMERIC_LITERAL, check))
                continue

            check, tmp_s = GroovyLexer.lex_space(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.SPACE, check))
                continue

            check, tmp_s = GroovyLexer.lex_punctuation(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.PUNCTUATION, check))
                continue

            check, tmp_s = GroovyLexer.lex_string(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.STRING_LITERAL, check))
                continue

            check, tmp_s = GroovyLexer.lex_string(string)
            if check != "":
                string = tmp_s
                tokens.append((TokenType.STRING_LITERAL, check))
                continue

            string = string[1:]

        return tokens

    @staticmethod
    def lex_id(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0].isalpha() or string[0] == '_' or string[0] == '$':
            while len(string):
                if string[0].isalpha() or string[0].isdigit() or string[0] == '_' or string[0] == '$':
                    buff = buff + string[0]
                    string = string[1:]
                else:
                    break
        return buff, string

    @staticmethod
    def is_keyword(string: str) -> bool:
        return string in GROOVY_KEYWORDS

    @staticmethod
    def lex_number(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0] == '-' and string[1].isdigit():
            buff = buff + string[0]
            string = string[1:]

        if string[0:2] == '0b' or string[0:2] == '0x':
            buff = string[0:2]
            string = string[2:]

        if string[0].isnumeric():
            while len(string):
                if string[0].isnumeric() or string[0] == '.':
                    buff = buff + string[0]
                    string = string[1:]
                else:
                    break



        return buff, string

    @staticmethod
    def lex_space(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0] in GROOVY_WHITESPACE:
            buff = buff + string[0]
            string = string[1:]
        return buff, string

    @staticmethod
    def lex_punctuation(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0] in GROOVY_PUNCTUATION:
            buff = buff + string[0]
            string = string[1:]
        return buff, string

    @staticmethod
    def lex_string(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0] in GROOVY_QUOTE:
            quote_type = string[0]
            buff = buff + string[0]
            string = string[1:]
            while len(string) and string[0] != quote_type:
                buff = buff + string[0]
                string = string[1:]
            buff = buff + string[0]
            string = string[1:]
        return buff, string

    @staticmethod
    def lex_line_comment(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0:2] == '//':
            while string[0] != '\n':
                buff = buff + string[0]
                string = string[1:]
        return buff, string

    @staticmethod
    def lex_multiline_comment(string: str, tokens) -> Tuple[str, str]:
        buff = ""
        if string[0:2] == '/*':
            while string[0:2] != '*/':
                buff = buff + string[0]
                string = string[1:]
            buff = buff + string[0:2]
            string = string[2:]
        return buff, string


if __name__ == '__main__':
    lex_res = GroovyLexer.lex("test.groovy")
    for lex in lex_res:
        print(lex)
