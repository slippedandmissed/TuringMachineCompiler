#pragma once

struct Cell {
    char *value;
    struct Cell *next;
    struct Cell *prev;
};


struct Cell *nextCell(struct Cell *);
struct Cell *prevCell(struct Cell *);
struct Cell *constructTape(char *);
char *tapeToString(struct Cell *, int);