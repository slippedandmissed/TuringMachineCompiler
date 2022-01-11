#pragma once

struct Instruction
{
    char *startState;
    char *endState;
    char *matchSymbol;
    char *replaceWith;
    int offset;
};

void printInstruction(struct Instruction);

struct Instruction *parseInstructions(FILE *fp, int *count);