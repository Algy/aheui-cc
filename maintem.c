#include <stdio.h>
#include <stdlib.h>

#ifndef MAX_STACK_SIZE 
# define MAX_STACK_SIZE 14096
#endif
#define STACK_CELL_COUNT 33

#ifndef MAX_QUEUE_SIZE
# define MAX_QUEUE_SIZE 14096
#endif
typedef long long cell_t; 
typedef unsigned int unichar_t;

/* Helper macros */
#define HEX__(n) 0x##n##LU
#define B8__(x) ((x&0x0000000FLU)?1:0) \
    +((x&0x000000F0LU)?2:0) \
+((x&0x00000F00LU)?4:0) \
+((x&0x0000F000LU)?8:0) \
+((x&0x000F0000LU)?16:0) \
+((x&0x00F00000LU)?32:0) \
+((x&0x0F000000LU)?64:0) \
+((x&0xF0000000LU)?128:0)

/* User macros */
#define B8(d) ((unsigned char)B8__(HEX__(d)))

static void illegal_utf8(const char* msg) {
    fprintf(stderr, "Illegal UTF-8 character: %s\n", msg);
    abort();
}


static inline void _printchar (unichar_t num) {
    int size;
    int header_bits;
    unsigned char header_magic;
    if (num <= 0x007F) {
        header_magic = B8(0);
        header_bits = 1;
        size = 0;
    } else if (num <= 0x07FF) {
        header_magic = B8(110);
        header_bits = 3;
        size = 1;
    } else if (num <= 0xFFFF) {
        header_magic = B8(1110);
        header_bits = 4;
        size = 2;
    } else if (num <= 0x1FFFFF) {
        header_magic = B8(11110);
        header_bits = 5;
        size = 3;
    } else if (num <= 0x3FFFFFF) {
        header_magic = B8(111110);
        header_bits = 6;
        size = 4;
    } else if (num <= 0x7FFFFFFF) {
        header_magic = B8(1111110);
        header_bits = 7;
        size = 5;
    } else {
        putchar('?');
        return;
    }

    char result[6];
    int idx;
    for (idx = size; idx > 0; idx--) {
        result[idx] = B8(10000000) + (num & B8(111111));
        num >>= 6;
    }
    result[0] = num + (header_magic << (8 - header_bits));
    putchar((int)result[0]);
    for (idx = 1; idx <= size; idx++) {
        putchar((int)result[idx]);
    }
}

static inline void _printnum (cell_t c) {
    printf("%lld", c);
}


#define CHECK_EOF(c) { \
    if (c == EOF) { \
        fprintf(stderr, "met EOF while reading a character\n"); \
        abort(); \
    } \
}

static inline unichar_t _getchar () {
    int i_c1 = getchar();
    CHECK_EOF(i_c1);
    unsigned char c1 = (unsigned char)i_c1;
    unichar_t result;
    if (c1 >> 7) {
        int size = 0;
        if ((c1 >> 5) == B8(110)) {
            // 110xxxxx
            result = c1 & B8(11111);
            size = 1;
        } else if ((c1 >> 4) == B8(1110)) {
            // 1110xxxx
            result = c1 & B8(1111);
            size = 2;
        } else if ((c1 >> 3) == B8(11110)) { 
            // 11110xxx
            result = c1 & B8(111);
            size = 3;
        } else if ((c1 >> 2) == B8(111110)) { 
            // 111110xx
            result = c1 & B8(11);
            size = 4;
        } else if ((c1 >> 1) == B8(1111110)) { 
            result = c1 & B8(1);
            size = 5;
        } else {
            char s[100];
            sprintf(s, "Invalid character number: %x", c1);
            illegal_utf8(s);
        }

        int idx = 0;
        for (idx = 0; idx < size; idx++) {
            int i_nc = getchar();
            CHECK_EOF(i_nc);
            unsigned char nc = (unsigned char)i_nc;
            if ((nc >> 6) != B8(10))
                illegal_utf8("Following characters after first character in utf-8 encoding should start with 10(binary)");
            result = (result << 6) + (nc & B8(111111));
        }
    } else {
        result = (unichar_t)c1;
    }
    // fprintf(stderr, "Input char ord: %d\n", result);
    return result;
}

static inline cell_t _getnum() {
    cell_t c;
    scanf("%lld", &c);
    return c;
}

cell_t *queue;
cell_t *queue_front, *queue_back;
int _is_queuemode = 0;

static inline void _enterqueuemode() {
    _is_queuemode = 1;
}

static inline void _leavequeuemode() {
    _is_queuemode = 0;
}

static inline cell_t _queue_len() {
    if (queue_front <= queue_back) {
        return queue_back - queue_front;
    } else {
        return queue_back + MAX_QUEUE_SIZE - queue_front;
    }
}

#define QUEUE_CHECK_STUB(check_overflow) { \
    if (check_overflow) { \
        cell_t* head_1; \
        head_1 = queue_back + 1; \
        if ((head_1 - queue) >= MAX_QUEUE_SIZE) \
            head_1 = queue; \
        if (head_1  == queue_front) { \
            fprintf(stderr, "Queue Overflow\n"); \
            abort(); \
        } \
    } else { \
        if (queue_back == queue_front) { \
            fprintf(stderr, "Queue Underflow\n"); \
            abort(); \
        } \
    } \
}

