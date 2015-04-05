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

    # if stackno is None:
    #   current_storage <-  src1
    # else:
    #   stack[stackno] <- src1
    PUSH = "push"

    # enqueue(src1)
    ENQUEUE = "enqueue"
    # dest = dequeue()
    DEQUEUE = "dequeue"
    # dest = peekqueue()
    PEEKQUEUE = "peekqueue"

    # dup()
    DUP = "dup"
    # dupqueue()
    DUPQUEUE = "dupqueue"

    # enterqueuemode
    ENTERQUEUEMODE = "enterqueuemode"
    # leavequeuemode
    LEAVEQUEUEMODE = "leavequeuemode"


    # cur_stackno = stackno
    STACK_SEL = "stacksel"

    # base_stackno = cur_stackno (no arguments required)
    SET_BASE_STACK = "setbasestack"

    # if stackno is None:
    #   dest (may be None) = pop from current storage (can be both stack and queue)
    # else:
    #   dest (may be None) = pop from stack[stackno]
    POP = "pop"

    # if stackno is None:
    #   dest (may be None) = peek from current storage (can be both stack and queue)
    # else:
    #   dest (may be None) = peek from stack[stackno]
    PEEK = "peek"

    # jmp loc
    JMP = "jmp"

    # if imm == 0:
    #   if stackno is not None:
    #     pop and jmp to loc if stack[stackno] is not empty and its top is 0
    #     o.w. just pop (if the stack is empty, skip this operation and jmp to loc)
    #   else:
    #     pop and jmp if current_storage is not empty and its top is 0
    #     o.w. just pop (if the storage is empty, skip this operation and jmp to loc)
    # else:
    #   pop and jmp if queue is not empty and its front is 0
    #   o.w. just pop front (if the queue is empty, skip this operation and jmp to loc)
    POPANDJZ = "popandjz"


    # Jump if length of the current stack or queue is less than imm
    JSTORAGE = "jstorage" 

    # Jump if length of stack[stackno] is less than imm
    JSS = "jss"

    # Jump if length of the queue is less than imm
    JQS = "jqs"

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

def repr_op_enqueue(tac):
    return "enqueue <- %s"%(tac.src1.name)

def repr_op_dequeue(tac):
    return "%s = dequeue" % (tac.dest.name)

def repr_op_peekqueue(tac):
    return "%s = peekqueue" % (tac.dest.name)


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

def repr_op_popandjz(tac):
    if tac.imm != 0:
        return "popandjmp queue -> %s"%(tac.loc.name)
    elif tac.stackno is not None:
        return "popandjmp stack[%s] -> %s"%(repr(tac.stackno), tac.loc.name)
    else:
        return "popandjmp cur_storage -> %s"%(tac.loc.name)

def repr_op_jss(tac):
    return "jmp %s, if len(stack[%s]) < %d"%(tac.loc.name, repr(tac.stackno), tac.imm)

def repr_op_jqs(tac):
    return "jmp %s, if len(queue) < %d"%(tac.loc.name, tac.imm)

def repr_op_jstorage(tac):
    return "jmp %s, if len(cur_storage) < %d"%(tac.loc.name, tac.imm)

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
    TAC_OP.ENQUEUE: repr_op_enqueue,
    TAC_OP.DEQUEUE: repr_op_dequeue,
    TAC_OP.PEEKQUEUE: repr_op_peekqueue,
    TAC_OP.STACK_SEL: repr_op_stack_sel,
    TAC_OP.SET_BASE_STACK: repr_op_set_base_stack, 
    TAC_OP.ENTERQUEUEMODE: lambda _: "enter queuemode",
    TAC_OP.LEAVEQUEUEMODE: lambda _: "leave queuemode",
    TAC_OP.DUP: lambda _: "dup",
    TAC_OP.DUPQUEUE: lambda _: "dupqueue",
    TAC_OP.POP: repr_op_stack_pop,
    TAC_OP.PEEK: repr_op_stack_peek,
    TAC_OP.JMP: repr_op_jmp,
    TAC_OP.POPANDJZ: repr_op_popandjz,
    TAC_OP.JSS: repr_op_jss,
    TAC_OP.JQS: repr_op_jqs,
    TAC_OP.JSTORAGE: repr_op_jstorage,
    TAC_OP.HALT: repr_op_halt,
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
            block.incomming_blocks.append(prev_block)
        prev_block = block
        result_blocks.append(block)
        if locname is not None:
            locname_to_block[locname] = block

    for block in result_blocks:
        if block.jmp_loc:
            block.jmp_block = locname_to_block[block.jmp_loc.name];
            block.jmp_block.incomming_blocks.append(block)

        
    if result_blocks:
        start_block = result_blocks[0]
    else:
        start_block = None
    blockgraph = BlockGraph(result_blocks, start_block, block_id_cnt)
    blockgraph.infer_final_stackno()
    blockgraph.infer_possible_initial_stacknos()

    return blockgraph
            

