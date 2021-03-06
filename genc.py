import gentac 
import os

from gentac import TAC_OP, BASE_STACK_MAGIC



DIR_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = open(os.path.join(DIR_PATH, "maintem.c"), "r").read()


BINOP_OP_TBL = {
    TAC_OP.ADD: "+", 
    TAC_OP.SUB: "-",
    TAC_OP.MUL: "*",
    TAC_OP.DIV: "/",
    TAC_OP.MOD: "%",
    TAC_OP.GTE: ">="
}

class CCodeGenerator(object):
    def _convert_binop(self, tac):
        return "".join([self._lvalue(tac.dest),
                        self._rvalue(tac.src1),
                        BINOP_OP_TBL[tac.op],
                        self._rvalue(tac.src2)])
            



    def _lvalue(self, temp):
        return "cell_t %s = "%temp.name

    def _rvalue(self, temp):
        return temp.name

    # generate one expression
    def convert_tac(self, tac):

        if tac.op in BINOP_OP_TBL:
            return self._convert_binop(tac)
        elif tac.op == TAC_OP.ASSIGN:
            return self._lvalue(tac.dest) + self._rvalue(tac.src1);
        elif tac.op == TAC_OP.ASSIGN_VAL:
            return self._lvalue(tac.dest) + str(tac.imm)
        elif tac.op == TAC_OP.ASSIGN_CHAR:
            return self._lvalue(tac.dest) + "_getchar()";
        elif tac.op == TAC_OP.ASSIGN_NUM:
            return self._lvalue(tac.dest) + "_getnum()";
        elif tac.op == TAC_OP.PRINT_NUM:
            return "_printnum(%s)"%self._rvalue(tac.src1);
        elif tac.op == TAC_OP.PRINT_CHAR:
            return "_printchar(%s)"%self._rvalue(tac.src1);
        elif tac.op == TAC_OP.PUSH:
            if tac.stackno is None:
                return "_push(%s)"%self._rvalue(tac.src1);
            elif tac.stackno == BASE_STACK_MAGIC:
                return "_push_base_stack(%s)"%self._rvalue(tac.src1);
            else:
                return "_push_stack_no(%d, %s)"%(tac.stackno, self._rvalue(tac.src1))
        elif tac.op == TAC_OP.STACK_SEL:
            return "_stack_sel(%d)"%tac.stackno
        elif tac.op == TAC_OP.SET_BASE_STACK:
            return "_set_base_stack()"
        elif tac.op in [TAC_OP.POP, TAC_OP.PEEK]:
            def inner(sym):
                if tac.stackno is None:
                    return "_%s()"%sym
                elif tac.stackno == BASE_STACK_MAGIC:
                    return "_%s_base_stack()"%sym
                else:
                    return "_%s_stack_no(%d)"%(sym, tac.stackno)
            s = inner("pop" if tac.op == TAC_OP.POP else "peek" )
            if tac.dest is not None:
                s = self._lvalue(tac.dest) + s
            return s
        elif tac.op == TAC_OP.ENQUEUE:
            return "_enqueue(%s)"%self._rvalue(tac.src1)
        elif tac.op == TAC_OP.DEQUEUE:
            return self._lvalue(tac.dest) + "_dequeue()"
        elif tac.op == TAC_OP.PEEKQUEUE:
            return self._lvalue(tac.dest) + "_peekqueue()"
        elif tac.op == TAC_OP.ENTERQUEUEMODE:
            return "_enterqueuemode()"
        elif tac.op == TAC_OP.LEAVEQUEUEMODE:
            return "_leavequeuemode()"
        elif tac.op == TAC_OP.DUP:
            return "_dup()"
        elif tac.op == TAC_OP.DUPQUEUE:
            return "_dupqueue()"
        elif tac.op == TAC_OP.JMP:
            return "goto %s"%tac.loc.name;
        elif tac.op == TAC_OP.POPANDJZ:
            template = "if (!(%s) || ((%s) == 0)) goto %s;"
            if tac.imm != 0:
                return template%("_queue_len() > 0", 
                                 "_dequeue()",
                                 tac.loc.name)
            elif tac.stackno is None:
                return template%("_storage_len() > 0",
                                 "_pop()",
                                 tac.loc.name)
            elif tac.stackno == BASE_STACK_MAGIC:
                return template%("_base_stack_len() > 0",
                                 "_pop_base_stack()",
                                 tac.loc.name)
            else:
                return template%("_stack_no_len(%d) > 0"%tac.stackno, 
                                 "_pop_stack_no(%d)"%tac.stackno,
                                 tac.loc.name)
        elif tac.op == TAC_OP.JSS:
            assert (tac.stackno is not None)
            if tac.stackno == BASE_STACK_MAGIC:
                return "if(_base_stack_len() < %d) goto %s"%(tac.imm, tac.loc.name)
            else:
                return "if(_stack_no_len(%d) < %d) goto %s"%(tac.stackno, tac.imm, tac.loc.name)
        elif tac.op == TAC_OP.JQS:
            return "if(_queue_len() < %d) goto %s"%(tac.imm, tac.loc.name)
        elif tac.op == TAC_OP.JSTORAGE:
            return "if(_storage_len() < %d) goto %s"%(tac.imm, tac.loc.name)
        elif tac.op == TAC_OP.HALT:
            return "return"
        else:
            raise Exception("NOT REACHABLE: %s"%tac.op)

    def convert_loc(self, loc):
        return loc.name + ":"
    def convert_comment(self, cmt):
        return "// TACgen: " + cmt.comment


    def convert_irs(self, irs):
        slist = []
        for ir in irs:
            if isinstance(ir, gentac.IRLoc):
                slist.append(self.convert_loc(ir))
            elif isinstance(ir, gentac.IRComment):
                slist.append(self.convert_comment(ir))
            elif isinstance(ir, gentac.IRTac):
                slist.append(self.convert_tac(ir))
            else:
                raise Exception("NOT REACHABLE")
            slist.append(";\n")
        return "".join(slist)

    def generate(self, irs):
        return TEMPLATE.replace("//{_CC_MAIN}", self.convert_irs(irs))


