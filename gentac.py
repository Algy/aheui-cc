# -*- coding: utf-8 -*-
from pprint import pprint 
class TAC_OP:
    # stackno: int or 
    #          BASE_STACK_MAGIC or 
    #          HEAD_STACK_MAGIC(internal use. it doesn't appear after TAC generated)
    # loc: IRLoc or None
    # imm: int
    # dest: TacTemp or None
    # src1: TacTemp
    # src2: TacTemp
    # dest = src1 OP src2
    ADD = "add"
    SUB = "sub"
    MUL = "mul"
    DIV = "div"
    MOD = "mod"
    GTE = "gte"

    # dest = src1
    ASSIGN = "assign" 
    # dest = imm
    ASSIGN_VAL = "assignval" 
    # dest = GETCHAR()
    ASSIGN_CHAR = "assignchar" 
    # dest = GETNUM()
    ASSIGN_NUM = "assignnum" 
    # print src1
    PRINT_NUM = "printnum"
    # print src1
    PRINT_CHAR = "printchar"

    # stack[stackno] += src1
    PUSH = "push"

    # cur_stackno = stackno
    STACK_SEL = "stacksel"

    # base_stackno = cur_stackno (no arguments required)
    SET_BASE_STACK = "setbasestack"

    # dest (may be None) = pop element from stack[stackno] 
    POP = "pop"
    # dest = peek from the top of stack[stackno]
    PEEK = "peek"

    # jmp loc
    JMP = "jmp"
    # jz src1, loc,
    JZ = "jz"
    # Jump if stack length is less than imm
    JSS = "jss" 
    # halt 
    HALT = "halt"


class IR(object):
    '''
    '''

class IRComment(IR):
    def __init__(self, comment):
        self.comment = comment

    def __repr__(self):
        return "; %s"%self.comment


class IRLoc(IR):
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return "<IRLoc>%s"%self.name


def repr_op_binop(tac):
    return "%s := %s %s %s"%(tac.dest.name, tac.src1.name, tac.op, tac.src2.name)

def repr_op_assign(tac):
    return "%s := %s"%(tac.dest.name, tac.src1.name)

def repr_op_assign_val(tac):
    return "%s := $%d"%(tac.dest.name, tac.imm)

def repr_op_assign_char(tac):
    return "%s := getc()"%(tac.dest.name)

def repr_op_assign_num(tac):
    return "%s := getn()"%(tac.dest.name)

def repr_op_print_num(tac):
    return "printnum %s"%(tac.src1.name)

def repr_op_print_char(tac):
    return "printchar %s"%(tac.src1.name)

def repr_op_stack_push(tac):
    if tac.stackno is not None:
        return "push[%s] <- %s"%(repr(tac.stackno), tac.src1.name)
    else:
        return "push <- %s"%(tac.src1.name)

def repr_op_stack_sel(tac):
    return "sel %s"%(repr(tac.stackno))

def repr_op_set_base_stack(tac):
    return "set basestackno"

def repr_op_stack_pop(tac):
    if tac.stackno is not None:
        s = "pop[%s]"%(repr(tac.stackno))
    else:
        s = "pop"
    if tac.dest:
        s = "%s := " % tac.dest.name + s
    return s

def repr_op_stack_peek(tac):
    if tac.stackno is not None:
        return "%s := peek[%s]"%(tac.dest.name, repr(tac.stackno))
    else:
        return "%s := peek"%(tac.dest.name)

def repr_op_jmp(tac):
    return "jmp %s"%(tac.loc.name)

def repr_op_jz(tac):
    return "jmp %s, if %s == 0"%(tac.loc.name, tac.src1.name)

def repr_op_jss(tac):
    return "jmp %s, if ss < %d"%(tac.loc.name, tac.imm)

def repr_op_halt(tac):
    return "halt"


