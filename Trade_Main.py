import pygame
import random
import math
from enum import Enum

###########################
###-ENUMS-###
###########################
class Shape(Enum):
    CIRCLE = 1
    SQUARE = 2
    HEX = 3
    LINE = 4

class TradeTypes(Enum):
    ALL = 1
    INDUSTRIAL = 2
    HIGH_TECH = 3
    AGRICULTURE = 4
    WATER_WORLD = 5
    ICE_CAPPED = 6
    ASTEROID = 7
    GARDEN = 8
    HIGH_POP = 9
    DESERT = 10
    FLUID_OCEANS = 11
    LOW_POP = 12
    NON_INDUSTRIAL = 13


###########################
###-CLASSES-###
###########################


class Cargo:
    Tonnage = 0

class CargoMail(Cargo):
    origin = ""
    destination = ""
    worth = 0
    stringList = []

class CargoGeneric(Cargo):
    origin = ""
    destination = ""
    worth = 0

class UIObject:
    posX = 0
    posY = 0
    size = 0
    name = ""
    enableName = False
    color = ""
    shape = Shape.CIRCLE


    def __init__(self, posX, posY, size, name, color, shape = Shape.CIRCLE):
        self.posX = posX
        self.posY = posY
        self.size = size
        self.name = name
        self.color = color
        self.shape = shape

class Line(UIObject):
    startPosX = 0
    startPosY = 0
    endPosX = 0
    endPosY = 0
    shape = Shape.LINE
    def __init__(self, startPosX, startPosY, endPosX, endPosY, color):
        self.startPosX = startPosX
        self.startPosY = startPosY
        self.endPosX = endPosX
        self.endPosY = endPosY
        self.color = color

class Ship(UIObject):
    startPosX = 0
    startPosY = 0
    destinationPosX = 0
    destinationPosY = 0
    startTime = 0

    jumpRange = 0

    tonnage = 0
    currentMoney = 0
    currentCargo = []


    def __init__(self, posX, posY, size = 3, name = "ship", color = "blue", shape = Shape.CIRCLE):
        self.posX = posX
        self.posY = posY
        self.startPosX = posX
        self.startPosY = posY
        self.size = size
        self.name = name
        self.color = color
        self.shape = shape
        self.currentCargo = []

class System(UIObject):
    hexNumX = 0
    hexNumY= 0
    shipsInSystem = []
    def __init__(self, posX, posY, size = 10, name = "system", color = "grey", shape = Shape.CIRCLE):
        self.posX = posX
        self.posY = posY
        self.size = size
        self.name = name
        self.color = color
        self.shape = shape
        self.shipsInSystem = []

class Hex(UIObject):
    shape = Shape.HEX
    hexNumX = 0
    hexNumY= 0
    hexCenterX = 0
    hexCenterY = 0
    points = []
    systemAssigned = False
    system = System(0,0)

    def __init__(self, hexNumX, hexNumY, color = "white"):
        self.color = color
        self.hexNumX = hexNumX
        self.hexNumY = hexNumY
        self.points = []
        self.systemAssigned = False
        self.system = System(0,0)

###########################
###-GLOBALS-###
###########################
global waitBetweenShipGen; waitBetweenShipGen = 1
global shipGenCountdown; shipGenCountdown = waitBetweenShipGen
global numShipsDuringGen; numShipsDuringGen = 5
global chanceToSpawnShip; chanceToSpawnShip = 3
global gameTime; gameTime = 0
global gameDay; gameDay = 4 #Every X seconds is 1 day
global systemTravelTime; systemTravelTime = 7 #It takes 7 days to get from one system to another, regardless of distance.

global hexSize; hexSize = 20
global major_radius; major_radius = hexSize / math.cos(math.radians(30))
global hexOffsetX; hexOffsetX = major_radius
global hexOffsetY; hexOffsetY = hexSize
global hexGridX; hexGridX = 16
global hexGridY; hexGridY = 20

global numberOfSystems; numberOfSystems = 75

