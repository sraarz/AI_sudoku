import random
import numpy as np
import math 
from random import choice
import statistics 
import ast
import json 


def GUI(sudoku):
    print("\n")
    for i in range(len(sudoku)):
        line = ""
        if i == 3 or i == 6:
            print("---------------------")
        for j in range(len(sudoku[i])):
            if j == 3 or j == 6:
                line += "| "
            line += str(sudoku[i,j])+" "
        print(line)


def FixSudokuValues(fixed_value):
    for i in range (0,9):
        for j in range (0,9):
            if fixed_value[i,j] != 0:
                fixed_value[i,j] = 1
    
    return(fixed_value)
  
def RowColumnErrorNum(row, column, sudoku):
    numberOfErrors = (9 - len(np.unique(sudoku[:,column]))) + (9 - len(np.unique(sudoku[row,:])))
    return(numberOfErrors)

def ErrorsNum(sudoku):
    numberOfErrors = 0 
    for i in range (0,9):
        numberOfErrors += RowColumnErrorNum(i ,i ,sudoku)
    return(numberOfErrors)


def Create3x3BlocksList ():
    finalListOfBlocks = []
    for r in range (0,9):
        tmpList = []
        block1 = [i + 3*((r)%3) for i in range(0,3)]
        block2 = [i + 3*math.trunc((r)/3) for i in range(0,3)]
        for x in block1:
            for y in block2:
                tmpList.append([x,y])
        finalListOfBlocks.append(tmpList)
    return(finalListOfBlocks)

def Fill3x3Blocks(sudoku, listOfBlocks):
    for block in listOfBlocks:
        for box in block:
            if sudoku[box[0],box[1]] == 0:
                currentBlock = sudoku[block[0][0]:(block[-1][0]+1),block[0][1]:(block[-1][1]+1)]
                sudoku[box[0],box[1]] = choice([i for i in range(1,10) if i not in currentBlock])
    return sudoku

def SumOfOneBlock (sudoku, oneBlock):
    finalSum = 0
    for box in oneBlock:
        finalSum += sudoku[box[0], box[1]]
    return(finalSum)

def RandomBoxes(fixed_value, block):
    while (1):
        firstBox = random.choice(block)
        secondBox = choice([box for box in block if box is not firstBox ])

        if fixed_value[firstBox[0], firstBox[1]] != 1 and fixed_value[secondBox[0], secondBox[1]] != 1:
            return([firstBox, secondBox])

def FlipBoxes(sudoku, boxesToFlip):
    proposedSudoku = np.copy(sudoku)
    placeHolder = proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]]
    proposedSudoku[boxesToFlip[0][0], boxesToFlip[0][1]] = proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]]
    proposedSudoku[boxesToFlip[1][0], boxesToFlip[1][1]] = placeHolder
    return (proposedSudoku)

def StateGenerator (sudoku, fixed_value, listOfBlocks):
    randomBlock = random.choice(listOfBlocks)
    while(SumOfOneBlock(fixed_value, randomBlock) > 8):
      randomBlock = random.choice(listOfBlocks)
    boxesToFlip = RandomBoxes(fixed_value, randomBlock)
    proposedSudoku = FlipBoxes(sudoku,  boxesToFlip)
    return([proposedSudoku, boxesToFlip])

def NewState (currentSudoku, fixed_value, listOfBlocks, sigma):
    proposal = StateGenerator(currentSudoku, fixed_value, listOfBlocks)
    newSudoku = proposal[0]
    boxesToCheck = proposal[1]
    currentCost = RowColumnErrorNum(boxesToCheck[0][0], boxesToCheck[0][1], currentSudoku) + RowColumnErrorNum(boxesToCheck[1][0], boxesToCheck[1][1], currentSudoku)
    newCost = RowColumnErrorNum(boxesToCheck[0][0], boxesToCheck[0][1], newSudoku) + RowColumnErrorNum(boxesToCheck[1][0], boxesToCheck[1][1], newSudoku)

    costDifference = newCost - currentCost
    rho = math.exp(-costDifference/sigma)
    if(np.random.uniform(1,0,1) < rho):
        return([newSudoku, costDifference])
    return([currentSudoku, 0])


