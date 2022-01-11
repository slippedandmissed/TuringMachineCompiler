#pragma once
#include <stdint.h>
#include "parse.h"

struct HashMapLL
{
    char *key;
    void *value;
    struct HashMapLL *next;
};

struct HashMap
{
    struct HashMapLL **array;
    int size;
};

struct HashMap *newHashMap(int);

void hashMapPut(struct HashMap *, char *, void *);

void *hashMapGet(struct HashMap *, char *);