REPR_TBL = {
    TAC_OP.ADD: repr_op_binop,
    TAC_OP.SUB: repr_op_binop,
    TAC_OP.MUL: repr_op_binop,
    TAC_OP.DIV: repr_op_binop,
    TAC_OP.MOD: repr_op_binop,
    TAC_OP.GTE: repr_op_binop,
    TAC_OP.ASSIGN: repr_op_assign,
    TAC_OP.ASSIGN_VAL: repr_op_assign_val,
    TAC_OP.ASSIGN_CHAR: repr_op_assign_char,
    TAC_OP.ASSIGN_NUM: repr_op_assign_num,
    TAC_OP.PRINT_NUM: repr_op_print_num,
    TAC_OP.PRINT_CHAR: repr_op_print_char,
    TAC_OP.PUSH: repr_op_stack_push,
    TAC_OP.STACK_SEL: repr_op_stack_sel,
    TAC_OP.SET_BASE_STACK: repr_op_set_base_stack, 
    TAC_OP.POP: repr_op_stack_pop,
    TAC_OP.PEEK: repr_op_stack_peek,
    TAC_OP.JMP: repr_op_jmp,
    TAC_OP.JZ: repr_op_jz,
    TAC_OP.JSS: repr_op_jss,
    TAC_OP.HALT: repr_op_halt
}


class IRTac(IR):
    def __init__(self, op, src1=None, src2=None, dest=None, stackno=None, loc=None, imm=None):
        self.op = op
        self.dest = dest
        self.src1 = src1
        self.src2 = src2
        self.stackno = stackno
        self.loc = loc
        self.imm = imm

    def __repr__(self):
        return REPR_TBL[self.op](self)
        



    
class TacTemp:
    '''
    should be Immutable
    '''
    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return "<TacTemp %s>"%self.name



def parse_aheui_asm(s):
    '''
    string -> AheuiAsmInstr generator
    '''
    for x in s.splitlines():
        # rip off comment
        idx = x.find(";")
        if idx >= 0:
            x = x[:idx]
        # seperate location
        idx = x.find(":")
        locname = None
        if idx >= 0:
            locname = x[:idx]
            x = x[idx+1:]
        x = x.strip()
        if not x:
            continue
        words = x.split()
        name = words[0].lower()
        arg = None
        try:
            arg = words[1]
        except IndexError:
            pass
        if locname:
            yield AheuiAsmInstr(locname, is_loc=True)
        yield AheuiAsmInstr(name, arg=arg)


class AheuiAsmInstr(object):
    def __init__(self, name, arg=None, is_loc=False):
        self.name = name
        self.arg = arg
        self.is_loc = is_loc

    def __repr__(self):
        if self.is_loc:
            return "<AheuiAsm Loc %s>"%self.name
        else:
            return "<AheuiAsm %s%s>"%(self.name, " %s"%repr(self.arg))



JMP_INSTRUCTIONS = set(["brpop1", "brpop2", "jmp", "brz"])

def make_block_graph(sym_env, asmlist):
    block_id_cnt = 0
    idx = 0
    prev_block = None
    result_blocks = []


    locname_to_block = {}
    while idx < len(asmlist):
        locname = None
        asm_loc = None
        codes = []
        trailing_jmp = None
        jmp_loc = None

        if asmlist[idx].is_loc:
            locname = asmlist[idx].name
            asm_loc = asmlist[idx]
            idx += 1
        elif asmlist[idx].name == "halt":
            codes.append(asmlist[idx])
            idx += 1


        if locname is not None:
            codes.append(asm_loc)
        loc = sym_env.defloc(locname) if locname else None


        while idx < len(asmlist):
            asm = asmlist[idx]
            if asm.is_loc:
                break
            if asm.name == "halt":
                break
            if not asm.is_loc and asm.name in JMP_INSTRUCTIONS:
                trailing_jmp = asm
                idx += 1
                break
            codes.append(asm)
            idx += 1

        jmp_loc  = sym_env.useloc(trailing_jmp.arg) if trailing_jmp else None

        block_id = block_id_cnt
        block_id_cnt += 1
        block = CodeBlock(block_id, codes, loc, trailing_jmp, jmp_loc)
        if prev_block is not None:
            prev_block.next_block = block
        prev_block = block
        result_blocks.append(block)
        if locname is not None:
            locname_to_block[locname] = block

    for block in result_blocks:
        if block.jmp_loc:
            block.jmp_block = locname_to_block[block.jmp_loc.name];
        
    if result_blocks:
        start_block = result_blocks[0]
    else:
        start_block = None
    start_block.stackno = INITIAL_STACKNO
    return BlockGraph(result_blocks, start_block, block_id_cnt)
            

class BlockGraph(object):
    def __init__(self, blocks, start_block, id_cnt):
        self.blocks = blocks
        self.start_block = start_block
        self.id_cnt = id_cnt

    def infer_possible_stacknos(self):
        pass