def NumOfItterations(fixed_value):
    numberOfItterations = 0
    for i in range (0,9):
        for j in range (0,9):
            if fixed_value[i,j] != 0:
                numberOfItterations += 1
    return numberOfItterations

def InitialSigma (sudoku, fixed_value, listOfBlocks):
    listOfDifferences = []
    tmpSudoku = sudoku
    for i in range(1,10):
        tmpSudoku = StateGenerator(tmpSudoku, fixed_value, listOfBlocks)[0]
        listOfDifferences.append(ErrorsNum(tmpSudoku))
    return (statistics.pstdev(listOfDifferences))


def solveSudoku (sudoku):
    solutionFound = 0
    while (solutionFound == 0):
        decreaseFactor = 0.99
        stuckCount = 0
        fixedSudoku = np.copy(sudoku)
        GUI(sudoku)
        FixSudokuValues(fixedSudoku)
        listOfBlocks = Create3x3BlocksList()
        tmpSudoku = Fill3x3Blocks(sudoku, listOfBlocks)
        sigma = InitialSigma(sudoku, fixedSudoku, listOfBlocks)
        score = ErrorsNum(tmpSudoku)
        itterations = NumOfItterations(fixedSudoku)
        if score <= 0:
            solutionFound = 1

        while solutionFound == 0:
            previousScore = score
            for i in range (0, itterations):
                newState = NewState(tmpSudoku, fixedSudoku, listOfBlocks, sigma)
                tmpSudoku = newState[0]
                scoreDiff = newState[1]
                score += scoreDiff
                print(score)
                if score <= 0:
                    solutionFound = 1
                    break

            sigma *= decreaseFactor
            if score <= 0:
                solutionFound = 1
                break
            if score >= previousScore:
                stuckCount += 1
            else:
                stuckCount = 0
            if (stuckCount > 80):
                sigma += 2
            if(ErrorsNum(tmpSudoku)==0):
                GUI(tmpSudoku)
                break
    return(tmpSudoku)



class AI:
    # ^^^ DO NOT change the name of the class ***
    def __init__(self):
        pass

    # the solve function takes a json string as input
    # and outputs the solved version as json
    def solve(self, problem):
        # ^^^ DO NOT change the solve function above ***

        problem_data = json.loads(problem)
        # ^^^ DO NOT change the problem_data above ***

        sudoku_list =  problem_data['sudoku']
        sudoku = np.array(sudoku_list)

        # TODO implement your code here
        solution = solveSudoku(sudoku)
        print(ErrorsNum(solution))
        x = ast.literal_eval(str(solution).replace(' ',','))
        d = {}
        d.update({"sudoku":x})
        sudoku = json.dumps(d)
        GUI(solution)
        # finished is the solved version
        return sudoku


if __name__ == "__main__":
    input = """{
      "sudoku": [
          [1,0,4, 8,6,5, 2,3,7],
          [7,0,5, 4,1,2, 9,6,8],
          [8,0,2, 3,9,7, 1,4,5],
          [9,0,1, 7,4,8, 3,5,6],
          [6,0,8, 5,3,1, 4,2,9],
          [4,0,3, 9,2,6, 8,7,1],
          [3,0,9, 6,5,4, 7,1,2],
          [2,0,6, 1,7,9, 5,8,3],
          [5,0,7, 2,8,3, 6,9,4]
      ]
  }"""

    harder_input = """{
      "sudoku": [
          [0,2,4, 0,0,7, 0,0,0],
          [6,0,0, 0,0,0, 0,0,0],
          [0,0,3, 6,8,0, 4,1,5],
          [4,3,1, 0,0,5, 0,0,0],
          [5,0,0, 0,0,0, 0,3,2],
          [7,9,0, 0,0,0, 0,6,0],
          [2,0,9, 7,1,0, 8,0,0],
          [0,4,0, 0,9,3, 0,0,0],
          [3,1,0, 0,0,4, 7,5,0]
      ]
  }"""
    ai = AI()
    ai.solve(input)
