#!/usr/bin/python3
# J.Christensen 03Sep2022
# Hack Virtual Machine Translator.

import Parser
import CodeWriter
import argparse
import os
import sys

def main() -> None:
    """
    VM Translator by Jack Christensen Sep-2022.
    Project 08 from "The Elements of Computing Systems"
    by Nisan and Schocken, MIT Press. Also www.nand2tetris.org
    """

    # process command line arguments
    argParser = argparse.ArgumentParser(
        description='A VM Translator for the Hack computer.',
        epilog='VM Translator by Jack Christensen. Project 08 from "The Elements of Computing Systems" by Nisan and Schocken, MIT Press. Also www.nand2tetris.org')
    argParser.add_argument('source', help='Input file or directory')
    args = argParser.parse_args()

    fileList = []
    if os.path.isfile(args.source):
        # source is a file, process the input filename
        inDir, inFilename = os.path.split(args.source)
        try:
            filename, ext = inFilename.rsplit(sep='.', maxsplit=1)
        except Exception as e:
            print('Error: Input file must have .vm extension.', file=sys.stderr)
            sys.exit(1)
        if ext != 'vm':
            print('Error: Input file must have .vm extension.', file=sys.stderr)
            sys.exit(2)
        if not filename[0].isupper():
            print('Error: Input file must start with an upper-case letter.', file=sys.stderr)
            sys.exit(3)
        fileList.append(args.source)
        # output filename is same as input filename
        outFilename = filename + '.asm'
        if inDir:
            outFilename = inDir + os.sep + outFilename
    elif os.path.isdir(args.source):
        # source is a directory, build a list of .vm files to process
        dirName = args.source
        # if directory name was entered with trailing slash, remove it to prevent double slash
        if dirName[-1] == os.sep:
            dirName = dirName[:-1]
        d = os.scandir(dirName)
        for e in d:
            if e.is_file() and e.name[-3:] == '.vm':
                fileList.append(dirName + os.sep + e.name)
        # output filename is same as input directory name
        outFilename = dirName + os.sep + os.path.basename(dirName) + '.asm'
    else:
        print(f'Source is invalid: {args.source}', file=sys.stderr)
        sys.exit(4)

    if not fileList:
        print(f'ERROR: No VM source files (*.vm) found in directory {dirName}', file=sys.stderr)
        sys.exit(5)

    writer = CodeWriter.CodeWriter()

    for file in fileList:
        writer.setFilename(file)
        parser = Parser.Parser(file)
        while parser.hasMoreLines():
            parser.advance()
            #print(parser.commandType(), parser.currentCmd)
            if parser.commandType() == 'C_ERROR':
                print('Translation terminated.')
                sys.exit(5)
            elif parser.commandType() == 'C_COMMENT':
                writer.writeComment(parser.currentCmd)
            elif parser.commandType() == 'C_PUSH' or parser.commandType() == 'C_POP':
                writer.writePushPop(parser.currentCmd, parser.arg0(), parser.arg1(), parser.arg2())
            elif parser.commandType() == 'C_ARITHMETIC':
                writer.writeArithmetic(parser.currentCmd, parser.arg0())
            elif parser.commandType() == 'C_LABEL':
                writer.writeLabel(parser.currentCmd, parser.arg1())
            elif parser.commandType() == 'C_GOTO':
                writer.writeGoto(parser.currentCmd, parser.arg1())
            elif parser.commandType() == 'C_IF':
                writer.writeIf(parser.currentCmd, parser.arg1())
            elif parser.commandType() == 'C_FUNCTION':
                writer.writeFunction(parser.currentCmd, parser.arg0(), parser.arg1())
            elif parser.commandType() == 'C_RETURN':
                writer.writeReturn(parser.currentCmd)
            elif parser.commandType() == 'C_CALL':
                writer.writeCall(parser.currentCmd, parser.arg0(), parser.arg1())
            else:
                print('Translation terminated.')
                sys.exit(6)

    # all done
    writer.close(outFilename)
    print(f'** VM TRANSLATOR COMPLETE **', file=sys.stderr)

if __name__ == '__main__':
    main()
