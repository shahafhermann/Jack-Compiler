TYPES_DIC = {"KEYWORD": 1, "SYMBOL": 2, "IDENTIFIER": 3,
             "INT_CONST": 4, "STRING_CONST": 5, "CLASS": "class",
             "METHOD": "method", "FUNCTION": "function",
             "CONSTRUCTOR": "constructor", "INT": "int", "BOOLEAN":
             "boolean", "CHAR": "char", "VOID": "void", "VAR":
             "var", "STATIC": "static", "FIELD": "field", "LET":
             "let", "DO": "do", "IF": "if", "ELSE": "else",
             "WHILE": "while", "RETURN": "return", "TRUE": "true",
             "FALSE": "false", "NULL": "null", "THIS": "this"}


class JackTokenizer:
    KEYWORDS = {"class", "constructor", "function", "method",
                "field", "static", "var", "int", "char", "boolean",
                "void", "true", "false", "null", "this", "let", "do",
                "if", "else", "while", "return"}
    SYMBOLS = {"{", "}", "(", ")", ".", ",", ";", "+", "-", "*", "/",
               "&", "|", "<", ">", "=", "~", "[", "]"}

    def __init__(self, in_file):
        self.__str_file = ""
        self.__token_counter = -1
        self.__current_token = None
        with open(in_file, "r") as file:
            for line in file:
                self.__str_file += line
        self.__tokens_list = self.__tokenize()

    def __tokenize(self):
        """
        Splits the file into tokens.
        :return: a list of all the tokens in the input file.
        """
        token_list = []
        buffer = ""
        in_string = False
        comment1 = False
        comment2 = False
        comment_flag = ""
        for c in self.__str_file:
            if not in_string:
                if c == '/' or c == "*":
                    comment_flag += c
                else:
                    comment_flag = ""
            if comment_flag == "/*" and not comment1 and not comment2:
                comment1 = True
                comment_flag = ""
                del(token_list[-1:])
            if comment_flag[-2:] == "*/" and comment1:
                comment1 = False
                comment_flag = ""
                continue
            if comment_flag == "//" and not comment1 and not comment2:
                if not comment2:
                    del (token_list[-1:])
                comment2 = True
                comment_flag = ""
            if c == "\n" and comment2:
                comment2 = False
                comment_flag = ""
                continue
            if not comment1 and not comment2:
                if c == '"':
                    if in_string:
                        buffer += c
                        in_string = False
                    else:
                        in_string = True
                        buffer += c
                elif in_string:
                    buffer += c
                elif c == " " or c == "\t" or c == "\r" or c == "\n" or c in self.SYMBOLS:
                    if buffer != "":
                        token_list.append(buffer)
                    if c in self.SYMBOLS:
                        token_list.append(c)
                    buffer = ""
                else:
                    buffer += c
        return token_list

    def has_more_tokens(self):
        """
        Checks if there are more tokens in the input.
        :return: True if there are more tokens in the input,
        False otherwise.
        """
        return self.__token_counter < len(self.__tokens_list)-1

    def peek(self):
        """
        :return: the next token after the current token (without
        advancing the tokenizer).
        """
        return self.__tokens_list[self.__token_counter + 1]

    def advance(self):
        """
        advance the current token, should
        only be called if has_more_tokens() id TRUE
        """
        self.__token_counter += 1
        self.__current_token = self.__tokens_list[self.__token_counter]

    def token_type(self):
        """
        :return: the type of the current token
        """
        if self.__current_token in self.KEYWORDS:
            return TYPES_DIC["KEYWORD"]
        elif self.__current_token in self.SYMBOLS:
            return TYPES_DIC["SYMBOL"]
        elif self.__current_token.isdigit():
            return TYPES_DIC["INT_CONST"]
        elif self.__current_token[0] == '"':
            return TYPES_DIC["STRING_CONST"]
        else:
            return TYPES_DIC["IDENTIFIER"]

    def keyword(self):
        """
        should be called only if token_type() is KEYWORD
        :return: the keyword which is the current token.
        """
        if self.__current_token == "class":
            return TYPES_DIC["CLASS"]
        elif self.__current_token == "method":
            return TYPES_DIC["METHOD"]
        elif self.__current_token == "function":
            return TYPES_DIC["FUNCTION"]
        elif self.__current_token == "constructor":
            return TYPES_DIC["CONSTRUCTOR"]
        elif self.__current_token == "int":
            return TYPES_DIC["INT"]
        elif self.__current_token == "boolean":
            return TYPES_DIC["BOOLEAN"]
        elif self.__current_token == "char":
            return TYPES_DIC["CHAR"]
        elif self.__current_token == "void":
            return TYPES_DIC["VOID"]
        elif self.__current_token == "var":
            return TYPES_DIC["VAR"]
        elif self.__current_token == "static":
            return TYPES_DIC["STATIC"]
        elif self.__current_token == "field":
            return TYPES_DIC["FIELD"]
        elif self.__current_token == "let":
            return TYPES_DIC["LET"]
        elif self.__current_token == "do":
            return TYPES_DIC["DO"]
        elif self.__current_token == "if":
            return TYPES_DIC["IF"]
        elif self.__current_token == "else":
            return TYPES_DIC["ELSE"]
        elif self.__current_token == "while":
            return TYPES_DIC["WHILE"]
        elif self.__current_token == "return":
            return TYPES_DIC["RETURN"]
        elif self.__current_token == "true":
            return TYPES_DIC["TRUE"]
        elif self.__current_token == "false":
            return TYPES_DIC["FALSE"]
        elif self.__current_token == "null":
            return TYPES_DIC["NULL"]
        elif self.__current_token == "this":
            return TYPES_DIC["THIS"]

    def symbol(self):
        """
        should be called only if token_type() is SYMBOL
        :return: the character which is the current token.
        """
        return self.__current_token

    def identifier(self):
        """
        should be called only if token_type() is IDENTIFIER
        :return: the identifier which is the current token.
        """
        return self.__current_token

    def int_val(self):
        """
        should be called only if token_type() is INT_CONST
        :return: the integer value of the current token.
        """
        return int(self.__current_token)

    def string_val(self):
        """
        should be called only if token_type() is STRING_CONST
        :return: the string value of the current token without the
        double quotes.
        """
        return self.__current_token[1:-1]

    def get_token_count(self):
        """
        :return: The current token's index in the list
        """
        return self.__token_counter

    def jump_to(self, n):
        """
        Jump to the given token index and continue tokenizing from there
        :param n: The index to jump to
        """
        self.__token_counter = n
        self.__current_token = self.__tokens_list[n]