class BlockGraph(object):
    def __init__(self, blocks, start_block, id_cnt):
        self.blocks = blocks
        self.start_block = start_block
        self.id_cnt = id_cnt


    def is_start_block(self, block):
        return self.start_block.block_id == block.block_id
    
    def infer_final_stackno(self):
        '''
        Fill up each `final_stackno` field of all the blocks
        '''
        for block in self.blocks:
            try:
                final_stackno = (int(asm.arg) 
                                 for asm in block.asmlist[::-1] 
                                 if not asm.is_loc and asm.name == "sel").next()
            except StopIteration:
                final_stackno = HEAD_STACK_MAGIC
            block.final_stackno = final_stackno
            # pprint("block %d -> finalstackno "%block.block_id + str(final_stackno))

    def infer_possible_initial_stacknos(self): 
        # FIXME
        # requires both block.incomming_blocks and block.final_stackno to be already filled up
        # provides block.initial_stackno, block.possible_initial_stacknos

        # First, gather constraints

        # blockid |-> stackno set
        const_constraints = {} 
        # blockid |-> blockid set
        constraints = {} 

        for block in self.blocks:
            const_stacknos = set()
            dependent_block_ids = set()
            for incomming in block.get_incomming_blocks():
                if incomming.final_stackno == HEAD_STACK_MAGIC:
                    dependent_block_ids.add(incomming.block_id)
                else:
                    const_stacknos.add(incomming.final_stackno)
            if self.is_start_block(block):
                const_stacknos.add(INITIAL_STACKNO)

            if dependent_block_ids:
                constraints[block.block_id] = dependent_block_ids
            const_constraints[block.block_id] = const_stacknos

        # Second, propagate constants
        store = {} # blockid |-> stackno set
        for block_id, stacknoset in const_constraints.items():
            store[block_id] = set(stacknoset)

        # Third, propagate linked constraints repeatedly
        # until propagation doesn't affect any block's possible stacknos
        candidates = set(filter(lambda k: k in constraints, constraints.keys()))
        while candidates:
            cand_block_id = candidates.pop()
            assert (cand_block_id in constraints)

            prop_has_effect = False
            for source_block_id in constraints[cand_block_id]:
                dest_set = store[cand_block_id]
                for propagated_stackno in store[source_block_id]:
                    if propagated_stackno not in dest_set:
                        prop_has_effect = True
                        dest_set.add(propagated_stackno)
            if prop_has_effect:
                for outgoing in self.blocks[cand_block_id].get_outgoing_blocks():
                    if outgoing.block_id in constraints:
                        candidates.add(outgoing.block_id)

        # Check soundness, to say, whether the above is right. If not, There must be a bug!
        for block_id, sol_set in store.items():
            test_set = set()
            for c in constraints.get(block_id, []):
                test_set.update(store[c])
            test_set.update(const_constraints[block_id])
            if sol_set != test_set:
                raise Exception('Error: %s is not sound solution for Block %d. We get %s'%(repr(sol_set), block_id, repr(test_set)))

        # Finally, Retrieve possible stacknos from `store`, with which each block starts.
        for block_id, possible_initial_stacknos in store.items():
            self.blocks[block_id].possible_initial_stacknos = possible_initial_stacknos

        # Plus, if the number of possible stacknos is one, we can set block.initial_stackno to the only element of them
        for b in self.blocks:
            assert (len(b.possible_initial_stacknos) > 0)
            if len(b.possible_initial_stacknos) == 1:
                b.initial_stackno = iter(b.possible_initial_stacknos).next()
                if b.final_stackno == HEAD_STACK_MAGIC:
                    b.final_stackno = b.initial_stackno
            