class CodeBlock(object):
    def __init__(self, block_id, asmlist, loc=None, trailing_jmp=None, jmp_loc=None):
        self.block_id = block_id
        self.asmlist = asmlist
        self.trailing_jmp = trailing_jmp
        self.jmp_loc = jmp_loc 
        self.jmp_block = None
        self.next_block = None
        self.loc = loc # IRLoc or None
        self.stackno = HEAD_STACK_MAGIC


    def debug_string(self):
        slist = ["<CodeBlock id=%d, trailing_jmp=%s, loc=%s, jmp_loc=%s>"%(self.block_id, repr(self.trailing_jmp), repr(self.loc), repr(self.jmp_loc))]
        slist.append("\n")
        slist.append("===\n")
        for asm in self.asmlist:
            slist.append(repr(asm))
            slist.append("\n")
        if self.jmp_block:
            slist.append(">>JUMP TO %s: %s\n"%(repr(self.jmp_block.block_id), repr(self.trailing_jmp)))
        if self.next_block:
            slist.append(">> FALL TOWORD %d\n"%(self.next_block.block_id))
        else:
            slist.append(">> NO FALLNG THRU\n")

        return "".join(slist)




def convert_halt(env, instr):
    return IRTac(TAC_OP.HALT)

OPTBL = {"add": TAC_OP.ADD,
         "sub": TAC_OP.SUB,
         "mul": TAC_OP.MUL,
         "div": TAC_OP.DIV,
         "mod": TAC_OP.MOD,
         "cmp": TAC_OP.GTE}

def convert_binop(env, instr):
    src2 = env.pop()
    src1 = env.pop() # -> TacTemp
    dest = env.newtemp()
    op = OPTBL[instr.name]
    env.add_eager_tac(IRTac(op, src1, src2, dest))
    env.push(dest)


def convert_pop(env, instr):
    src1 = env.pop()
    if instr.name == "popnum":
        env.add_lazy_tac(IRTac(TAC_OP.PRINT_NUM, src1))
    elif instr.name == "popchar":
        env.add_lazy_tac(IRTac(TAC_OP.PRINT_CHAR, src1))
    elif instr.name == "pop":
        pass
    else:
        raise Exception("NON REACHABLE")
        

def convert_push(env, instr):
    temp = env.newtemp()
    if instr.name == "push":
        env.add_eager_tac(IRTac(TAC_OP.ASSIGN_VAL, dest=temp, imm=int(instr.arg)))
    elif instr.name == "pushnum":
        env.add_eager_tac(IRTac(TAC_OP.ASSIGN_CHAR, dest=temp))
    elif instr.name == "pushchar":
        env.add_eager_tac(IRTac(TAC_OP.ASSIGN_NUM, dest=temp))
    else:
        raise Exception("NON REACHABLE")
    env.push(temp)


def convert_dup(env, instr):
    temp = env.peek()
    env.push(temp)

def convert_swap(env, instr):
    x = env.pop()
    y = env.pop()
    env.push(x)
    env.push(y)

def convert_sel(env, instr):
    stackno = int(instr.arg)
    if stackno == QUEUENO:
        raise NotImplementedError("Queue \'ㅇ\' is not implemented yet")
    env.select_stack(stackno)


def convert_mov(env, instr):
    other_stackno = int(instr.arg)
    if env.cur_stackno == other_stackno:
        return None # NOP
    env.move(other_stackno)

def convert_brz(env, instr): 
    temp = env.pop()
    loc = env.useloc(instr.arg)
    return IRTac(TAC_OP.JZ, temp, loc=loc)

def ctor_convert_brpop(num):
    def convert_brpop(env, instr):
        return IRTac(TAC_OP.JSS, loc=env.useloc(instr.arg), imm=num)
    return convert_brpop
    

def convert_jmp(env, instr):
    return IRTac(TAC_OP.JMP, loc=env.useloc(instr.arg))


