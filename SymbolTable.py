class SymbolTable:

    def __init__(self):
        self.__table = {}
        self.__arg_count = 0
        self.__lcl_count = 0
        self.__static_count = 0
        self.__this_count = 0

    def start_subroutine(self):
        """
        Reset the table and counters.
        """
        self.__table = {}
        self.__arg_count = 0
        self.__lcl_count = 0
        self.__static_count = 0
        self.__this_count = 0

    def define(self, name, type, kind):
        """
        Add a new variable to the table
        :param name: Variable's name
        :param type: The variable's type
        :param kind: The variable's identifier/scope
        """
        if kind == "static":
            self.__table[name] = (type, "static", self.__static_count)
            self.__static_count += 1
        elif kind == "field":
            self.__table[name] = (type, "this", self.__this_count)
            self.__this_count += 1
        elif kind == "argument":
            self.__table[name] = (type, "argument", self.__arg_count)
            self.__arg_count += 1
        else:
            self.__table[name] = (type, "local", self.__lcl_count)
            self.__lcl_count += 1

    def var_count(self, kind):
        """
        Count's how many variables of the given kind exist in the table
        :param kind: The kind to count
        :return: The number of variables
        """
        if kind == "STATIC":
            return self.__static_count
        elif kind == "FIELD":
            return self.__this_count
        elif kind == "ARG":
            return self.__arg_count
        else:
            return self.__lcl_count

    def kind_of(self, name):
        """
        :param name: The name of the Variable
        :return: The variable's kind
        """
        return self.__table[name][1]

    def type_of(self, name):
        """
        :param name: The name of the Variable
        :return: The variable's type
        """
        return self.__table[name][0]

    def index_of(self, name):
        """
        :param name: The name of the Variable
        :return: The variable's index
        """
        return self.__table[name][2]

    def contains(self, name):
        return name in self.__table
