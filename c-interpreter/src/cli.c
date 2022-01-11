#include <stdio.h>
#include "parse.h"
#include "interpret.h"
#include "tape.h"

int main(int argc, char **argv)
{

    if (argc != 2 && argc != 3)
    {
        printf("Usage: %s [program] [initialTape]\n", argv[0]);
        return 1;
    }

    FILE *fp = fopen(argv[1], "r");

    if (fp == NULL)
    {
        printf("No such file: %s\n", argv[1]);
        return 2;
    }

    int instructionCount;
    struct HashMap *instructions = parseInstructions(fp, &instructionCount);
    fclose(fp);

    char *initialTape;
    if (argc == 3)
    {
        initialTape = argv[2];
    }
    else
    {
        initialTape = "";
    }

    struct Cell *currentCell = constructTape(initialTape);

    struct Cell *final = interpret("start", instructions, instructionCount, currentCell, 0);

    printf("%s\n", tapeToString(final, 0));

    return 0;
}