#######################
##-Global roll chart-##
#######################
global shipJumpRangeChart; shipJumpRangeChart = [2,2,2,2,2,2,2,3,3,3,3,3,3,4,4,4,5,5,6]

global maxShips; maxShips = 30
global dt; dt = 0.0
pygame.init()
pygame.font.init()
global gameFont; gameFont = pygame.font.SysFont("Aptos", 20)
global screen; screen = pygame.display.set_mode((1500, 1000))
global clock; clock = pygame.time.Clock()
global tradeChart; tradeChart = {
    "Common Electronics": ["ALL"]
}

###########################
###-FUNCTIONS-###
###########################

def genHexes():
    hexes = []

    #cols = int(800 / (1.5 * hexSize)) + 2
    #rows = int(800 / (math.sqrt(3) * hexSize)) + 2


    hex_width = 2 * major_radius
    hex_height = hexSize * 2
    horiz_spacing = 3/4 * hex_width
    vert_spacing = hex_height



    for row in range(hexGridX):
        for col in range(hexGridY):
            hex = Hex(row, col)
            x = (col * horiz_spacing) + hexOffsetX
            y = (row * vert_spacing) + hexOffsetY
            if col % 2 == 1:
                y += vert_spacing / 2

            for i in range(6):
                angle_deg = 60 * i
                angle_rad = math.radians(angle_deg)
                px = x + major_radius * math.cos(angle_rad)
                py = y + major_radius * math.sin(angle_rad)
                hex.points.append((px, py))
            hex.hexCenterX = x
            hex.hexCenterY = y
            hexes.append(hex)
    return hexes


def genSystems(listHexes):
    listSystems = []

    nato_phonetic_alphabet = [
    "Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot",
    "Golf", "Hotel", "India", "Juliett", "Kilo", "Lima",
    "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo",
    "Sierra", "Tango", "Uniform", "Victor", "Whiskey", "X-ray",
    "Yankee", "Zulu"]

    for i in range(numberOfSystems):
        systemAssigned = False
        while(not systemAssigned):
            j = random.randrange(0,len(listHexes))
            if listHexes[j].systemAssigned == False:
                system = System(listHexes[j].hexCenterX,listHexes[j].hexCenterY, name = f"{nato_phonetic_alphabet[i%len(nato_phonetic_alphabet)]} {nato_phonetic_alphabet[i//len(nato_phonetic_alphabet)]}")
                systemAssigned = True
                system.hexNumX = listHexes[j].hexNumX
                system.hexNumY = listHexes[j].hexNumY
                listHexes[j].systemAssigned = True
                listHexes[j].system = system

        listSystems.append(system)
    return listSystems

#ships, systems
def genShips(listSystems):
    ship_names = ["Star Voyager", "Nebula Explorer", "Galactic Cruiser", "Cosmic Odyssey", "Solar Wind",
                  "Lunar Pioneer", "Stellar Horizon", "Celestial Navigator", "Quantum Leap", "Eclipse Runner",
                  "Infinity Seeker", "Astral Nomad", "Comet Chaser", "Meteor Drifter", "Planetary Rover",
                  "Galaxy Wanderer", "Orbit Raider", "Space Adventurer", "Nebula Drifter", "Starlight Glider",
                  "Cosmos Voyager", "Asteroid Hunter", "Solaris Explorer", "Lunar Pathfinder", "Stellar Seeker",
                  "Celestial Voyager", "Quantum Explorer", "Eclipse Chaser", "Infinity Voyager", "Astral Explorer"]

    for i in range(maxShips):
        systemIndex = random.randrange(len(listSystems))
        shipCreation = Ship(listSystems[systemIndex].posX,listSystems[systemIndex].posY, name = ship_names[random.randrange(len(ship_names))])
        shipCreation.currentMoney = random.randrange(100000,1000000)
        shipCreation.tonnage = random.randrange(10,4000,5)
        shipCreation.jumpRange = shipJumpRangeChart[random.randrange(len(shipJumpRangeChart))]
        listSystems[systemIndex].shipsInSystem.append(shipCreation)
        print(f"Ship: {shipCreation.name} created at {listSystems[systemIndex].name}. Cargo: {shipCreation.tonnage}, Money: {str(shipCreation.currentMoney)}, Jump: {shipCreation.jumpRange}")

    ##global shipGenCountdown
    ##shipGenCountdown = shipGenCountdown - dt
    ##if (shipGenCountdown <= 0):
    ##    if (random.randrange(chanceToSpawnShip) == 0): #Only spawn when the dice roll 0
    ##        systemIndexes = list(range(0, len(listSystems))) # gen a list of all systems currently in play
    ##        random.shuffle(systemIndexes) #Shuffle, as to not just spawn ships at planet 0 heading off to planet 1
    ##        startSystemIndex = systemIndexes.pop()
    ##        endSystemIndex = systemIndexes.pop()
