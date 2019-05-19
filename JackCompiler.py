import os
import sys
import platform
from CompilationEngine import CompilationEngine
WIN_PATH_DEL = "\\"  # Delimiter in Windows based directory path
OTHER_PATH_DEL = "/"  # Delimiter in other OS's directory path
VM_SUFFIX = ".vm"
JACK_SUFFIX = ".jack"
SUFFIX_DELIMITER = "."

if __name__ == '__main__':
    if os.path.isdir(sys.argv[1]):
        for file_name in os.listdir(sys.argv[1]):
            if file_name.endswith(JACK_SUFFIX):
                if platform.system() == "Windows":
                    name = sys.argv[1] + WIN_PATH_DEL + file_name
                    name = name.rsplit(SUFFIX_DELIMITER, 1)[0]
                    output = name + VM_SUFFIX
                    engine = CompilationEngine(sys.argv[1] +
                                               WIN_PATH_DEL + file_name,
                                               output)
                    engine.compile_class()
                else:
                    name = sys.argv[1] + OTHER_PATH_DEL + file_name
                    name = name.rsplit(SUFFIX_DELIMITER, 1)[0]
                    output = name + VM_SUFFIX
                    engine = CompilationEngine(sys.argv[1] +
                                               OTHER_PATH_DEL +
                                               file_name, output)
                    engine.compile_class()
    else:
        if platform.system() == "Windows":
            name = sys.argv[1].rsplit(SUFFIX_DELIMITER, 1)[0]
            output = name + VM_SUFFIX
            engine = CompilationEngine(sys.argv[1], output)
            engine.compile_class()
        else:
            name = sys.argv[1].rsplit(SUFFIX_DELIMITER, 1)[0]
            output = name + VM_SUFFIX
            engine = CompilationEngine(sys.argv[1], output)
            engine.compile_class()
