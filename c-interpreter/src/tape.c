#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "params.h"
#include "tape.h"

struct Cell *nextCell(struct Cell *current)
{
    struct Cell *nextPtr = current->next;
    if (nextPtr == NULL)
    {
        nextPtr = (struct Cell *)malloc(sizeof(struct Cell));
        nextPtr->value = (char *)malloc(sizeof(char) * MAX_SYMBOL_LENGTH);
        (nextPtr->value)[0] = '\0';
        nextPtr->next = NULL;
        nextPtr->prev = current;
        current->next = nextPtr;
    }
    return nextPtr;
}

struct Cell *prevCell(struct Cell *current)
{
    struct Cell *prevPtr = current->prev;
    if (prevPtr == NULL)
    {
        prevPtr = (struct Cell *)malloc(sizeof(struct Cell));
        prevPtr->value = (char *)malloc(sizeof(char) * MAX_SYMBOL_LENGTH);
        (prevPtr->value)[0] = '\0';
        prevPtr->next = current;
        prevPtr->prev = NULL;
        current->prev = prevPtr;
    }
    return prevPtr;
}

struct Cell *constructTape(char *initial)
{
    struct Cell *current = (struct Cell *)malloc(sizeof(struct Cell));
    current->value = (char *)malloc(sizeof(char) * MAX_SYMBOL_LENGTH);
    current->next = NULL;
    current->prev = NULL;
    for (int i = 0; i < strlen(initial); i++)
    {
        if (initial[i] != ' ')
        {
            current->value[0] = initial[i];
            current->value[1] = '\0';
        }
        current = nextCell(current);
    }
    return prevCell(current);
}

char *tapeToString(struct Cell *current, int shouldColorCurrent)
{
    struct Cell *initial = current;
    while (current->next != NULL)
    {
        current = current->next;
    }

    int count = 1;
    while (current->prev != NULL)
    {
        current = current->prev;
        count++;
    }

    char *changeToRed = "\033[0;31m";
    char *changeToBlack = "\033[0m";
    int size = sizeof(char) * (count * (MAX_SYMBOL_LENGTH - 1) + 1) + (shouldColorCurrent ? (strlen(changeToRed) + strlen(changeToBlack)) : 0);
    char *result = (char *)malloc(size);
    int i = 0;
    while (current->next != NULL)
    {
        if (shouldColorCurrent != 0 && (current == initial))
        {
            strcpy(result + i, changeToRed);
            i += strlen(changeToRed);
            if (current->value[0] == '\0')
            {
                result[i++] = '_';
            }
        }
        strcpy(result + i, current->value);
        i += strlen(current->value);
        if (shouldColorCurrent != 0 && (current == initial))
        {
            strcpy(result + i, changeToBlack);
            i += strlen(changeToBlack);
        }

        current = current->next;
    }
    result[i] = '\0';

    return result;
}

void freeCell(struct Cell* cell) {
    free(cell->value);
    free(cell);
}

void freeTape(struct Cell *current)
{
    while (current->next != NULL)
    {
        current = current->next;
    }

    while (current->prev != NULL)
    {
        struct Cell *old = current;
        current = current->prev;
        freeCell(old);
    }

    freeCell(current);

    return;
}