##
    ##        shipCreation = Ship(listSystems[startSystemIndex].posX,listSystems[startSystemIndex].posY, name = ship_names[random.randrange(len(ship_names))])
    ##        shipCreation.endPosX = listSystems[endSystemIndex].posX
    ##        shipCreation.endPosY = listSystems[endSystemIndex].posY
    ##        shipCreation.startTime = gameTime
    ##        shipCreation.enableName = True
##
    ##        list_initialShips.append(shipCreation)
##
    ##        print(shipCreation.name + " created. From: " + listSystems[startSystemIndex].name + " To: " + listSystems[endSystemIndex].name)
    ##    shipGenCountdown = waitBetweenShipGen

def moveShips(listShips):
    shipsToRemove = []
    for ship in listShips:
        percentToSystem = (gameTime - ship.startTime) / (gameDay * systemTravelTime)
        ship.posX = ship.startPosX + ((ship.endPosX - ship.startPosX) * percentToSystem)
        ship.posY = ship.startPosY + ((ship.endPosY - ship.startPosY) * percentToSystem)
        if (percentToSystem >= 1):
            print(ship.name + " arrived at its destination")
            shipsToRemove.append(ship)
    for ship in shipsToRemove:
        listShips.remove(ship)

def drawUI(UIElements):
    for UIElement in UIElements:
        pos = pygame.Vector2(UIElement.posX,UIElement.posY)
        if UIElement.shape == Shape.CIRCLE:
            pygame.draw.circle(screen, UIElement.color, pos, UIElement.size)
        if UIElement.shape == Shape.SQUARE:
            pygame.draw.square(screen, "red", pos, UIElement.size)
        if UIElement.shape == Shape.HEX:
            pygame.draw.polygon(screen, "white", UIElement.points, 2)
        if UIElement.shape == Shape.LINE:
             pygame.draw.line(screen, "yellow", pygame.Vector2(UIElement.startPosX,UIElement.startPosY),pygame.Vector2(UIElement.endPosX,UIElement.endPosY))
        if UIElement.enableName:
            text = gameFont.render(UIElement.name, False, "white")
            screen.blit(text,(UIElement.posX,UIElement.posY + 20))

        if isinstance(UIElement,Ship):
            startPos = pygame.Vector2(UIElement.startPosX, UIElement.startPosY)
            endPos = pygame.Vector2(UIElement.posX,UIElement.posY)
            pygame.draw.line(screen, "blue", startPos, endPos)

def convertToGrid(listHexes):
    hexGrid = [[False for _ in range(hexGridY)] for _ in range(hexGridX)]
    for hex in listHexes:
        if hex.systemAssigned == True:
            hexGrid[hex.hexNumX][hex.hexNumY] = True
    return hexGrid

def minDistance(point1,point2):
    return math.sqrt(((point2[0]-point1[0])* (point2[0]-point1[0])) + ((point2[1]-point1[1])* (point2[1]-point1[1])))

