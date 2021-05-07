#!/usr/bin/python3.9

import pygame
import time
import sys
from pygame.locals import *


pygame.init()

screenWidth,screenHeight = 1600, 900

screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("Turing Machine")

tape = [""]
if len(sys.argv) > 2:
    tape = list(sys.argv[2])
    for i in range(len(tape)):
        if tape[i] == " ":
            tape[i] = ""

boxSize = 100
transitionTime = 0.1

program = sys.argv[1]

font = pygame.font.SysFont("Courier", 30)

offset = 0
currentIndex = 0
if len(sys.argv) > 3:
    currentIndex = int(sys.argv[3])
startedTransitioningTime = 0
transitioning = 0
tapeLabels = list(font.render(x, 1, (0, 0, 0) ) for x in tape)
tapeLabelDict = {"": font.render("", 1, (0, 0, 0))}
for i, cell in enumerate(tape):
    if cell not in tapeLabelDict:
        tapeLabelDict[cell] = tapeLabels[i]

state = "start"

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
        pygame.quit()
        sys.exit()

currentRule = "Program terminated"
if state in rules:
    if tape[currentIndex] in rules[state]:
        write, direction, newState = rules[state][tape[currentIndex]]
        arrow = "←" if direction == "<" else "→"
        currentRule = "Δ(%s,%s) = (%s,%s,%s)" % (state, tape[currentIndex], write, arrow, newState)


manual = True

moveCount = 0

manualToggleLabel = font.render("Press SPACE to toggle manual mode", 1, (255, 0, 0))
manualLabel = font.render("MANUAL MODE - Press RETURN to advance", 1, (255, 0, 0))

def advance():
    global state
    global moveCount
    global startedTransitioningTime
    global transitioning
    global tapeLabels
    global tapeLabelDict
    global tape
    global font
    global currentRule
    if state in rules:
        if tape[currentIndex] in rules[state]:
            moveCount += 1
            write, direction, newState = rules[state][tape[currentIndex]]
            transitioning = -1 if direction == "<" else 1
            arrow = "←" if direction == "<" else "→"
            state = newState
            tape[currentIndex] = write
            if write not in tapeLabelDict:
                tapeLabelDict[write] = font.render(write, 1, (0, 0, 0))
            tapeLabels[currentIndex] = tapeLabelDict[write]
            startedTransitioningTime = time.time()


ruleLabelDict = {}
stateLabelDict = {}
speedLabelDict = {}

lastTime = time.time()
programStartTime = time.time()

view = 0
viewLabel = font.render("Press T to switch views", 1, (255, 0, 0))

rowCount = 10
miniBoxSize = 50
rowSpacing = 10

