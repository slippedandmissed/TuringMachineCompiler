#!/usr/bin/python3.9

import sys


tape = [""]
if len(sys.argv) > 2:
    tape = list(sys.argv[2])
    for i in range(len(tape)):
        if tape[i] == " ":
            tape[i] = ""

program = sys.argv[1]


state = "start"
currentIndex = 0

rules = {}

with open(program, encoding="utf-8") as transitionTable:
    data = [x.strip() for x in transitionTable.read().strip().split("\n") if not x.startswith("#")]
for index, i in enumerate(data):
    try:
        parts = i.split(" = ")
        oldState, read = parts[0][2:-1].split(",")
        write, arrow, newState = parts[1][1:-1].split(",")
        direction = "<" if arrow == "←" else ">"
        if oldState not in rules:
            rules[oldState] = {}
        rules[oldState][read] = [write, direction, newState]
    except:
        print("Mangled rule: '%s' on line %i" % (i, index+1))
        sys.exit()

currentRule = "Program terminated"
if state in rules:
    if tape[currentIndex] in rules[state]:
        write, direction, newState = rules[state][tape[currentIndex]]
        arrow = "←" if direction == "<" else "→"
        currentRule = "Δ(%s,%s) = (%s,%s,%s)" % (state, tape[currentIndex], write, arrow, newState)


def advance():
    global state
    global tape
    global currentRule
    global currentIndex
    if state in rules:
        if tape[currentIndex] in rules[state]:
            write, direction, newState = rules[state][tape[currentIndex]]
            transitioning = -1 if direction == "<" else 1
            arrow = "←" if direction == "<" else "→"
            state = newState
            tape[currentIndex] = write
            currentIndex += transitioning
            if currentIndex < 0:
                currentIndex += 1
                tape = [""] + tape
            if currentIndex >= len(tape):
                tape.append("")
            return True
    return False

stateWidth = 20

span = 20

change = True
while change:
    change = advance()

line = ""

for i, x in enumerate(tape):
    line += " " if x == "" else x

print(line.strip())