CVRTS = {
    "halt": convert_halt,
    "add": convert_binop,
    "mul": convert_binop,
    "sub": convert_binop,
    "div": convert_binop,
    "mod": convert_binop,
    "cmp": convert_binop,
    "pop": convert_pop,
    "popchar": convert_pop,
    "popnum": convert_pop,
    "popchar": convert_pop,
    "push": convert_push,
    "pushnum": convert_push,
    "pushchar": convert_push,
    "dup": convert_dup,
    "swap": convert_swap,
    "sel": convert_sel,
    "mov": convert_mov,
    "brz": convert_brz,
    "brpop1": ctor_convert_brpop(1),
    "brpop2": ctor_convert_brpop(2),
    "jmp": convert_jmp,
}

# TODO: is the initial stackno set to 0?
INITIAL_STACKNO = 0
QUEUENO = 21
HEAD_STACK_MAGIC = "@head"
BASE_STACK_MAGIC = "@base"

class StackEnv(object):
    def __init__(self, stackno):
        self.stackno = stackno
        self.reset()

    def reset(self):
        self.stack_top = 0
        self.stack = [] # stack[0], stack[1], ...
        self.neg_stack = [] # ..., stack[-1]
        self.args = [] # intial values of stack[-1], stack[-2], ...

    def pop(self, sym_env):
        self.stack_top -= 1
        try:
            return self.stack.pop()
        except IndexError:
            try:
                return self.neg_stack.pop()
            except IndexError:
                temp = sym_env.newtemp()
                self.args.append(temp)
                return temp

    def push(self, elem):
        if self.stack_top >= 0:
            self.stack.append(elem)
        else:
            self.neg_stack.append(elem)
        self.stack_top += 1

    def peek(self, sym_env):
        elem = self.pop(sym_env)
        self.push(elem)
        return elem


    def retrieve_mapping(self):
        '''
        Returns -
            {
                "args": TacTemp list
                "pop_n": int
                "push": TacTemp list
            }
        '''
        return {"args": self.args, 
                "pop_n": len(self.args),
                "push": self.neg_stack + self.stack}




class GlobalSymbolEnv(object):
    def __init__(self):
        self.defined_locs = set()
        self.used_loc = set()
        self.loc_pool = {}
        self.temp_pool = {}
        self.temp_last_id = 0

    def newtemp(self):
        self.temp_last_id += 1
        name = "_t%d"%self.temp_last_id
        temp = TacTemp(name)
        self.temp_pool[name] = temp
        return temp

    def defloc(self, locname):
        assert (isinstance(locname, basestring))
        self.defined_locs.add(locname)
        return self._get_loc(locname)

    def useloc(self, locname):
        assert (isinstance(locname, basestring))
        self.used_loc.add(locname)
        return self._get_loc(locname)


    def _get_loc(self, locname):
        try:
            return self.loc_pool[locname]
        except KeyError:
            loc = IRLoc(locname)
            self.loc_pool[locname] = loc
            return loc