class CodeBlock(object):
    def __init__(self, block_id, asmlist, loc=None, trailing_jmp=None, jmp_loc=None):
        self.block_id = block_id
        self.asmlist = asmlist
        self.trailing_jmp = trailing_jmp
        self.loc = loc # IRLoc or None
        self.jmp_loc = jmp_loc 
        self.jmp_block = None
        self.next_block = None
        self.incomming_blocks = []

        self.initial_stackno = HEAD_STACK_MAGIC

        self.final_stackno = HEAD_STACK_MAGIC
        self.possible_initial_stacknos = None

    def should_emit_enterqueuemode(self):
        assert (self.final_stackno is not None)
        if self.final_stackno == QUEUENO:
            return any(self.ambiguous_stack_or_queue() 
                       for self in self.get_outgoing_blocks())
        return False

    
    def get_outgoing_blocks(self):
        return filter(bool, [self.jmp_block, self.next_block]) # filter None

    def get_incomming_blocks(self):
        return self.incomming_blocks

    def ambiguous_storage(self):
        if self.possible_initial_stacknos is None:
            return True
        return len(self.possible_initial_stacknos) > 1

    def ambiguous_stack_or_queue(self):
        if self.possible_initial_stacknos is None:
            return True
        return (len(self.possible_initial_stacknos) > 1 and
                QUEUENO in self.possible_initial_stacknos)

    def initial_queue_possible(self):
        return QUEUENO in self.possible_initial_stacknos

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
        env.add_eager_tac(IRTac(TAC_OP.ASSIGN_NUM, dest=temp))
    elif instr.name == "pushchar":
        env.add_eager_tac(IRTac(TAC_OP.ASSIGN_CHAR, dest=temp))
    else:
        raise Exception("NON REACHABLE")
    env.push(temp)


def convert_dup(env, instr):
    env.dup()

def convert_swap(env, instr):
    x = env.pop()
    y = env.pop()
    env.push(x)
    env.push(y)

def convert_sel(env, instr):
    stackno = int(instr.arg)
    env.select_stack(stackno)


def convert_mov(env, instr):
    other_stackno = int(instr.arg)
    env.move(other_stackno)

def convert_brz(env, instr): 
    loc = env.useloc(instr.arg)
    if env.cur_stackno == HEAD_STACK_MAGIC:
        return IRTac(TAC_OP.POPANDJZ, loc=loc, imm=0)
    elif env.cur_stackno == QUEUENO:
        return IRTac(TAC_OP.POPANDJZ, loc=loc, imm=1)
    else:
        return IRTac(TAC_OP.POPANDJZ, loc=loc, stackno=env.cur_stackno, imm=0)


