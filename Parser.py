import os
import sys

class Parser:
    """
    Parses a single .vm file. Reads a VM command, parses it into its
    components, and provides access to these components. Ignores white
    space (blank lines) and comments.
    """

    def __init__(self, infile: str) -> None:
        """
        Process command line arguments, process the input filename,
        open and read it, construct the output filename.
        """

        # initialize instance variables
        self.currentCmd = ''    # the current instruction being processed
        self.lines = []         # list of lines in the input file
        self.nLines = 0         # number of lines in the input file
        self.currentLine = 0    # the number of the current line being processed
        self.arithmeticCommands = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
        self.memorySegments = ['argument', 'local', 'static', 'constant', 'this', 'that', 'pointer', 'temp']
        self.filename = ''      # just the input filename (no dir, no ext) for CodeWriter static variables

        # read the input file into a list
        try:
            with open(infile, 'r') as f:
                self.lines = f.readlines()
        except Exception as e:
            print(f'Error reading {infile}: {str(e)}', file=sys.stderr)
            sys.exit(4)
        self.nLines = len(self.lines)

        # get just the filename without directory or extension
        inDir, inFilename = os.path.split(infile)
        self.filename, ext = inFilename.rsplit(sep='.', maxsplit=1)

    def __del__(self) -> None:
        print('Parser destructed.', file=sys.stderr)

    def hasMoreLines(self) -> bool:
        """Are there more commands in the input?"""
        return self.currentLine < self.nLines

    def advance(self) -> None:
        """
        Reads the next line from the input and makes it the current
        command. Should be called only if hasMoreLines() is true.
        Initially there is no current command.
        """
        self.currentCmd = self.lines[self.currentLine].rstrip()
        self.currentLine += 1

    def commandType(self) -> str:
        """Returns the type of the current command."""
        # remove any trailing comment
        cmd = self.currentCmd.split('//')[0].strip()
        if len(cmd) == 0:
            return 'C_COMMENT'
        else:
            self.cmdParts = cmd.split()
            if len(self.cmdParts) == 1:
                if self.cmdParts[0] in self.arithmeticCommands:
                    return 'C_ARITHMETIC'
                if self.cmdParts[0] == 'return':
                    return 'C_RETURN'
                else:
                    print(f'Invalid command on line {self.currentLine}:\n{self.currentCmd}')
                    return 'C_ERROR'
            elif len(self.cmdParts) == 2:
                if self.cmdParts[0] == 'label':
                    return 'C_LABEL'
                elif self.cmdParts[0] == 'goto':
                    return 'C_GOTO'
                elif self.cmdParts[0] == 'if-goto':
                    return 'C_IF'
                else:
                    print(f'Invalid command on line {self.currentLine}:\n{self.currentCmd}')
                    return 'C_ERROR'
            elif len(self.cmdParts) == 3:
                # error checking for push and pop
                if self.cmdParts[0] == 'push' or self.cmdParts[0] == 'pop':
                    if not self.cmdParts[2].isnumeric():
                        print(f'Index not numeric on line {self.currentLine}:\n{self.currentCmd}')
                        return 'C_ERROR'
                    if self.cmdParts[1] not in self.memorySegments:
                        print(f'Invalid memory segment on line {self.currentLine}:\n{self.currentCmd}')
                        return 'C_ERROR'
                if self.cmdParts[0] == 'push':
                    return 'C_PUSH'
                elif self.cmdParts[0] == 'pop':
                    return 'C_POP'
                elif self.cmdParts[0] == 'function':
                    return 'C_FUNCTION'
                elif self.cmdParts[0] == 'call':
                    return 'C_CALL'
                else:
                    print(f'Invalid command on line {self.currentLine}:\n{self.currentCmd}')
                    return 'C_ERROR'

    def arg0(self) -> str:
        """
        Returns the first field from the current command, which is
        the name of the command.
        """
        return self.cmdParts[0]

    def arg1(self) -> str:
        """
        Returns the second field from the current command, which is
        the segment name. Should be called for push/pop commands only.
        """
        return self.cmdParts[1]

    def arg2(self) -> str:
        """
        Returns the third field from the current command, which is
        the segment index. Should be called for push/pop commands only.
        """
        return self.cmdParts[2]