static inline void _enqueue(cell_t c) {
#ifdef CHECK_STACK 
    QUEUE_CHECK_STUB(1);
#endif
    *queue_back = c;
    queue_back++;
    if (queue_back - queue >= MAX_QUEUE_SIZE) queue_back = queue;
}

static inline cell_t _dequeue() {
#ifdef CHECK_STACK 
    QUEUE_CHECK_STUB(0);
#endif
    cell_t c = *queue_front;
    queue_front++;
    if (queue_front - queue >= MAX_QUEUE_SIZE) queue_front = queue;
    return c;
}

static inline cell_t _peekqueue() {
#ifdef CHECK_STACK 
    QUEUE_CHECK_STUB(0);
#endif
    return *queue_front;
}

static inline void _dupqueue() {
#ifdef CHECK_STACK 
    QUEUE_CHECK_STUB(0);
    QUEUE_CHECK_STUB(1);
#endif
    cell_t c;
    
    c = *queue_front;
    queue_front--;
    if (queue_front < queue)
        queue_front += MAX_QUEUE_SIZE;
    *queue_front = c;
}


cell_t *stack_bots[STACK_CELL_COUNT];
cell_t *stack_tops[STACK_CELL_COUNT];
cell_t** p_cur_stack_top;
cell_t** p_base_stack_top;

static inline cell_t _stack_no_len(int stackno) {
    return stack_tops[stackno] - stack_bots[stackno];
}

static inline cell_t _stack_len() {
    int stackno = p_cur_stack_top - stack_tops;
    return _stack_no_len(stackno);
}


static inline cell_t _base_stack_len() {
    int stackno = p_base_stack_top - stack_tops;
    return _stack_no_len(stackno);

}

#define STACK_CHECK_STUB(len_invocation, check_overflow)  { \
    cell_t len = len_invocation; \
    if (check_overflow) { \
        if (len >= MAX_STACK_SIZE) { \
            fprintf(stderr, "Stack Overflow\n"); \
            abort(); \
        } \
    } else { \
        if (len <= 0) { \
            fprintf(stderr, "Stack Underflow\n"); \
            abort(); \
        } \
    } \
}


static inline void _push_stack(cell_t c) {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_len(), 1);
#endif
    **p_cur_stack_top = c;
    (*p_cur_stack_top)++;
}

static inline void _dupstack() {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_len(), 1);
    STACK_CHECK_STUB(_stack_len(), 0);
#endif
    cell_t c = *((*p_cur_stack_top) - 1);
    **p_cur_stack_top = c;
    (*p_cur_stack_top)++;
}

static inline void _push(cell_t c) {
    if (_is_queuemode)
        _enqueue(c);
    else
        _push_stack(c);
}

static inline void _push_stack_no(int stackno, cell_t c) {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_no_len(stackno), 1);
#endif
    cell_t** t;
    t = &stack_tops[stackno];
    **t = c;
    (*t)++;
}
static inline void _push_base_stack(cell_t c) {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_base_stack_len(), 1);
#endif
    **p_base_stack_top = c;
    (*p_base_stack_top)++;
}

static inline void _dup() {
    if (_is_queuemode) {
        _dupqueue();
    } else {
        _dupstack();
    }
}

static inline void _stack_sel(int stackno) {
    p_cur_stack_top = &stack_tops[stackno];
}

static inline void _set_base_stack() {
    p_base_stack_top = p_cur_stack_top;
}


static inline cell_t _peek_stack() {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_len(), 0);
#endif
    return *((*p_cur_stack_top) - 1);
}

static inline cell_t _peek() {
    if (_is_queuemode)
        return _peekqueue();
    else
        return _peek_stack();
}

static inline cell_t _peek_stack_no(int stackno) {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_no_len(stackno), 0);
#endif
    return *(stack_tops[stackno] - 1);
}

static inline cell_t _peek_base_stack() {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_base_stack_len(), 0);
#endif
    return *((*p_base_stack_top) - 1);
}

static inline cell_t _pop_stack() {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_len(), 0);
#endif
    (*p_cur_stack_top)--;
    return **p_cur_stack_top;
}

static inline cell_t _pop() {
    if (_is_queuemode)
        return _dequeue();
    else
        return _pop_stack();
}


static inline cell_t _pop_stack_no(int stackno) {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_stack_no_len(stackno), 0);
#endif
    stack_tops[stackno]--;
    return *stack_tops[stackno];
}

static inline cell_t _pop_base_stack() {
#ifdef CHECK_STACK
    STACK_CHECK_STUB(_base_stack_len(), 0);
#endif
    (*p_base_stack_top)--;
    return **p_base_stack_top;
}


static inline cell_t _storage_len() {
    if (_is_queuemode)
        return _queue_len();
    else
        return _stack_len();
}


void setup_stack() {
    int idx;
    for (idx = 0; idx < STACK_CELL_COUNT; idx++) {
        stack_bots[idx] = stack_tops[idx] = malloc(MAX_STACK_SIZE * sizeof(cell_t));
    }
    queue = queue_back = queue_front = malloc(MAX_QUEUE_SIZE * sizeof(cell_t));
    p_cur_stack_top = p_base_stack_top = &stack_tops[0];
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