def ctor_convert_brpop(num):
    def convert_brpop(env, instr):
        loc = env.useloc(instr.arg)
        if env.cur_stackno == HEAD_STACK_MAGIC:
            return IRTac(TAC_OP.JSTORAGE, loc=loc, imm=num)
        elif env.cur_stackno == QUEUENO:
            return IRTac(TAC_OP.JQS, loc=loc, imm=num)
        else:
            return IRTac(TAC_OP.JSS, loc=loc, stackno=env.cur_stackno, imm=num)
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
        self.block_to_convert = None

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
        

    def _select_stack(self, new_stackno):
        assert (new_stackno is not None)
        if self.cur_stackno == new_stackno:
            return
        self.cur_stackno = new_stackno
        if self.cur_stackno not in self.stack_env_dict:
            self.stack_env_dict[self.cur_stackno] = StackEnv(self.cur_stackno)
        

    def select_stack(self, new_stackno):
        assert (new_stackno is not None)
        if self.cur_stackno == HEAD_STACK_MAGIC:
            # install a LEAVEQUEUEMODE guard
            self.add_eager_tac(IRTac(TAC_OP.LEAVEQUEUEMODE)) 
        self._select_stack(new_stackno)
        

    def newtemp(self):
        return self.gblsym_env.newtemp()

    def useloc(self, locname):
        return self.gblsym_env.useloc(locname)

    def defloc(self, locname):
        return self.gblsym_env.defloc(locname)


    def move(self, dest_stackno):
        use_runtime_stack = False
        if self.cur_stackno == QUEUENO:
            t = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.DEQUEUE, dest=t))
        elif self.cur_stackno == HEAD_STACK_MAGIC:
            t = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.POP, dest=t))
            use_runtime_stack = True
        else:
            t = self.pop()
        # t should exist here in any cases

        if dest_stackno == QUEUENO:
            self.add_eager_tac(IRTac(TAC_OP.ENQUEUE, t))
        elif use_runtime_stack:
            self.add_eager_tac(IRTac(TAC_OP.PUSH, t, stackno=dest_stackno))
        else:
            self.stackenv(dest_stackno).push(t)

    def push(self, elem):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            self.add_eager_tac(IRTac(TAC_OP.PUSH, elem))
        elif self.cur_stackno == QUEUENO:
            self.add_eager_tac(IRTac(TAC_OP.ENQUEUE, elem))
        else:
            self.stackenv().push(elem)

    def pop(self):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            temp = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.POP, dest=temp))
            return temp
        elif self.cur_stackno == QUEUENO:
            temp = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.DEQUEUE, dest=temp))
            return temp
        else:
            return self.stackenv().pop(self.gblsym_env)

    def peek(self):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            temp = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.PEEK, dest=temp))
            return temp
        elif self.cur_stackno == QUEUENO:
            temp = self.newtemp()
            self.add_eager_tac(IRTac(TAC_OP.PEEKQUEUE, dest=temp))
            return temp
        else:
            return self.stackenv().peek(self.gblsym_env)

    def dup(self):
        if self.cur_stackno == HEAD_STACK_MAGIC:
            self.add_eager_tac(IRTac(TAC_OP.DUP))
        elif self.cur_stackno == QUEUENO:
            self.add_eager_tac(IRTac(TAC_OP.DUPQUEUE))
        else:
            temp = self.peek()
            self.push(temp)

    def convert(self, block):
        '''
        self x asmblock -> IR list
        '''
        self.block_to_convert = block

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

        self._select_stack(block.initial_stackno)

        # First, 
        # if block.initial_stackno is not HEAD_STACK_MAGIC and
        # there's at least one block incomming to this block that can end with ENTERQUEUEMODE,
        # we should add a LEAVEQUEUEMODE instruction to head
        # (we will call it LEAVEQUEUEMODE guard)
        if (block.initial_stackno != HEAD_STACK_MAGIC and
            any(block.should_emit_enterqueuemode() 
                for block in block.get_incomming_blocks())):
            add_to_head(IRTac(TAC_OP.LEAVEQUEUEMODE))

        # Then, translate body
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
                # args_header.append(IRComment("%s: arg#%d"%(repr(stackno), idx)))
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
                # args_trailer.append(IRComment("%s: ret #%d"%(repr(stackno), push_len - idx - 1)))
                args_trailer.append(IRTac(TAC_OP.PUSH, argtemp, stackno=push_stackno))

        # install setbasestack at the header if needed
        if generate_stack_base:
            args_header.insert(0, IRTac(TAC_OP.SET_BASE_STACK))

        # install header and trailer
        result = args_header + result
        result.extend(args_trailer)

        # append stack selection 
        assert (self.cur_stackno is not None)
        if (  self.cur_stackno is not HEAD_STACK_MAGIC and
              any(block.ambiguous_storage()
                  for block in block.get_outgoing_blocks())):
            add(IRTac(TAC_OP.STACK_SEL, stackno=self.cur_stackno))

        # If this block ends with the current storage being the queue 
        # and any outgoing blocks has an ambigous stack/queue state 
        # (where we don't determine if they start with which stack or queue),
        # we should put "enterqueuemode" instruction 
        if block.should_emit_enterqueuemode():
            add(IRTac(TAC_OP.ENTERQUEUEMODE))

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
            result.append(IRComment("==Block %d=="%block.block_id))
            if block.incomming_blocks:
                cmt = "--Incommings: %s--"%(", ".join([str(b.block_id) for b in block.incomming_blocks]))
                result.append(IRComment(cmt))
            result.append(IRComment(
                "--Possible stacknos: %s--"%", ".join([str(x) 
                                                       for x in block.possible_initial_stacknos])))
            result.append(IRComment("--final stackno: %s--"%block.final_stackno))
            result.extend(converter.convert(block))
        return result