while True:
    boxCount = screenWidth//boxSize
    miniBoxCount = screenWidth//miniBoxSize
    boxCount += 4 if boxCount % 2 else 3
    deltaTime = time.time()-lastTime
    lastTime = time.time()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_SPACE:
                manual = not manual
                if not manual:
                    advance()
            elif event.key == K_t:
                view = 1-view
            elif event.key == K_LEFT:
                transitionTime += 0.05
            elif event.key == K_RIGHT:
                transitionTime -= 0.05
                if transitionTime <= 0:
                    transitionTime = 0.000000001
            if transitioning == 0:
                if event.key == K_RETURN and manual:
                    advance()

    screen.fill((255, 255, 255))

    screen.blit(manualToggleLabel, (screenWidth-manualToggleLabel.get_width()-10, 10))
    if manual:
        screen.blit(manualLabel, (screenWidth-manualLabel.get_width()-10, 20+manualToggleLabel.get_height()))
    if transitionTime not in speedLabelDict:
        speedLabelDict[transitionTime] = font.render("Speed: "+str(round(1/transitionTime, 3)), 1, (255, 0, 0))
    speedLabel = speedLabelDict[transitionTime]
    screen.blit(speedLabel, (screenWidth-speedLabel.get_width()-10,
                             30+manualToggleLabel.get_height()+manualLabel.get_height()))

    screen.blit(viewLabel, (screenWidth-viewLabel.get_width()-10,
                            40+manualToggleLabel.get_height()+manualLabel.get_height()+speedLabel.get_height()))
    
    if state not in stateLabelDict:
        stateLabelDict[state] = font.render("State: %s" % state, 1, (255, 0, 0))
    stateLabel = stateLabelDict[state]
    screen.blit(stateLabel, (10, 10))

    if currentRule not in ruleLabelDict:
        ruleLabelDict[currentRule] = font.render(currentRule, 1, (255, 0, 0))
    ruleLabel = ruleLabelDict[currentRule]
    screen.blit(ruleLabel, (10, screenHeight-ruleLabel.get_height()-10))

    if view == 0:
        y = (screenHeight-boxSize)//2

        for i in range(-boxCount//2, boxCount//2+1):
            x = (screenWidth-boxSize)//2 + i*boxSize + offset
            pygame.draw.rect(screen, (0, 0, 0), (x, y, boxSize, boxSize), 1)
            tapeIndex = i + currentIndex
            if 0 <= tapeIndex < len(tape):
                label = tapeLabels[tapeIndex]
                screen.blit(label, (x+(boxSize-label.get_width())//2, y+(boxSize-label.get_height())//2))
            pygame.draw.rect(screen, (0, 0, 255), ((screenWidth-boxSize)//2, y, boxSize, boxSize), 3)
    else:
        startY = 70+manualToggleLabel.get_height()+manualLabel.get_height()+speedLabel.get_height()+viewLabel.get_height()
        startX = (screenWidth-miniBoxCount*miniBoxSize)/2
        i = 0
        miniOffset = offset*(miniBoxSize/boxSize)
        for row in range(rowCount):
            for column in range(miniBoxCount):
                y = startY + row * (miniBoxSize + rowSpacing)
                x = startX + column * miniBoxSize
                if currentIndex == 0 and transitioning == -1:
                    pygame.draw.rect(screen, (0, 0, 0), (x+miniOffset, y, miniBoxSize, miniBoxSize), 1)
                    if column == miniBoxCount-1:
                        pygame.draw.rect(screen, (0, 0, 0), (startX-miniBoxSize+miniOffset,
                                                             y,
                                                             miniBoxSize,
                                                             miniBoxSize), 1)
                else:
                    pygame.draw.rect(screen, (0, 0, 0), (x, y, miniBoxSize, miniBoxSize), 1)
                if i < len(tape):
                    label = tapeLabels[i]
                    if currentIndex == 0 and transitioning == -1:
                        screen.blit(label, (x+(miniBoxSize-label.get_width())/2+miniOffset,
                                            y+(miniBoxSize-label.get_height())/2))
                        if column == miniBoxCount-1 and row < rowCount-1:
                            screen.blit(label, (startX-miniBoxSize+(miniBoxSize-label.get_width())/2+miniOffset,
                                                y+miniBoxSize+rowSpacing+(miniBoxSize-label.get_height())/2))
                    else:
                        screen.blit(label, (x+(miniBoxSize-label.get_width())/2,
                                            y+(miniBoxSize-label.get_height())/2))
                i += 1
        if currentIndex == 0 and transitioning == -1:
            pygame.draw.rect(screen, (0, 0, 255), (startX, startY, miniBoxSize, miniBoxSize), 3)
        elif currentIndex < miniBoxCount * rowCount:
            pygame.draw.rect(screen, (0, 0, 255), (startX+(currentIndex%miniBoxCount)*miniBoxSize-miniOffset,
                                                   startY+(currentIndex//miniBoxCount)*(miniBoxSize+rowSpacing),
                                                   miniBoxSize,
                                                   miniBoxSize), 3)
            if currentIndex%miniBoxCount == miniBoxCount-1 and currentIndex//miniBoxCount < rowCount-1:
                pygame.draw.rect(screen, (0, 0, 255), (startX-miniBoxSize-miniOffset,
                                                       startY+(currentIndex//miniBoxCount+1)*(miniBoxSize+rowSpacing),
                                                       miniBoxSize,
                                                       miniBoxSize), 3)
                
    if time.time()-programStartTime > transitionTime and moveCount == 0 and not manual:
        advance()

    transitionedFor = time.time()-startedTransitioningTime
    if transitionedFor >= transitionTime and transitioning != 0:
        offset = 0
        if currentIndex == 0 and transitioning == -1:
            tape = [""] + tape
            tapeLabels = [tapeLabelDict[""]] + tapeLabels
        else:
            currentIndex += transitioning
            if currentIndex == len(tape) and transitioning == 1:
                tape.append("")
                tapeLabels.append(tapeLabelDict[""])
        transitioning = 0
        currentRule = "Program terminated"
        if state in rules:
            if tape[currentIndex] in rules[state]:
                write, direction, newState = rules[state][tape[currentIndex]]
                arrow = "←" if direction == "<" else "→"
                currentRule = "Δ(%s,%s) = (%s,%s,%s)" % (state, tape[currentIndex], write, arrow, newState)

        if not manual:
            advance()
    else:
        offset = - transitioning * boxSize * transitionedFor //transitionTime
    
    pygame.display.update()