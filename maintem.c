#include <stdio.h>
#include <stdlib.h>

#define MAX_STACK_SIZE 4096
#define STACK_CELL_COUNT 33
typedef long long cell_t; 
typedef unsigned long long unichar_t;

static inline void _printchar (unichar_t num) {
    putchar((int)num);
}

static inline void _printnum (cell_t c) {
    printf("%lld", c);
}

static inline unichar_t _getchar () {
    return (unichar_t) getchar();
}

static inline cell_t _getnum() {
    cell_t c;
    scanf("%lld", &c);
    return c;
}




cell_t *stack_bots[STACK_CELL_COUNT];
cell_t *stack_tops[STACK_CELL_COUNT];
cell_t** p_cur_stack_top;
cell_t** p_base_stack_top;

static inline void _push_stack(cell_t c) {
    **p_cur_stack_top = c;
    (*p_cur_stack_top)++;
}

static inline void _push_stack_no(int stackno, cell_t c) {
    cell_t** t;
    t = &stack_tops[stackno];
    **t = c;
    (*t)++;
}
static inline void _push_base_stack(cell_t c) {
    **p_base_stack_top = c;
    (*p_base_stack_top)++;
}

static inline void _stack_sel(int stackno) {
    p_cur_stack_top = &stack_tops[stackno];
}

static inline void _set_base_stack() {
    p_base_stack_top = p_cur_stack_top;
}

static inline cell_t _peek_stack() {
    return *((*p_cur_stack_top) - 1);
}

static inline cell_t _peek_stack_no(int stackno) {
    return *(stack_tops[stackno] - 1);
}

static inline cell_t _peek_base_stack() {
    return *((*p_base_stack_top) - 1);
}

static inline cell_t _pop_stack() {
    (*p_cur_stack_top)--;
    return **p_cur_stack_top;
}

static inline cell_t _pop_stack_no(int stackno) {
    stack_tops[stackno]--;
    return *stack_tops[stackno];
}

static inline cell_t _pop_base_stack() {
    (*p_base_stack_top)--;
    return **p_base_stack_top;
}


void setup_stack() {
    int idx;
    for (idx = 0; idx < STACK_CELL_COUNT; idx++) {
        stack_bots[idx] = stack_tops[idx] = malloc(MAX_STACK_SIZE * sizeof(cell_t));
    }
    p_cur_stack_top = p_base_stack_top = &stack_tops[0];
}

static inline cell_t _stack_no_len(int stackno) {
    return (stack_tops[stackno] - stack_bots[stackno]) / sizeof(cell_t);
}

static inline cell_t _stack_len() {
    int stackno = (p_cur_stack_top - stack_tops)/sizeof(cell_t*);
    return _stack_no_len(stackno);
}


static inline cell_t _base_stack_len() {
    int stackno = (p_base_stack_top - stack_tops)/sizeof(cell_t*);
    return _stack_no_len(stackno);

}

void main_program() {
//{_CC_MAIN}
}

int main () {
    setup_stack();
    main_program();

        
    if (_stack_len() > 0)
        return (int)_pop_stack();
    return 0;
}


