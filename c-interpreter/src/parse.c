#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "params.h"
#include "parse.h"

void printInstruction(struct Instruction i)
{
    printf("Δ(%s,%s) = (%s,%d,%s)\n", i.startState, i.matchSymbol, i.replaceWith, i.offset, i.endState);
}

char *allocateCharArrayOnHeap(int n)
{
    return (char *)malloc(n * sizeof(char));
}

void freeInstruction(struct Instruction *ptr) {
    free(ptr->startState);
    free(ptr->endState);
    free(ptr->matchSymbol);
    free(ptr->replaceWith);
    free(ptr);
    return;
}

struct Instruction *parseSingleInstruction(char *line)
{
    char *startState = allocateCharArrayOnHeap(MAX_STATE_NAME_SIZE);
    char *endState = allocateCharArrayOnHeap(MAX_STATE_NAME_SIZE);
    char *matchSymbol = allocateCharArrayOnHeap(MAX_SYMBOL_LENGTH);
    char *replaceWith = allocateCharArrayOnHeap(MAX_SYMBOL_LENGTH);
    char arrow[4];

    int offset = 3;
    int i = 0;
    while (line[offset] != ',')
    {
        startState[i++] = line[offset++];
    }
    startState[i] = '\0';

    offset++;
    i = 0;
    while (line[offset] != ')')
    {
        matchSymbol[i++] = line[offset++];
    }
    matchSymbol[i] = '\0';

    offset += 5;
    i = 0;
    while (line[offset] != ',')
    {
        replaceWith[i++] = line[offset++];
    }
    replaceWith[i] = '\0';

    offset++;
    i = 0;
    while (line[offset] != ',')
    {
        arrow[i++] = line[offset++];
    }
    arrow[i] = '\0';

    offset++;
    i = 0;
    while (line[offset] != ')')
    {
        endState[i++] = line[offset++];
    }
    endState[i] = '\0';        
    
    struct Instruction *instruction = (struct Instruction *)malloc(sizeof(struct Instruction));
    instruction->startState = startState;
    instruction->endState = endState;
    instruction->matchSymbol = matchSymbol;
    instruction->replaceWith = replaceWith;
    instruction->offset = strcmp(arrow, "←") == 0 ? -1 : 1;

    return instruction;
}

struct HashMap *parseInstructions(FILE *fp, int *count)
{
    *count = 0;
    while (!feof(fp))
    {
        if (fgetc(fp) == '\n')
        {
            (*count)++;
        }
    }

    struct HashMap *instructions = newHashMap(1024);
    fseek(fp, 0, SEEK_SET);
    char line[MAX_LINE_LENGTH];
    for (int i = 0; i < (*count); i++)
    {
        struct Instruction *instruction = parseSingleInstruction(fgets(line, 1024, fp));
        struct HashMap *symbolHashMap = (struct HashMap *)hashMapGet(instructions, instruction->startState);
        if (symbolHashMap == NULL) {
            symbolHashMap = newHashMap(128);
            hashMapPut(instructions, instruction->startState, symbolHashMap);
        }
        hashMapPut(symbolHashMap, instruction->matchSymbol, instruction);
    }

    return instructions;
}
