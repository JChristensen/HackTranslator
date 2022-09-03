class CodeWriter:
    """
    Translates a parsed VM command into Hack assembly code.
    """

    def __init__(self, progname: str) -> None:
        """Creates an empty list to hold the VM commands."""
        self.code = []              # lines of code are added to this list, written to output file later
        self.words = 0              # address of the next instruction to write
        self.segDict = {'local':'LCL', 'argument':'ARG', 'this':'THIS', 'that':'THAT'}
        self.progname = progname    # for static variable names

    def writeArithmetic(self, line: str, op: str) -> None:
        """
        Appends the code for the given arithmetic or logical command
        to the VM code list.
        """
        self.writeComment(f'// [{self.words}] {line}')
        if op == 'add':
            self.instruction( '  @SP')
            self.instruction( '  M=M-1')
            self.instruction( '  A=M')
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  M=M+D')    # M = x + y
        elif op == 'sub':
            self.instruction( '  @SP')
            self.instruction( '  M=M-1')
            self.instruction( '  A=M')
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  M=M-D')    # M = x - y
        elif op == 'neg':
            self.instruction( '  @SP')
            self.instruction( '  A=M')
            self.instruction( '  A=A-1')
            self.instruction( '  M=-M')
        if op == 'and':
            self.instruction( '  @SP')
            self.instruction( '  M=M-1')
            self.instruction( '  A=M')
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  M=M&D')    # M = x & y
        elif op == 'or':
            self.instruction( '  @SP')
            self.instruction( '  M=M-1')
            self.instruction( '  A=M')
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  M=M|D')    # M = x | y
        elif op == 'not':
            self.instruction( '  @SP')
            self.instruction( '  A=M')
            self.instruction( '  A=A-1')
            self.instruction( '  M=!M')
        elif op == 'eq':
            self.instruction( '  @SP')      # A = SP ptr
            self.instruction( '  M=M-1')    # SP--
            self.instruction( '  A=M')      # A = SP
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  D=M-D')    # result in D
            self.instruction(f'  @{self.words+7}')
            self.instruction( '  D;JEQ')    # jump if D is zero, i.e. x==y
            self.instruction( '  @SP')      # x<>y so put false (0) on the stack
            self.instruction( '  A=M-1')
            self.instruction( '  M=0')
            self.instruction(f'  @{self.words+5}')
            self.instruction( '  0;JMP')
            self.instruction( '  @SP')      # x==y so put true (-1) on the stack
            self.instruction( '  A=M-1')
            self.instruction( '  M=-1')
        elif op == 'lt':                    # x < y
            self.instruction( '  @SP')      # A = SP ptr
            self.instruction( '  M=M-1')    # SP--
            self.instruction( '  A=M')      # A = SP
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  D=M-D')    # result in D
            self.instruction(f'  @{self.words+7}')
            self.instruction( '  D;JLT')    # jump if D < zero, i.e. x<y
            self.instruction( '  @SP')      # x>=y so put false (0) on the stack
            self.instruction( '  A=M-1')
            self.instruction( '  M=0')
            self.instruction(f'  @{self.words+5}')
            self.instruction( '  0;JMP')
            self.instruction( '  @SP')      # x<y so put true (-1) on the stack
            self.instruction( '  A=M-1')
            self.instruction( '  M=-1')
        elif op == 'gt':                    # x > y
            self.instruction( '  @SP')      # A = SP ptr
            self.instruction( '  M=M-1')    # SP--
            self.instruction( '  A=M')      # A = SP
            self.instruction( '  D=M')      # D = y
            self.instruction( '  A=A-1')    # M = x
            self.instruction( '  D=M-D')    # result in D
            self.instruction(f'  @{self.words+7}')
            self.instruction( '  D;JGT')    # jump if D > zero, i.e. x>y
            self.instruction( '  @SP')      # x<=y so put false (0) on the stack
            self.instruction( '  A=M-1')
            self.instruction( '  M=0')
            self.instruction(f'  @{self.words+5}')
            self.instruction( '  0;JMP')
            self.instruction( '  @SP')      # x>y so put true (-1) on the stack
            self.instruction( '  A=M-1')
            self.instruction( '  M=-1')

    def writePushPop(self, line: str, op: str, segment: str, index: str) -> None:
        """Appends the code for a push or pop command to the VM code list."""
        self.writeComment(f'// [{self.words}] {line}')
        if op == 'push':
            if segment == 'constant':
                self.instruction(f'  @{index}')     # get value to push in D
                self.instruction( '  D=A')
                self.pushD()
            elif segment in self.segDict:
                self.instruction(f'  @{index}')     # get value to push in D
                self.instruction( '  D=A')
                self.instruction(f'  @{self.segDict[segment]}')
                self.instruction( '  A=M')
                self.instruction( '  A=D+A')
                self.instruction( '  D=M')
                self.pushD()
            elif segment == 'temp':
                self.instruction(f'  @{index}')     # get value to push in D
                self.instruction( '  D=A')
                self.instruction( '  @5')           # TEMP is RAM[5-12]
                self.instruction( '  A=D+A')
                self.instruction( '  D=M')
                self.pushD()
            elif segment == 'pointer':
                self.instruction(f'  @{index}')     # get value to push in D
                self.instruction( '  D=A')
                self.instruction( '  @3')           # POINTER is RAM[3-4]
                self.instruction( '  A=D+A')
                self.instruction( '  D=M')
                self.pushD()
            elif segment == 'static':
                self.instruction(f'  @{self.progname}.{index}') # addr of static variable
                self.instruction( '  D=M')
                self.pushD()
        elif op == 'pop':
            if segment in self.segDict:
                self.instruction(f'  @{index}')     # A = seg idx
                self.instruction( '  D=A')          # D = seg idx
                self.instruction(f'  @{self.segDict[segment]}') # A = seg base ptr
                self.instruction( '  A=M')          # A = seg base addr
                self.instruction( '  D=D+A')        # D = indexed seg addr
                self.instruction( '  @R15')
                self.instruction( '  M=D')          # save in R15
                self.pop15()
            elif segment == 'temp':
                self.instruction(f'  @{index}')     # A = seg idx
                self.instruction( '  D=A')          # D = seg idx
                self.instruction( '  @5')           # TEMP is RAM[5-12]
                self.instruction( '  D=D+A')        # indexed address
                self.instruction( '  @R15')
                self.instruction( '  M=D')          # save in R15
                self.pop15()
            elif segment == 'pointer':
                self.instruction(f'  @{index}')     # A = seg idx
                self.instruction( '  D=A')          # D = seg idx
                self.instruction( '  @3')           # POINTER is RAM[3-4]
                self.instruction( '  D=D+A')        # indexed address
                self.instruction( '  @R15')
                self.instruction( '  M=D')          # save in R15
                self.pop15()
            elif segment == 'static':
                self.instruction(f'  @{self.progname}.{index}') # addr of static variable
                self.instruction( '  D=A')
                self.instruction( '  @R15')
                self.instruction( '  M=D')          # save in R15
                self.pop15()

    def instruction(self, inst: str) -> None:
        """Writes a single instruction and increments the word count."""
        self.code.append(inst + '\n')
        self.words += 1

    def pushD(self) -> None:
        """Pushes the contents of D onto the stack."""
        self.instruction('  @SP')       # A = SP address
        self.instruction('  A=M')       # A = SP value
        self.instruction('  M=D')       # store D in *SP
        self.instruction('  @SP')       # A = SP address
        self.instruction('  M=M+1')     # increment SP

    def pop15(self) -> None:
        """Pops the top value from the stack and stores it at the address contained in R15."""
        self.instruction('  @SP')       # A = addr of SP
        self.instruction('  M=M-1')     # decrement SP
        self.instruction('  A=M')       # A = SP
        self.instruction('  D=M')       # D = top item from stack
        self.instruction('  @R15')
        self.instruction('  A=M')       # A = saved addr
        self.instruction('  M=D')       # store value from stack

    def writeComment(self, line: str) -> None:
        """
        Appends the input line as is to the VM code list.
        Use for comments, blank lines.
        """
        self.code.append(line + '\n')

    def close(self, outFilename: str) -> None:
        """
        Adds an infinite loop to the end of the output file to
        stop execution, and closes the file.
        """
        self.code.append(f'// [{self.words}] Infinite loop\n')
        self.code.append('(__FINIS__)\n')
        self.code.append('  @__FINIS__\n')
        self.code.append('  0;JMP\n')

        with open(outFilename, 'w') as f:
            f.writelines(self.code)
