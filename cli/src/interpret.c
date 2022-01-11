#include <stdio.h>
#include <string.h>
#include "params.h"
#include "interpret.h"

struct Instruction *nextInstruction(char *state, struct Instruction *instructions, int instructionCount, char *symbol)
{
    for (int i = 0; i < instructionCount; i++)
    {
        if ((strcmp(instructions[i].startState, state) == 0) && (strcmp(instructions[i].matchSymbol, symbol) == 0))
        {
            return instructions + i;
        }
    }
    return NULL;
}

struct Cell *interpret(char *state, struct Instruction *instructions, int instructionCount, struct Cell *current, int verbose)
{
    struct Instruction *toApply;
    while ((toApply = nextInstruction(state, instructions, instructionCount, current->value)) != NULL)
    {
        if (verbose)
        {
            printf("%s: '%s'\n", state, tapeToString(current, 1));
        }

        strcpy(current->value, toApply->replaceWith);
        state = toApply->endState;
        if (toApply->offset == -1)
        {
            current = prevCell(current);
        }
        else
        {
            current = nextCell(current);
        }
    }
    return current;
}