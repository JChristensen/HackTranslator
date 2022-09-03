#!/usr/bin/python3
# J.Christensen 03Sep2022
# Hack Virtual Machine Translator.

import Parser
import CodeWriter
import sys

def main() -> None:
    """
    VM Translator by Jack Christensen Sep-2022.
    Project 08 from "The Elements of Computing Systems"
    by Nisan and Schocken, MIT Press. Also www.nand2tetris.org
    """

    parser = Parser.Parser()
    writer = CodeWriter.CodeWriter(parser.filename)

    while parser.hasMoreLines():
        parser.advance()
        #print(parser.commandType(), parser.currentCmd)
        if parser.commandType() == 'ERROR':
            print('Translation terminated.')
            sys.exit(5)
        elif parser.commandType() == 'COMMENT':
            writer.writeComment(parser.currentCmd)
        elif parser.commandType() == 'C_PUSH' or parser.commandType() == 'C_POP':
            writer.writePushPop(parser.currentCmd, parser.arg0(), parser.arg1(), parser.arg2())
        elif parser.commandType() == 'C_ARITHMETIC':
            writer.writeArithmetic(parser.currentCmd, parser.arg0())
        else:
            print('Translation terminated.')
            sys.exit(6)

    # all done
    writer.close(parser.outFilename)
    print(f'**** VM TRANSLATOR COMPLETE ****', file=sys.stderr)

if __name__ == '__main__':
    main()