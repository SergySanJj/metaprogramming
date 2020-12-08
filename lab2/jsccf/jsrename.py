import logging
import os
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
    TRUE_CONST = 7


VARIABLE_KEYWORDS = ["var", "let"]
CONST_KEYWORDS = ["const"]
CLASS_KEYWORDS = ["class"]


class Scopes(Enum):
    GLOBAL = 0
    CLASS = 1
    METHOD = 2
    LIST = 3
    DICT = 4
    LAMBDA = 5
    ARGUMENTS = 6
    CONDITION = 7
    IF_ELSE = 8
    CLASS_METHOD = 9
    CALL_ARGS = 10


class Scope:
    def __init__(self, start, closing_symbol, state: Scopes):
        self.start = start
        self.end = start
        self.closing_symbol = closing_symbol
        self.state = state

    def __str__(self):
        return f"{self.start}, {self.end}  : {self.state}"


class Declaration:
    def __init__(self, file, identifier_token: Token, identifier_type: IdentifierType,
                 scope: Scope):
        self.file = file
        self.identifier_token = identifier_token
        self.identifier_type = identifier_type
        self.scope = scope
        self.references: List[Token] = []

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
        return f"{self.file}: {self.identifier_type}:   {self.identifier_token.text}   ({self.scope})"


class Message:
    def __init__(self, file, line, description):
        self.file = file
        self.line = line
        self.description = description

    def __str__(self):
        return f"{self.file}: ln:{self.line} - {self.description}"


