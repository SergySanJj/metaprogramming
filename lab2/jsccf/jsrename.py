from enum import Enum
from typing import List, Tuple, Dict

from jsccf.jslexer import Token, JS_KEYWORDS


class IdentifierType(Enum):
    VARIABLE = 0
    FUNCTION = 1
    CONST = 2
    CLASS = 3


VARIABLE_KEYWORDS = ["var", "let"]
CONST_KEYWORDS = ["const"]
CLASS_KEYWORDS = ["class"]


class Renamer:
    def __init__(self):
        # (file, identifier_token, IdentifierType)
        self.declarations = []

    def find_declarations(self, code_tree: Dict[str, List[Tuple[str, Token, int]]], args):
        for f, k in code_tree.items():
            print(f)
            i = 0
            while i < len(k):
                s, t, line = k[i]
                print(s, t, line)
                if t == Token.IDENTIFIER:
                    search_p = i - 1
                    while search_p > 0 and k[search_p][0] not in JS_KEYWORDS \
                            and k[search_p][1] != Token.SKIP \
                            and k[search_p][1] != Token.IDENTIFIER:
                        search_p -= 1

                    if k[search_p][0] in VARIABLE_KEYWORDS:
                        self.declarations.append((f, k[i], IdentifierType.VARIABLE))
                        i += 1
                        continue
                    if k[search_p][0] in CONST_KEYWORDS:
                        self.declarations.append((f, k[i], IdentifierType.CONST))
                        i += 1
                        continue
                    if k[search_p][0] in CLASS_KEYWORDS:
                        self.declarations.append((f, k[i], IdentifierType.CLASS))
                        i += 1
                        continue
                i += 1

        for s in self.declarations:
            print(s)
        return self.declarations
