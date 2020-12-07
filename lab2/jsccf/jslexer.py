from enum import Enum
from typing import List, Tuple
import re


class TokenType(Enum):
    SKIP = 0
    MULTILINE_STRING = 1
    SINGLE_LINE_STRING = 2
    MULTILINE_COMMENT = 3
    SINGLE_LINE_COMMENT = 4
    WHITESPACE = 5
    NEWLINE = 6
    IDENTIFIER = 7
    KEYWORD = 8


class Token:
    def __init__(self, text, token_type: TokenType, line_number):
        self.text = text
        self.token_type = token_type
        self.line_number = line_number

    def __str__(self):
        return f"{self.text}, {self.token_type}, ln:{self.line_number}"


JS_KEYWORDS = [
    "abstract", "arguments", "await*", "boolean",
    "break", "byte", "case", "catch",
    "char", "class*", "const", "continue",
    "debugger", "default", "delete", "do",
    "double", "else", "enum*", "eval",
    "export*", "extends*", "false", "final",
    "finally", "float", "for", "function",
    "goto", "if", "implements", "import*",
    "in", "instanceof", "int", "interface",
    "let*", "long", "native", "new",
    "null", "package", "private", "protected",
    "public", "return", "short", "static",
    "super*", "switch", "synchronized", "this",
    "throw", "throws", "transient", "true",
    "try", "typeof", "var", "void",
    "volatile", "while", "with", "yield", "let", "class", "constructor", "exports"
]

is_whitespace = re.compile(r"\s+")
is_token_start = re.compile(r"[a-zA-Z_\$]")
is_token_inside = re.compile(r"[a-zA-Z_0-9\$]*")


def count_newlines(s, pos):
    return s[0:pos].count('\n') + 1


def lex_file(content: str, args) -> List[Token]:
    tokens = []
    pos = 0
    s = content
    buff = ""
    while pos < len(s):
        if s[pos] == '"' or s[pos] == "'":
            c = "'" if s[pos] == "'" else '"'
            buff += s[pos]
            pos += 1
            while pos < len(s) and s[pos] != c and s[pos] != '\n':
                buff += s[pos]
                pos += 1
            if s[pos] == c:
                buff += s[pos]
                pos += 1
            tokens.append(Token(buff, TokenType.SINGLE_LINE_STRING, count_newlines(s, pos)))
            buff = ""
            continue
        elif s[pos] == '`':
            start_pos = pos
            buff += s[pos]
            pos += 1
            while s[pos] != "`" and pos < len(s):
                buff += s[pos]
                pos += 1
            if s[pos] == "`":
                buff += s[pos]
                pos += 1
            tokens.append(Token(buff, TokenType.MULTILINE_STRING, count_newlines(s, start_pos)))
            buff = ""
            continue
        elif s[pos] == "/":
            buff += s[pos]
            pos += 1
            if pos < len(s) and s[pos] == "/":
                buff += s[pos]
                pos += 1
                while s[pos] != '\n' and pos < len(s):
                    buff += s[pos]
                    pos += 1
                tokens.append(Token(buff, TokenType.SINGLE_LINE_COMMENT, count_newlines(s, pos)))
                buff = ""
                continue
            elif pos < len(s) and s[pos] == "*":
                start_pos = pos
                buff += s[pos]
                pos += 1
                while s[pos:pos + 2] != '*/' and pos + 1 < len(s):
                    buff += s[pos]
                    pos += 1
                if s[pos:pos + 2] == '*/':
                    buff += "*/"
                    pos += 2
                tokens.append(Token(buff, TokenType.MULTILINE_COMMENT, count_newlines(s, start_pos)))
                buff = ""
                continue
        elif s[pos] == "\n":
            tokens.append(Token(s[pos], TokenType.NEWLINE, count_newlines(s, pos)))
            pos += 1
            continue
        elif is_whitespace.fullmatch(s[pos]):
            tokens.append(Token(s[pos], TokenType.WHITESPACE, count_newlines(s, pos)))
            pos += 1
            continue
        elif is_token_start.fullmatch(s[pos]):
            buff += s[pos]
            pos += 1
            while pos < len(s) and is_token_inside.fullmatch(s[pos]):
                buff += s[pos]
                pos += 1
            if buff in JS_KEYWORDS:
                tokens.append(Token(buff, TokenType.KEYWORD, count_newlines(s, pos)))
            else:
                tokens.append(Token(buff, TokenType.IDENTIFIER, count_newlines(s, pos)))
            buff = ""
            continue
        else:
            tokens.append(Token(s[pos], TokenType.SKIP, count_newlines(s, pos)))
            pos += 1
    return tokens
