from enum import Enum
from typing import List, Tuple, Dict

from jsccf.jslexer import TokenType, JS_KEYWORDS, Token


class IdentifierType(Enum):
    VARIABLE = 0
    FUNCTION = 1
    CONST = 2
    CLASS = 3
    EXPORTS = 4
    CLASS_VARIABLE = 5
    CLASS_METHOD = 6


VARIABLE_KEYWORDS = ["var", "let"]
CONST_KEYWORDS = ["const"]
CLASS_KEYWORDS = ["class"]


class States(Enum):
    GLOBAL = 0
    CLASS = 1
    METHOD = 2
    LIST = 3
    DICT = 4
    LAMBDA = 5


class Scope:
    def __init__(self, start, closing_symbol):
        self.start = start
        self.end = start
        self.closing_symbol = closing_symbol

    def __str__(self):
        return f"{self.start}, {self.end}"


class Declaration:
    def __init__(self, file, identifier_token: Token, identifier_type: IdentifierType,
                 scope: Scope):
        self.file = file
        self.identifier_token = identifier_token
        self.identifier_type = identifier_type
        self.scope = scope
        self.references = []

    def is_reference(self, ref, pos):
        if self.scope.start <= pos <= self.scope.end:
            if self.identifier_token[0] == ref[0]:
                return True

    def add_reference(self, ref):
        self.references.append(ref)

    def rename(self, new_name):
        self.identifier_token.text = new_name
        for ref in self.references:
            ref.text = new_name

    def __str__(self):
        return f"{self.file}:  {self.identifier_token.text}   ({self.scope})"


class Renamer:
    def __init__(self):
        self.declarations = []
        self.states = {States.GLOBAL: True,
                       States.CLASS: False,
                       States.METHOD: False,
                       States.LIST: False,
                       States.DICT: False,
                       States.LAMBDA: False,
                       }

    def find_declarations(self, code_tree: Dict[str, List[Token]], args):
        for f, k in code_tree.items():
            print(f)
            i = 0
            balance = 0
            global_scope = Scope(0, "")
            global_scope.end = len(k)
            scopes = [global_scope]

            while i < len(k):
                cur_t = k[i]
                t = cur_t.token_type

                if t == TokenType.WHITESPACE:
                    i += 1
                    continue

                if t != TokenType.NEWLINE:
                    print(i, cur_t)

                if t == TokenType.SKIP:
                    if cur_t.text == "{":
                        balance += 1
                        scopes.append(Scope(i, "}"))
                    elif cur_t.text == "[":
                        balance += 1
                        scopes.append(Scope(i, "]"))
                    elif cur_t.text == "(":
                        balance += 1
                        scopes.append(Scope(i, ")"))

                    elif cur_t.text in ["}", "]", ")"]:
                        balance -= 1
                        scopes[len(scopes) - 1].end = i
                        print("Scope ", scopes[len(scopes) - 1])
                        scopes.pop()
                    i += 1
                    continue

                # if t == TokenType.IDENTIFIER:
                #     search_p = i - 1
                #     while search_p > 0 and k[search_p][0] not in JS_KEYWORDS \
                #             and k[search_p][1] != TokenType.SKIP \
                #             and k[search_p][1] != TokenType.IDENTIFIER:
                #         search_p -= 1
                #
                #     if k[search_p][0] in VARIABLE_KEYWORDS:
                #         self.declarations.append((f, k[i], IdentifierType.VARIABLE))
                #         i += 1
                #         continue
                #     if k[search_p][0] in CONST_KEYWORDS:
                #         self.declarations.append((f, k[i], IdentifierType.CONST))
                #         i += 1
                #         continue
                #     if k[search_p][0] in CLASS_KEYWORDS:
                #         self.declarations.append((f, k[i], IdentifierType.CLASS))
                #         i += 1
                #         continue
                #
                #     search_p = i - 1
                #     while search_p > 0 and k[search_p][0] not in ["exports", "this"] and k[search_p][
                #         1] != TokenType.IDENTIFIER:
                #         if k[search_p][1] == TokenType.SKIP and k[search_p][0] != ".":
                #             break
                #         search_p -= 1
                #     if k[search_p][0] == "exports":
                #         self.declarations.append((f, k[i], IdentifierType.EXPORTS))
                #         i += 1
                #         continue
                #     if k[search_p][0] == "this":
                #         self.declarations.append((f, k[i], IdentifierType.CLASS_VARIABLE))
                #         i += 1
                #         continue
                #
                # if t == TokenType.SKIP:

                i += 1

        for s in self.declarations:
            print(s)
        return self.declarations

    def has_declaration(self, token, token_file, inside_file=False):
        for s in self.declarations:
            if s[1][0] == token[0]:
                if inside_file:
                    if s[0] == token_file:
                        return True
                else:
                    return True
        return False

    def find_scope_end(self, end_symbol, search_start, tokens: List[Token]):
        i = search_start
        while i < len(tokens) and tokens[i].text != end_symbol:
            i += 1
        if tokens[i].text == end_symbol:
            return i
        else:
            return -1
