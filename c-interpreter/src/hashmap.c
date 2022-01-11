#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "params.h"
#include "hashmap.h"

struct HashMap *newHashMap(int size)
{
    struct HashMap *ptr = (struct HashMap *)malloc(sizeof(struct HashMap));
    ptr->size = size;
    ptr->array = (struct HashMapLL **)malloc(sizeof(struct HashMapLL *) * size);
    for (int i = 0; i < size; i++)
    {
        (ptr->array)[i] = NULL;
    }
    return ptr;
}

unsigned int hash(char *key, int size)
{

    unsigned int h = 5381;
    for (int i = 0; i < strlen(key); i++)
    {
        h += (h << 5) + ((const unsigned char *)key)[i];
    }

    return h & (size - 1);
}

void hashMapPut(struct HashMap *hashMap, char *key, void *value)
{
    unsigned int keyHash = hash(key, hashMap->size);
    struct HashMapLL *llPtr = hashMap->array[keyHash];
    if (llPtr == NULL)
    {
        hashMap->array[keyHash] = (struct HashMapLL *)malloc(sizeof(struct HashMapLL));
        llPtr = hashMap->array[keyHash];
        llPtr->next = NULL;
        llPtr->key = (char *)malloc(strlen(key) + 1);
        strcpy(llPtr->key, key);
    }
    else
    {
        while (strcmp(llPtr->key, key) != 0)
        {
            if (llPtr->next == NULL)
            {
                llPtr->next = (struct HashMapLL *)malloc(sizeof(struct HashMapLL));
                llPtr = llPtr->next;
                llPtr->next = NULL;
                llPtr->key = (char *)malloc(strlen(key) + 1);
                strcpy(llPtr->key, key);
                break;
            }
            llPtr = llPtr->next;
        }
    }

    llPtr->value = value;

    return;
}

void *hashMapGet(struct HashMap *hashMap, char *key)
{
    unsigned int keyHash = hash(key, hashMap->size);
    struct HashMapLL *llPtr = hashMap->array[keyHash];
    if (llPtr == NULL)
    {
        return NULL;
    }
    while (strcmp(llPtr->key, key) != 0)
    {
        if (llPtr->next == NULL)
        {
            return NULL;
        }
        llPtr = llPtr->next;
    }
    return llPtr->value;
}