class Renamer:
    def __init__(self):
        self.declarations: List[Declaration] = []

    def find_declarations(self, code_tree: Dict[str, List[Token]], args):
        for f, k in code_tree.items():
            i = 0
            global_scope = Scope(0, "", Scopes.GLOBAL)
            global_scope.end = len(k)
            scopes = [global_scope]

            while i < len(k):
                cur_t = k[i]
                t = cur_t.token_type

                if t == TokenType.WHITESPACE:
                    i += 1
                    continue

                if t == TokenType.IDENTIFIER:
                    if scopes[len(scopes) - 1].state == Scopes.CLASS:

                        # check on class method
                        start_pos = self.next_t(i, k, text_not_in=["(", ";", ".", "{"],
                                                token_type_not_in=[TokenType.IDENTIFIER, TokenType.KEYWORD])
                        if start_pos < len(k) and k[start_pos].text == "(":
                            has_func_body = self.next_t(start_pos, k, text_not_in=["{", ".", ";", "("],
                                                        token_type_not_in=[TokenType.KEYWORD])

                            if has_func_body < len(k) and k[has_func_body].text == "{":
                                function_scope = Scope(has_func_body, "}", Scopes.CLASS_METHOD)
                                scopes.append(function_scope)

                                self.declarations.append(Declaration(f, k[i], IdentifierType.CLASS_METHOD,
                                                                     scopes[len(scopes) - 2]))
                                func_args = Scope(start_pos, ")", Scopes.ARGUMENTS)
                                scopes.append(func_args)

                                continue

                        # check on class variable
                        start_pos = self.next_t(i, k, text_not_in=["=", ";", "."])

                        if start_pos < len(k) and k[start_pos].text == "=":
                            self.declarations.append(Declaration(f, k[i], IdentifierType.CLASS_VARIABLE,
                                                                 scopes[len(scopes) - 1]))
                            i += 1
                            continue

                    elif scopes[len(scopes) - 1].state in [Scopes.METHOD, Scopes.CLASS_METHOD, Scopes.GLOBAL]:
                        if scopes[len(scopes) - 1].state not in [Scopes.GLOBAL]:
                            # check on function
                            start_pos = self.next_t(i, k, text_not_in=["(", ";", ".", "{"])
                            if start_pos < len(k) and k[start_pos].text == "(":
                                has_func_body = self.next_t(start_pos, k, text_not_in=["{", ".", ";", "("],
                                                            token_type_not_in=[TokenType.KEYWORD])
                                if has_func_body < len(k) and k[has_func_body].text == "{":
                                    function_scope = Scope(has_func_body, "}", Scopes.METHOD)
                                    scopes.append(function_scope)

                                    self.declarations.append(Declaration(f, k[i], IdentifierType.FUNCTION,
                                                                         scopes[len(scopes) - 1]))
                                    func_args = Scope(start_pos, ")", Scopes.ARGUMENTS)
                                    scopes.append(func_args)
                                    i = start_pos
                                    continue
                        else:
                            # check on function
                            start_pos = self.next_t(i, k, text_not_in=["(", ";", ".", "{"])
                            if start_pos < len(k) and k[start_pos].text == "(":
                                has_func_body = self.next_t(start_pos, k, text_not_in=["{", ".", ";", "("],
                                                            token_type_not_in=[TokenType.KEYWORD])
                                if has_func_body < len(k) and k[has_func_body].text == "{":
                                    has_no_function = self.next_t(i, k, text_not_in=["function", "{", "("])
                                    if has_no_function < len(k) and k[has_no_function].text != "function":
                                        self.declarations.append(Declaration(f, k[i], IdentifierType.FUNCTION,
                                                                             scopes[len(scopes) - 1]))
                                        function_scope = Scope(has_func_body, "}", Scopes.METHOD)
                                        scopes.append(function_scope)
                                        func_args = Scope(start_pos, ")", Scopes.ARGUMENTS)
                                        scopes.append(func_args)
                                        i = start_pos
                                        continue

                        # check on variable
                        search_p = self.prev_t(i, k, text_not_in=["let", "const", "var"],
                                               token_type_not_in=[TokenType.SKIP, TokenType.IDENTIFIER])
                        if search_p >= 0 and k[search_p].text in VARIABLE_KEYWORDS:
                            variable_scope = scopes[len(scopes) - 1] if k[search_p].text == "let" else \
                                scopes[len(scopes) - 2]
                            self.declarations.append(Declaration(f, k[i], IdentifierType.VARIABLE, variable_scope))
                            i += 1
                        elif search_p >= 0 and k[search_p].text in CONST_KEYWORDS:
                            variable_scope = scopes[len(scopes) - 1]

                            const_val = self.next_t(i, k,
                                                    token_type_not_in=[TokenType.NUMBER, TokenType.MULTILINE_STRING,
                                                                       TokenType.SINGLE_LINE_STRING, TokenType.KEYWORD,
                                                                       TokenType.IDENTIFIER, TokenType.BOOL])
                            if const_val < len(k) and k[const_val].token_type in [TokenType.NUMBER,
                                                                                  TokenType.MULTILINE_STRING,
                                                                                  TokenType.SINGLE_LINE_STRING,
                                                                                  TokenType.BOOL]:
                                self.declarations.append(
                                    Declaration(f, k[i], IdentifierType.TRUE_CONST, variable_scope))
                                i += 1
                            else:
                                self.declarations.append(Declaration(f, k[i], IdentifierType.CONST, variable_scope))
                                i += 1

                        if search_p >= 0 and k[search_p].text in ["let", "var", "const"]:
                            dict_search = self.next_t(search_p, k, text_not_in=["{", ";"],
                                                      token_type_not_in=[TokenType.KEYWORD, TokenType.IDENTIFIER])
                            if dict_search < len(k) and k[dict_search].text == "{":
                                dict_scope = Scope(i, "}", Scopes.DICT)
                                scopes.append(dict_scope)

                elif t == TokenType.KEYWORD and cur_t.text == "class":
                    class_scope = Scope(i, "}", Scopes.CLASS)
                    scopes.append(class_scope)
                    while i < len(k) and k[i].token_type != TokenType.IDENTIFIER:
                        i += 1
                    # class C {}
                    if k[i].token_type == TokenType.IDENTIFIER:
                        self.declarations.append(Declaration(f, k[i], IdentifierType.CLASS, scopes[len(scopes) - 2]))
                    while i < len(k) and k[i].text != "{":
                        i += 1
                    if k[i].text == "{":
                        class_scope.start = i
                    i += 1
                    continue
                elif t == TokenType.KEYWORD and cur_t.text == "function":
                    # function f(){}
                    f_name = self.next_t(i, k, text_not_in=["(", "{"], token_type_not_in=[TokenType.IDENTIFIER])
                    if f_name < len(k) and k[f_name].token_type == TokenType.IDENTIFIER:
                        f_args = self.next_t(f_name, k, text_not_in=["("])
                        f_body = self.next_t(f_name, k, text_not_in=["{"])
                        if f_args < len(k) and k[f_args].text == "(":
                            if f_body < len(k) and k[f_body].text == "{":
                                function_scope = Scope(f_body, "}", Scopes.METHOD)
                                func_args = Scope(f_args, ")", Scopes.ARGUMENTS)
                                self.declarations.append(Declaration(f, k[f_name], IdentifierType.FUNCTION,
                                                                     scopes[len(scopes) - 2]))

                                scopes.append(function_scope)
                                scopes.append(func_args)
                                i = f_args + 1
                                continue
                    # var|let|const f = function () {}
                    elif f_name < len(k) and k[f_name].text == "(":
                        f_args = f_name
                        f_name = self.prev_t(i, k, token_type_not_in=[TokenType.IDENTIFIER])
                        if f_name < len(k) and k[f_name].token_type == TokenType.IDENTIFIER:
                            f_body = self.next_t(i, k, text_not_in=["{"])
                            if f_body < len(k) and k[f_body].text == "{":
                                function_scope = Scope(f_body, "}", Scopes.METHOD)
                                func_args = Scope(f_args, ")", Scopes.ARGUMENTS)
                                self.declarations.append(Declaration(f, k[f_name], IdentifierType.FUNCTION,
                                                                     scopes[len(scopes) - 2]))

                                scopes.append(function_scope)
                                scopes.append(func_args)
                                i = f_args + 1
                                continue

                elif t == TokenType.SKIP:
                    if cur_t.text == "[":
                        list_scope = Scope(i, "]", Scopes.LIST)
                        scopes.append(list_scope)
                    elif cur_t.text == "{":
                        if scopes[len(scopes) - 1].state in [Scopes.METHOD, Scopes.CLASS_METHOD]:
                            if scopes[len(scopes) - 1].start != i:
                                dict_scope = Scope(i, "}", Scopes.DICT)
                                scopes.append(dict_scope)

                    elif cur_t.text in ["}", "]", ")"] and len(scopes) > 0:
                        if scopes[len(scopes) - 1].closing_symbol == cur_t.text:
                            scopes[len(scopes) - 1].end = i
                            scopes.pop()
                    i += 1
                    continue
                elif t == TokenType.NEWLINE:
                    i += 1
                    continue
                i += 1

        return self.declarations

    def has_declaration(self, token, token_file, token_pos):
        decl = self.get_declaration(token, token_file, token_pos)
        return decl is not None

    def get_declaration(self, token, token_file, token_pos):
        for s in self.declarations:
            if s.file == token_file:
                if s.identifier_token.text == token.text:

                    if s.scope.start <= token_pos <= s.scope.end:
                        return s
        return None

    def find_scope_end(self, end_symbol, search_start, tokens: List[Token]):
        i = search_start
        while i < len(tokens) and tokens[i].text != end_symbol:
            i += 1
        if tokens[i].text == end_symbol:
            return i
        else:
            return -1

    def prev_t(self, pos, k: List[Token], text_not_in=None, token_type_not_in=None):
        if token_type_not_in is None:
            token_type_not_in = []
        if text_not_in is None:
            text_not_in = []
        search_p = pos - 1
        while search_p > 0 and k[search_p].token_type not in token_type_not_in \
                and k[search_p].text not in text_not_in:
            search_p -= 1
        return search_p

    def next_t(self, pos, k: List[Token], text_not_in=None, token_type_not_in=None):
        if token_type_not_in is None:
            token_type_not_in = []
        if text_not_in is None:
            text_not_in = []
        search_p = pos + 1
        while search_p < len(k) and k[search_p].token_type not in token_type_not_in \
                and k[search_p].text not in text_not_in:
            search_p += 1
        return search_p

    def build_references(self, code_tree: Dict[str, List[Token]], args):
        for f, k in code_tree.items():
            i = 0
            while i < len(k):
                cur_t = k[i]
                if cur_t.token_type == TokenType.IDENTIFIER:
                    if self.has_declaration(cur_t, f, i):
                        dec = self.get_declaration(cur_t, f, i)
                        dec.add_reference(cur_t)
                i += 1

    def rename(self, code_tree: Dict[str, List[Token]], args):
        error_messages = []
        rename_messages = []

        for dec in self.declarations:
            s = dec.identifier_token.text
            res = s
            error_description = ""
            if dec.identifier_type in [IdentifierType.CLASS]:
                res = self.to_camelcase(s, first_upper=True)
                error_description = \
                    f"6.2.2: Class, interface, record, and typedef names are written in UpperCamelCase. Got '{s}'"
            elif dec.identifier_type in [
                IdentifierType.FUNCTION, IdentifierType.CLASS_METHOD,
                IdentifierType.CLASS_VARIABLE, IdentifierType.VARIABLE,
                IdentifierType.EXPORTS, IdentifierType.CONST
            ]:
                res = self.to_camelcase(s)
                error_description = \
                    f"6.2.3: Method and variable names are written in lowerCamelCase. Got '{s}' "
            elif dec.identifier_type in [IdentifierType.TRUE_CONST]:
                res = self.to_true_constant(s)
                error_description = \
                    f"6.2.5: Constant names use CONSTANT_CASE: all uppercase letters, with words separated by " \
                    f"underscores. Got '{s}' "
            else:
                logging.error(f"UNKNOWN IDENTIFIER: {dec.identifier_type}")

            if s != res:
                for reference in dec.references:
                    error_messages.append(Message(os.path.abspath(dec.file), reference.line_number, error_description))
                if args.fix:
                    change_description = f"Changing '{s}' symbol to '{res}'"
                    for reference in dec.references:
                        rename_messages.append(Message(os.path.abspath(dec.file), reference.line_number, change_description))
                    dec.rename(res)
        return error_messages, rename_messages

    def to_camelcase(self, s: str, first_upper=False) -> str:
        res = ""
        words = self.split_to_words(s)
        for p in words:
            res += p.lower().capitalize()

        if first_upper:
            return res.capitalize()
        else:
            if len(res) > 1:
                return res[0].lower() + res[1:]
            elif len(res) == 1:
                return res[0].lower()
            else:
                return res

    def to_true_constant(self, s: str) -> str:
        words = self.split_to_words(s)
        res = words[0].upper()
        for p in words[1:]:
            tmp = p.upper()
            if tmp == "":
                continue
            res += "_" + tmp

        return res

    def split_to_words(self, s: str):
        words = []
        curr_word = ''
        for curr, last in zip(s, '_' + s[:-1]):
            if curr.isupper() and last.islower():
                words.append(curr_word)
                curr_word = ''
            elif curr == '_':
                words.append(curr_word)
                curr_word = ''
            if curr != '_':
                curr_word += curr
        words.append(curr_word)
        return words