def getNeighbors(hexGrid,current):
    neighbors = []
    possibleNeighbors = []
    if current[0] % 2 == 0: #Even
        possibleNeighbors = [[current[0],current[1] - 1],[current[0],current[1] + 1],[current[0]+1,current[0] - 1],[current[0]-1,current[0] - 1],[current[0]+1,current[0]],[current[0]-1,current[0]]]
    if current[0] % 2 == 1: #Odd
        possibleNeighbors = [[current[0],current[1] - 1],[current[0],current[1] + 1],[current[0]+1,current[0] + 1],[current[0]-1,current[0] + 1],[current[0]+1,current[0]],[current[0]-1,current[0]]]
    for possibleNeighbor in possibleNeighbors:
        print(possibleNeighbor[0])
        if (possibleNeighbor[0] >= 0) and (possibleNeighbor[0] < hexGridX):
            if (possibleNeighbor[1] >= 0) and (possibleNeighbor[1] < hexGridY):
                print(hexGrid[possibleNeighbor[0]][possibleNeighbor[1]])
                if hexGrid[possibleNeighbor[0]][possibleNeighbor[1]] == True:
                    neighbors.append(possibleNeighbor)
    return neighbors



def navigatePath(start, end, hexGrid):
    #https://en.wikipedia.org/wiki/A*_search_algorithm Pseudocode
    openSet = [start]
    cameFrom = []
    gScore = {}
    gScore[f"{start[0]}_{start[1]}"] = 0
    fScore = {}
    fScore[f"{start[0]}_{start[1]}"] = minDistance(start,end)

    while len(openSet) > 0:
        lowestOpenSet = openSet[0]
        for openItem in openSet:
            if fScore[f"{openItem[0]}_{openItem[1]}"] < fScore[f"{lowestOpenSet[0]}_{lowestOpenSet[1]}"]:
                lowestOpenSet = openItem
        current = lowestOpenSet

        if current == end:
            return cameFrom
            return reconstruct_path(cameFrom, current)
        openSet.remove(current)
        neighbors = getNeighbors(hexGrid,current) #note, will have to account for
        for neighbor in neighbors:
            tentative_gScore = gScore[current] + 1 #note, will have to change to weight in 'jumps'
            neighborString = f"{neighbor[0]}_{neighbor[1]}"
            if (neighborString not in gScore.keys):
                gScore[neighborString] = 99999999
            if (tentative_gScore < gScore[neighborString]):
                cameFrom[neighborString].append(current)
                gScore[neighborString] = tentative_gScore
                fScore[neighborString] = tentative_gScore + minDistance(neighbor,end)
                if neighbor not in openSet:
                    openSet.append(neighbor)

    return False


###########################
###-MAIN-###
###########################

def main():
    global dt
    global gameTime
    # pygame setup
    running = True

    player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    listHexes = genHexes()
    listSystems = genSystems(listHexes)
    listHexGrid = convertToGrid(listHexes)
    genShips(listSystems)
    listShipsFlying = []
    listLines = []
    startPosX = listSystems[0].posX
    startPosY = listSystems[0].posY
    endPosX = listSystems[1].posX
    endPosY = listSystems[1].posY

    line = Line(startPosX, startPosY, endPosX, endPosY, "yellow")
    listLines.append(line)
    text = gameFont.render("Test 1", False, "white")

    print(navigatePath([listSystems[0].hexNumX,listSystems[0].hexNumY], [listSystems[1].hexNumX,listSystems[1].hexNumY], listHexGrid))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # fill the screen with a color to wipe away anything from last frame
        screen.fill("black")

        # RENDER YOUR GAME HERE

        #keys = pygame.key.get_pressed()
        #if keys[pygame.K_w]:
        #    player_pos.y -= 300 * dt
        #if keys[pygame.K_s]:
        #    player_pos.y += 300 * dt
        #if keys[pygame.K_a]:
        #    player_pos.x -= 300 * dt
        #if keys[pygame.K_d]:
        #    player_pos.x += 300 * dt

        #listShipsFlying =

        moveShips(listShipsFlying)
        drawUI(listHexes)
        drawUI(listSystems)
        drawUI(listShipsFlying)
        drawUI(listLines)
        # flip() the display to put your work on screen
        pygame.display.flip()
        dt = clock.tick(60) / 1000
        gameTime = gameTime + dt
    pygame.quit()

main()