class BlockConverter(object):
    def __init__(self, gblsym_env):
        self.gblsym_env = gblsym_env
        self.reset()


    def reset(self):
        self.stack_env_dict = {} # (int or HEAD_STACK_MAGIC) |-> StackEnv
        self.cur_stackno = None
        self.lazy_tac_list = []
        self.eager_tac_list = []
        self.stackno_changed = False


    def add_lazy_tac(self, tac):
        self.lazy_tac_list.append(tac)

    def add_eager_tac(self, tac):
        self.eager_tac_list.append(tac)
    
    def flush_eager_tac(self):
        result = self.eager_tac_list
        self.eager_tac_list = []
        return result

    def stackenv(self, stackno=None):
        if stackno is None:
            return self.stack_env_dict[self.cur_stackno]
        else:
            if stackno not in self.stack_env_dict:
                self.stack_env_dict[stackno] = StackEnv(stackno)
            return self.stack_env_dict[stackno]
        

    def select_stack(self, new_stackno):
        assert (new_stackno is not None)
        if self.cur_stackno == new_stackno:
            return

        self.stackno_changed = True
        self.cur_stackno = new_stackno
        if self.cur_stackno not in self.stack_env_dict:
            self.stack_env_dict[self.cur_stackno] = StackEnv(self.cur_stackno)
        

    def newtemp(self):
        return self.gblsym_env.newtemp()

    def useloc(self, locname):
        return self.gblsym_env.useloc(locname)

    def defloc(self, locname):
        return self.gblsym_env.defloc(locname)


    def move(self, dest_stackno):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            t = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.POP, dest=t))
            self.add_eager_tac(IRTac(TAC_OP.PUSH, t, stackno=dest_stackno))
        else:
            t = self.pop()
            self.stackenv(dest_stackno).push(t)

    def push(self, elem):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            # use runtime stack instead of compile-time stack
            self.add_eager_tac(IRTac(TAC_OP.PUSH, elem))
        else:
            self.stackenv().push(elem)

    def pop(self):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            temp = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.POP, dest=temp))
            return temp
        else:
            return self.stackenv().pop(self.gblsym_env)

    def peek(self):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            temp = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.PEEK, dest=temp))
            return temp
        else:
            return self.stackenv().peek(self.gblsym_env)

    def convert(self, block):
        '''
        self x asmblock -> IR list
        '''

        self.select_stack(block.stackno)

        head_result = []
        result = []
        def add(code):
            if code is None:
                pass
            elif isinstance(code, (list, tuple)):
                for elem in code:
                    add(elem)
            else:
                assert (isinstance(code, IR))
                result.append(code)

        def add_to_head(code):
            if code is None:
                pass
            elif isinstance(code, (list, tuple)):
                for elem in code:
                    add_to_head(elem)
            else:
                assert (isinstance(code, IR))
                head_result.append(code)

        for instr in block.asmlist:
            if instr.is_loc:
                pass
            else:
                last_tac = CVRTS[instr.name](self, instr)
                if self.cur_stackno == HEAD_STACK_MAGIC:
                    add_to_head(self.flush_eager_tac())
                    add_to_head(last_tac)
                else:
                    add(self.flush_eager_tac())
                    add(last_tac)

        # Now, translate jmp operation (if exists)
        trailing_jmp = block.trailing_jmp
        jmp_codes = []
        if trailing_jmp is not None:
            jmp_codes = [CVRTS[trailing_jmp.name](self, trailing_jmp)]
            jmp_codes = self.flush_eager_tac() + jmp_codes 

        # flush lazy tacs
        add(self.lazy_tac_list)
        self.lazy_tac_list = []

        # get header and trailer for a block
        args_header = []
        args_trailer = []

        generate_stack_base = False
        for stackenv in self.stack_env_dict.values():
            mapping = stackenv.retrieve_mapping()
            stackno = stackenv.stackno

            pop_stackno = stackno
            if stackno == HEAD_STACK_MAGIC:
                # we can use current stack without specifying stack number
                pop_stackno = None 
            for idx, argtemp in enumerate(mapping["args"]):
                args_header.append(IRComment(
                    "%s: arg#%d"%(repr(stackno), idx)))
                args_header.append(IRTac(TAC_OP.POP, 
                                         dest=argtemp,
                                         stackno=pop_stackno))

            push_len = len(mapping["push"])
            for idx, argtemp in enumerate(mapping["push"]):
                push_stackno = stackno
                if stackno == HEAD_STACK_MAGIC:
                    if self.cur_stackno != HEAD_STACK_MAGIC:
                        generate_stack_base = True
                        push_stackno = BASE_STACK_MAGIC
                    else:
                        push_stackno = None # we can use current stack
                args_trailer.append(IRComment("%s: ret #%d"%(repr(stackno), push_len - idx - 1)))
                args_trailer.append(IRTac(TAC_OP.PUSH, argtemp, stackno=push_stackno))

        # install setbasestack at the header if needed
        if generate_stack_base:
            args_header.insert(0, IRTac(TAC_OP.SET_BASE_STACK))

        # install header and trailer
        result = args_header + result
        result.extend(args_trailer)

        # append stack select if stckno was changed
        if self.stackno_changed and self.cur_stackno is not None and self.cur_stackno is not HEAD_STACK_MAGIC:
            add(IRTac(TAC_OP.STACK_SEL, stackno=self.cur_stackno))

        # append jmp 
        if jmp_codes:
            add(jmp_codes)

        # Finally, prepend jmp location to the head of block
        if block.loc:
            head_result.insert(0, block.loc)
        return head_result + result

class TacGenerator(object):
    def generate(self, asm_str):
        '''
        self x string -> IR list
        '''
        sym_env = GlobalSymbolEnv()
        result = []
        for block in make_block_graph(sym_env, 
                                      list(parse_aheui_asm(asm_str))).blocks:
            converter = BlockConverter(sym_env)
            result.append(IRComment("Block %d"%block.block_id))
            result.extend(converter.convert(block))
        return result
