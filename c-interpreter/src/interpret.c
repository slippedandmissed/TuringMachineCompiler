#include <stdio.h>
#include <string.h>
#include "params.h"
#include "interpret.h"

struct Instruction *nextInstruction(char *state, struct HashMap *instructions, int instructionCount, char *symbol)
{
    struct HashMap *symbolHashMap = (struct HashMap *)hashMapGet(instructions, state);
    if (symbolHashMap == NULL)
    {
        return NULL;
    }
    return hashMapGet(symbolHashMap, symbol);
}

struct Cell *interpret(char *state, struct HashMap *instructions, int instructionCount, struct Cell *current, int verbose)
{
    struct Instruction *toApply;
    while ((toApply = nextInstruction(state, instructions, instructionCount, current->value)) != NULL)
    {
        if (verbose)
        {
            printf("%s: '%s'", state, tapeToString(current, 1));
            if (verbose > 1)
            {
                printf(" - applying ");
                printInstruction(*toApply);
            }
            else
            {
                printf("\n");
            }
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