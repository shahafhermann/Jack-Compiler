from JackTokenizer import *
from VMWriter import *
from SymbolTable import *


class CompilationEngine:

    def __init__(self, input_file, output):
        self.__input = input_file
        self.__output = output
        self.__tokenizer = JackTokenizer(input_file)
        self.__vmwriter = None
        self.__class_symbols = SymbolTable()
        self.__subroutine_symbols = SymbolTable()
        self.__class_name = ""
        self.__method_list = []
        self.__while_count = 0
        self.__if_count = 0

    def __find_methods(self):
        """
        Goes through all of the tokens and adds each method name to the class's method_list.
        """
        while self.__advance():
            if self.__tokenizer.token_type() == TYPES_DIC["KEYWORD"] and \
                    self.__tokenizer.identifier() == TYPES_DIC["METHOD"]:
                self.__advance(n=2)
                self.__method_list.append(self.__tokenizer.identifier())
        self.__tokenizer.jump_to(-1)

    def __advance(self, n=1):
        """
        checks if there are more tokens in the class's tokenizer,
        and if so advances it.
        :return True if the advancement succeeded. False otherwise.
        """
        for i in range(n):
            if self.__tokenizer.has_more_tokens():
                self.__tokenizer.advance()
                continue
            return False
        return True

    def __get_type(self):
        """
        checks the type of the current token.
        :return The type of the current token.
        """
        if self.__tokenizer.token_type() == TYPES_DIC["IDENTIFIER"]:
            return self.__tokenizer.identifier()
        else:
            return self.__tokenizer.keyword()

    def compile_class_var_dec(self):
        """
        compiles class variable declaration. This function does not omit any code.
        """
        kind = self.__tokenizer.keyword()
        self.__advance()
        type = self.__get_type()
        self.__advance()
        self.__class_symbols.define(self.__tokenizer.identifier(), type, kind)
        self.__advance()
        while self.__tokenizer.symbol() == ',':
            self.__advance()
            self.__class_symbols.define(self.__tokenizer.identifier(), type, kind)
            self.__advance()
        self.__advance()  # advance the ';' token

    def compile_parameter_list(self):
        """
        compiles a subroutine's parameter list
        """
        if self.__tokenizer.token_type() != TYPES_DIC["SYMBOL"]:
            type = self.__get_type()
            self.__advance()
            name = self.__tokenizer.identifier()
            self.__subroutine_symbols.define(name, type, "argument")
            self.__advance()
            while self.__tokenizer.symbol() != ')':
                self.__advance()
                type = self.__get_type()
                self.__advance()
                name = self.__tokenizer.identifier()
                self.__subroutine_symbols.define(name, type, "argument")
                self.__advance()

    def compile_var_dec(self):
        """
        compiles a subroutine's variable declaration.
        """
        self.__advance()
        type = self.__get_type()
        self.__advance()
        name = self.__tokenizer.identifier()
        self.__subroutine_symbols.define(name, type, "VAR")
        self.__advance()
        while self.__tokenizer.symbol() == ',':
            self.__advance()
            name = self.__tokenizer.identifier()
            self.__subroutine_symbols.define(name, type, "VAR")
            self.__advance()
        self.__advance()  # Advances the ';' token

    def __compile_string(self):
        """
        Compiles a string
        """
        self.__vmwriter.write_push("constant", len(self.__tokenizer.identifier()))
        self.__vmwriter.write_call("String.new", 1)
        for c in self.__tokenizer.identifier():
            if c == '"':
                continue
            self.__vmwriter.write_push("constant", ord(c))
            self.__vmwriter.write_call("String.appendChar", 2)

    def compile_term(self):
        """
        Compiles a term.
        """
        if self.__tokenizer.token_type() == TYPES_DIC["KEYWORD"]:
            if self.__tokenizer.keyword() == "true":
                self.__vmwriter.write_push("constant", 1)
                self.__vmwriter.write_arithmetic("neg")
            elif self.__tokenizer.keyword() == "this":
                self.__vmwriter.write_push("pointer", 0)
            else:
                self.__vmwriter.write_push("constant", 0)
            self.__advance()
        elif self.__tokenizer.token_type() == TYPES_DIC["SYMBOL"]:
            if self.__tokenizer.symbol() == '(':
                self.__advance()  # Advance after the '(' token
                self.compile_expression()
                self.__advance()  # Advance after the ')' token
            else:
                op = self.__tokenizer.symbol()
                self.__advance()
                self.compile_term()
                self.__compile_operator(op, "term")
        else:
            if self.__tokenizer.peek() == '(' or self.__tokenizer.peek() == '.':
                self.__compile_subroutine_call()
            else:
                if self.__tokenizer.identifier().isdigit():
                    self.__vmwriter.write_push("constant", self.__tokenizer.identifier())
                    self.__advance()
                elif self.__tokenizer.identifier()[0] == '"':
                    self.__compile_string()
                    self.__advance()
                else:
                    self.__compile_var(True)

    def __compile_operator(self, op, caller):
        """
        Compile an operator command
        :param op: The operator to compile
        :param caller: The function that called this compilation process
        """
        if op == "+":
            self.__vmwriter.write_arithmetic("add")
        elif op == "-" and caller == "expression":
            self.__vmwriter.write_arithmetic("sub")
        elif op == "*":
            self.__vmwriter.write_call("Math.multiply", 2)
        elif op == "/":
            self.__vmwriter.write_call("Math.divide", 2)
        elif op == "&":
            self.__vmwriter.write_arithmetic("and")
        elif op == "|":
            self.__vmwriter.write_arithmetic("or")
        elif op == "<":
            self.__vmwriter.write_arithmetic("lt")
        elif op == ">":
            self.__vmwriter.write_arithmetic("gt")
        elif op == "=":
            self.__vmwriter.write_arithmetic("eq")
        elif op == "-":
            self.__vmwriter.write_arithmetic("neg")
        elif op == "~":
            self.__vmwriter.write_arithmetic("not")

    def compile_expression(self):
        """
        Compiles an expression.
        """
        self.compile_term()
        while self.__tokenizer.symbol() != ')' and self.__tokenizer.symbol() != ']' and \
                self.__tokenizer.symbol() != ';' and self.__tokenizer.symbol() != ',':
            op = self.__tokenizer.symbol()
            self.__advance()
            self.compile_term()
            self.__compile_operator(op, "expression")

    def __compile_var(self, push):
        """
        Compile a variable
        :param push: Decide if it should be a push or pop command
        """
        name = self.__tokenizer.identifier()
        if self.__subroutine_symbols.contains(name):
            kind = self.__subroutine_symbols.kind_of(name)
            index = self.__subroutine_symbols.index_of(name)
        else:
            kind = self.__class_symbols.kind_of(name)
            index = self.__class_symbols.index_of(name)
        if self.__tokenizer.peek() != "[":
            if push:
                self.__vmwriter.write_push(kind, index)
        else:
            self.__vmwriter.write_push(kind, index)
            self.__advance(n=2)  # Advance after the '[' token
            self.compile_expression()
            self.__vmwriter.write_arithmetic("add")
            if push:
                self.__vmwriter.write_pop("pointer", 1)
                self.__vmwriter.write_push("that", 0)
        self.__advance()  # Advance after the var

    def compile_let(self):
        """
        Compiles a let statement.
        """
        self.__advance()
        if self.__tokenizer.peek() != "[":
            name = self.__tokenizer.identifier()
            if self.__subroutine_symbols.contains(name):
                kind = self.__subroutine_symbols.kind_of(name)
                index = self.__subroutine_symbols.index_of(name)
            else:
                kind = self.__class_symbols.kind_of(name)
                index = self.__class_symbols.index_of(name)
            self.__advance(n=2)  # Advance after the '=' token
            self.compile_expression()
            self.__vmwriter.write_pop(kind, index)
        else:
            self.__compile_var(False)
            self.__advance()
            self.compile_expression()
            self.__vmwriter.write_pop("temp", 0)
            self.__vmwriter.write_pop("pointer", 1)
            self.__vmwriter.write_push("temp", 0)
            self.__vmwriter.write_pop("that", 0)
        self.__advance()

    def compile_if(self):
        """
        Compiles an if statement.
        """
        else_label = "ELSE_" + str(self.__if_count)
        end_label = "END_IF_" + str(self.__if_count)
        self.__if_count += 1
        self.__advance(n=2)
        self.compile_expression()
        self.__vmwriter.write_arithmetic("not")
        self.__vmwriter.write_if(else_label)
        self.__advance(n=2)
        self.compile_statements()
        self.__vmwriter.write_goto(end_label)
        self.__vmwriter.write_label(else_label)
        self.__advance()
        if self.__tokenizer.keyword() == TYPES_DIC["ELSE"]:
            self.__advance(n=2)
            self.compile_statements()
            self.__advance()
        self.__vmwriter.write_label(end_label)

    def compile_while(self):
        """
        Compiles a while statement.
        """
        start_label = "WHILE_" + str(self.__while_count)
        end_label = "WHILE_END_" + str(self.__while_count)
        self.__while_count += 1
        self.__advance(n=2)  # Advance after the '(' token
        self.__vmwriter.write_label(start_label)
        self.compile_expression()
        self.__advance(n=2)  # Advance after the '{' token
        self.__vmwriter.write_arithmetic("not")
        self.__vmwriter.write_if(end_label)
        self.compile_statements()
        self.__advance()  # Advance after the '}' token
        self.__vmwriter.write_goto(start_label)
        self.__vmwriter.write_label(end_label)

    def compile_expression_list(self):
        """
        Compiles an expression list
        """
        if self.__tokenizer.token_type() == TYPES_DIC["SYMBOL"] and self.__tokenizer.symbol() == \
                ")":
            return 0
        exp_count = 0
        self.compile_expression()
        exp_count += 1
        while self.__tokenizer.symbol() != ")":
            self.__advance()  # Skip the ',' token
            self.compile_expression()
            exp_count += 1
        return exp_count

    def __compile_subroutine_call(self):
        """
        Compile a subroutine call.
        """
        num_of_expressions = 0
        if self.__tokenizer.peek() == "(":
            if self.__tokenizer.identifier() in self.__method_list:  # if it's a method call
                num_of_expressions += 1
                self.__vmwriter.write_push("pointer", 0)  # push this as argument 0
            name = self.__class_name + "." + self.__tokenizer.identifier()
        else:
            in_method = False
            if self.__subroutine_symbols.contains(self.__tokenizer.identifier()):
                name = self.__subroutine_symbols.type_of(self.__tokenizer.identifier())
                kind = self.__subroutine_symbols.kind_of(self.__tokenizer.identifier())
                index = self.__subroutine_symbols.index_of(self.__tokenizer.identifier())
                in_method = True
            elif self.__class_symbols.contains(self.__tokenizer.identifier()):
                name = self.__class_symbols.type_of(self.__tokenizer.identifier())
                kind = self.__class_symbols.kind_of(self.__tokenizer.identifier())
                index = self.__class_symbols.index_of(self.__tokenizer.identifier())
                in_method = True
            else:
                name = self.__tokenizer.identifier()
                kind = None  # we'll never use this
                index = 0  # we'll never use this
            self.__advance(n=2)
            if in_method:  # if it's a method call
                num_of_expressions += 1
                self.__vmwriter.write_push(kind, index)
            name += "." + self.__tokenizer.identifier()
        self.__advance(n=2)
        num_of_expressions += self.compile_expression_list()
        self.__vmwriter.write_call(name, num_of_expressions)
        self.__advance()

    def compile_do(self):
        """
        Compiles a do statement.
        """
        self.__advance()
        self.__compile_subroutine_call()
        self.__vmwriter.write_pop("temp", 0)
        self.__advance()

    def compile_return(self):
        """
        Compiles a return statement.
        """
        self.__advance()
        if self.__tokenizer.token_type() == TYPES_DIC["SYMBOL"] and self.__tokenizer.symbol() == \
                ";":
            self.__vmwriter.write_push("constant", 0)
        else:
            self.compile_expression()
        self.__vmwriter.write_return()
        self.__advance()

    def compile_statements(self):
        """
        Compiles a sequence of statements , not including the
        enclosing "{}".
        """
        while self.__tokenizer.token_type() == TYPES_DIC["KEYWORD"]:
            if self.__tokenizer.keyword() == TYPES_DIC["LET"]:
                self.compile_let()
            elif self.__tokenizer.keyword() == TYPES_DIC["DO"]:
                self.compile_do()
            elif self.__tokenizer.keyword() == TYPES_DIC["WHILE"]:
                self.compile_while()
            elif self.__tokenizer.keyword() == TYPES_DIC["RETURN"]:
                self.compile_return()
            elif self.__tokenizer.keyword() == TYPES_DIC["IF"]:
                self.compile_if()

    def __compile_subroutine_parameters(self):
        """
        Compiles the subroutine's parameters.
        """
        while self.__tokenizer.keyword() == TYPES_DIC["VAR"]:
            self.compile_var_dec()

    def __compile_subroutine_body(self):
        """
        Compiles the subroutine's body.
        """
        self.compile_statements()

    def compile_subroutine_dec(self):
        """
        Compiles a subroutine declaration.
        """
        in_constructor = False
        in_method = False
        if self.__tokenizer.keyword() == TYPES_DIC["CONSTRUCTOR"]:
            in_constructor = True
        if self.__tokenizer.keyword() == TYPES_DIC["METHOD"]:
            in_method = True
        self.__advance()
        self.__subroutine_symbols.start_subroutine()
        name = self.__class_name
        self.__advance()
        name += "." + self.__tokenizer.identifier()
        self.__advance(n=2)
        if in_method:
            self.__subroutine_symbols.define("this", self.__class_name, "argument")
        self.compile_parameter_list()
        self.__advance(n=2)
        self.__compile_subroutine_parameters()
        self.__vmwriter.write_function(name,
                                       self.__subroutine_symbols.var_count("VAR"))

        if in_constructor:
            self.__vmwriter.write_push("constant", self.__class_symbols.var_count("FIELD"))
            self.__vmwriter.write_call("Memory.alloc", 1)
            self.__vmwriter.write_pop("pointer", 0)
        if in_method:
            self.__vmwriter.write_push("argument", 0)
            self.__vmwriter.write_pop("pointer", 0)
        self.__compile_subroutine_body()
        self.__advance()  # Advance the '}' token

    def compile_class(self):
        """
        Compiles a class.
        """
        self.__find_methods()
        if not self.__advance():
            return
        self.__advance()
        self.__class_name = self.__tokenizer.identifier()
        self.__advance(n=2)
        self.__vmwriter = VMWriter(self.__output)
        while self.__tokenizer.has_more_tokens() and self.__tokenizer.token_type() == TYPES_DIC[
                                                                                        "KEYWORD"]:
            if self.__tokenizer.keyword() == TYPES_DIC["STATIC"] or self.__tokenizer.keyword() ==\
                    TYPES_DIC["FIELD"]:
                self.compile_class_var_dec()
            else:
                self.compile_subroutine_dec()
        self.__vmwriter.close()
