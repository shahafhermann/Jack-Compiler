class VMWriter:

    def __init__(self, output):
        self.__out = open(output, "w+")

    def write_push(self, segment, index):
        """
        Write a push command
        :param segment: The segment to write to
        :param index: The index to write to
        """
        self.__out.write("push " + segment + " " + str(index) + "\n")

    def write_pop(self, segment, index):
        """
        Write a pop command
        :param segment: The segment to write to
        :param index: The index to write to
        """
        self.__out.write("pop " + segment + " " + str(index) + "\n")

    def write_arithmetic(self, command):
        """
        Writes an arithmetic command
        :param command: The command to write
        """
        self.__out.write(command + "\n")

    def write_label(self, string):
        """
        Writes a label command
        :param string: The label's name
        """
        self.__out.write("label " + string + "\n")

    def write_goto(self, string):
        """
        Writes a goto statement
        :param string: The label to go to
        """
        self.__out.write("goto " + string + "\n")

    def write_if(self, string):
        """
        Writes an if-goto statement
        :param string: The label to go to
        """
        self.__out.write("if-goto " + string + "\n")

    def write_call(self, name, n_args):
        """
        Writes a function call command
        :param name: Function's name
        :param n_args: Number of arguments to call with
        """
        self.__out.write("call " + name + " " + str(n_args) + "\n")

    def write_function(self, name, n_locals):
        """
        Writes a function statement
        :param name: The function's name
        :param n_locals: The number of parameters
        """
        self.__out.write("function " + name + " " + str(n_locals) + "\n")

    def write_return(self):
        """
        Writes a return statement
        """
        self.__out.write("return\n")

    def close(self):
        """
        Close the output file
        """
        self.__out.close()
