#!/usr/bin/env python

import sys

from argparse import ArgumentParser
from distutils.ccompiler import new_compiler, CCompiler
from tempfile import NamedTemporaryFile
from subprocess import Popen
from compile import Compiler
from gentac import TacGenerator
from genc import CCodeGenerator


ccompiler = new_compiler()


parser = ArgumentParser()
parser.add_argument("source_file")
parser.add_argument("-o", metavar="executable", default="a.out", help="The path to an executable to be generated")


if __name__ == "__main__":
    args = parser.parse_args()
    executable = args.o

    with open(args.source_file, "r") as f:
        c = Compiler()
        ah_src = f.read()
        c.compile(ah_src)
        c.optimize2()

        with NamedTemporaryFile("w", suffix=".c") as tempf:
            asm_str = c.write_asm()
            ir_list = TacGenerator().generate(asm_str)
            ccode = CCodeGenerator().generate(ir_list)
            tempf.write(ccode)
            tempf.flush()
            ccompiler.link(CCompiler.EXECUTABLE, [tempf.name], executable, extra_postargs=["-O3"])
