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


class CmdlineOption(object):
    pass


parser = ArgumentParser()
parser.add_argument("source_file")
parser.add_argument("-o", metavar="", help="The path to an executable to be generated")
parser.add_argument("--type", choices=["ahssembly", "ir", "immediate"], help="Generate an ahssembly, IR, or immediate code instead of an executable")
parser.add_argument("--unsafestack", 
                    action="store_true",  
                    help="Force program not to check the stacks and the queue at runtime. "
                         "It'll get rid of burden for checking overflows or underflows for each push or pop operation,"
                         " but it may lead unexpected behavior if overflow or underflow take place")


if __name__ == "__main__":
    option = CmdlineOption()
    args = parser.parse_args()

    option.source_file = args.source_file
    option.dest = args.o
    option.type = args.type
    option.unsafestack = args.unsafestack

    asm_str = None
    with open(option.source_file, "r") as f:
        c = Compiler()
        ah_src = f.read()
        c.compile(ah_src)
        c.optimize2()
        asm_str = c.write_asm()

    if option.type == "ahssembly":
        with open(option.dest or "a.out.ahs", "w") as ahs_f:
            ahs_f.write(asm_str)
    else: 
        ir_list = TacGenerator().generate(asm_str)
        if option.type == "ir":
            with open(option.dest or "a.out.ir", "w") as ir_f:
                for ir in ir_list:
                    ir_f.write(repr(ir))
                    ir_f.write("\n")
        else:
            ccode = CCodeGenerator().generate(ir_list)
            if option.type == "immediate":
                with open(option.dest or "a.out.c", "w") as imd_f:
                    imd_f.write(ccode)
            else:
                with NamedTemporaryFile("w", suffix=".c") as tempf:
                    tempf.write(ccode)
                    tempf.flush()

                    macros = []
                    # safe stack option
                    if not option.unsafestack:
                        macros.append(("CHECK_STACK", None))
                    objpath = ccompiler.compile([tempf.name], macros=macros, extra_postargs=["-O3"])[0]
                    ccompiler.link(CCompiler.EXECUTABLE, [objpath], option.dest or "a.out")
