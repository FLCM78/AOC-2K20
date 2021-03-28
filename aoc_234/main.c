#include <assert.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#define NB_CUPS 1000000
#define NB_ROUDS 10000000

#define GET_VAL(c)                                                            \
({                                                                            \
     char _c = (c);                                                           \
     int _v = (int)(_c - '0' - 1);                                            \
                                                                              \
     assert (0 <= _v && _v <= 8);                                             \
                                                                              \
    _v;                                                                       \
})

int hash[NB_CUPS];
int cur = 0;

void pp_hash() {
    fputs("{", stderr);
    for (int i = 0, pos = cur; i < NB_CUPS + 1; ++i, pos = hash[pos]) {
        if (i > 0) {
            fputs(", ", stderr);
        }
    }

    fputs("}\n", stderr);
}

void init_hash(const char *init) {
    fprintf(stderr, "init with '%s'\n", init);

    int length = strlen(init);

    for (int i = 0; i < length; i++) {
        int pos = GET_VAL(init[i]);
        int prv;

        if (i == 0) {
            prv = (length == NB_CUPS) ? GET_VAL(init[length - 1]) : NB_CUPS - 1;
        } else {
            prv = GET_VAL(init[i - 1]);
        }

        hash[prv] = pos;
    }

    if (length < NB_CUPS) {
        hash[GET_VAL(init[length - 1])] = length;
    }

    cur = GET_VAL(init[0]);
}

#define NXT() (nxt == 0 ? (NB_CUPS - 1) : (nxt - 1))
void play() {
    int one = hash[cur];
    int two = hash[one];
    int three = hash[two];
    int nxt = cur;

    hash[cur] = hash[three];

    for(nxt = NXT(); nxt == one || nxt == two || nxt == three; nxt = NXT()) {}

    hash[three] = hash[nxt];
    hash[nxt] = one;

    cur = hash[cur];
}

int main(int argc, const char *argv[]) {
    for (int i = 0; i < NB_CUPS; i++) {
        hash[i] = (i + 1) % NB_CUPS;
    }

    if (argc > 1) {
        init_hash(argv[1]);
    }

    for (int i = 0; i < NB_ROUDS; ++i) {
        if (((i + 1) % 1000) == 0) {
            fprintf(stderr, "round %13d\r", i + 1);
        }

        play();
    }
    fprintf(stderr, "\n");

    fprintf(stderr, "one after 1: %d\n", hash[0] + 1);
    fprintf(stderr, "two after 1: %d\n", hash[hash[0]] + 1);
    fprintf(stderr, "result: %ld\n", (int64_t)(hash[0] + 1) * (int64_t)(hash[hash[0]] + 1));

    return 0;
}
