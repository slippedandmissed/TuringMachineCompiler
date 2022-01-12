#pragma once
#include "hashmap.h"

struct Instruction
{
    char *startState;
    char *endState;
    char *matchSymbol;
    char *replaceWith;
    int offset;
};

void printInstruction(struct Instruction);

void freeInstruction(struct Instruction *);

struct HashMap *parseInstructions(FILE *fp, int *count);