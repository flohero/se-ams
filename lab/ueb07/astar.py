import heapq
import random
import time
from collections import deque

random.seed(42)


class TileGameState:
    def __init__(self, n, copyFlag=None):
        if (copyFlag != None):
            old = n
            self.n = old.n
            self.freeX = old.freeX
            self.freeY = old.freeY
            self.data = [[old.data[x][y] for y in range(old.n)] for x in range(old.n)]
        else:
            l = [x for x in range(n * n - 1)]
            self.n = n
            self.freeX = n - 1
            self.freeY = n - 1
            invCount = 0
            if n != 1:
                while invCount == 0 or invCount % 2 == 1:
                    invCount = 0
                    random.shuffle(l)
                    for i in range(n * n - 2):
                        for j in range(i + 1, n * n - 1):
                            if l[i] > l[j]:
                                invCount = invCount + 1
            self.data = [[l[x * n + y] if x * n + y < n * n - 1 else None for y in range(n)] for x in range(n)]

    def draw(self):
        print("\n".join(["\t".join([str(val if val != None else "_") for val in row]) for row in self.data]) + "\n")

    def copy(self):
        return TileGameState(self, True)

    def moveRight(self):
        t = self.data[self.freeX - 1][self.freeY]
        self.data[self.freeX - 1][self.freeY] = None
        self.data[self.freeX][self.freeY] = t
        self.freeX = self.freeX - 1

    def moveLeft(self):
        t = self.data[self.freeX + 1][self.freeY]
        self.data[self.freeX + 1][self.freeY] = None
        self.data[self.freeX][self.freeY] = t
        self.freeX = self.freeX + 1

    def moveUp(self):
        t = self.data[self.freeX][self.freeY + 1]
        self.data[self.freeX][self.freeY + 1] = None
        self.data[self.freeX][self.freeY] = t
        self.freeY = self.freeY + 1

    def moveDown(self):
        t = self.data[self.freeX][self.freeY - 1]
        self.data[self.freeX][self.freeY - 1] = None
        self.data[self.freeX][self.freeY] = t
        self.freeY = self.freeY - 1

    def getMovedBoards(self):
        moves = []
        if self.freeX > 0:  # move a tile to the right
            g = self.copy()
            g.moveRight()
            moves.append(g)
        if self.freeX < self.n - 1:  # move a tile to the left
            g = self.copy()
            g.moveLeft()
            moves.append(g)
        if self.freeY < self.n - 1:  # move a tile up
            g = self.copy()
            g.moveUp()
            moves.append(g)
        if self.freeY > 0:  # move a tile down
            g = self.copy()
            g.moveDown()
            moves.append(g)
        return moves

    def isSolved(self):
        for i in range(self.n):
            for j in range(self.n):
                v = self.data[i][j]
                if v != None and v != i * self.n + j:
                    return False
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if other.n != self.n or other.freeX != self.freeX or other.freeY != self.freeY:
                return False
            for i in range(self.n):
                for j in range(self.n):
                    if self.data[i][j] != other.data[i][j]:
                        return False
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.n, self.freeX, self.freeY, frozenset([frozenset(row) for row in self.data])))


class transition:
    def __init__(self, key, heuristic):
        self.key = key
        self.value = heuristic(key)

    def __lt__(self, other):
        return self.value < other.value

    def __str__(self):
        return f"{self.key} -> {self.value}"


def DFS(gameState):
    if gameState.isSolved():
        print("DFS nr of moves: 0")
        return gameState
    stack = list()
    stack.append(gameState)
    handled = set()
    handled.add(gameState)
    moves = 0
    while len(stack) > 0:
        board = stack.pop()
        moves += 1
        for state in board.getMovedBoards():
            if state in handled:
                continue
            if state.isSolved():
                print("# moves:", moves)
                return state
            stack.append(state)
            handled.add(state)
    return None


def BFS(gameState):
    if gameState.isSolved():
        return gameState
    q = deque()
    q.append(gameState)
    handled = set()
    handled.add(gameState)
    moves = 0
    while len(q) > 0:
        board = q.popleft()
        moves += 1
        for state in board.getMovedBoards():
            if state in handled:
                continue
            if state.isSolved():
                print("# of moves:", moves)
                return state
            q.append(state)
            handled.add(state)
    return None


def AStar(game, h):
    if game.isSolved():
        return game
    heap = list()
    heapq.heappush(heap, transition(game, h))
    handled = set()
    handled.add(game)
    moves = 0
    while len(heap) > 0:
        board = heapq.heappop(heap).key
    moves += 1
    for state in board.getMovedBoards():
        if state.isSolved():
            print("# moves:", moves)
            return state
        if state in handled:
            continue
        heapq.heappush(heap, transition(state, h))
        handled.add(state)
    return None


def manhatten_distance(state: TileGameState):
    dist = 0
    for i in range(state.n):
        for j in range(state.n):
            val = state.data[i][j]
            if val is None:
                continue
            val += 1
            col_dist = val % state.n - j
            row_dist = val / state.n - i
            dist += abs(col_dist) + abs(row_dist)
    return dist


def average_of_ten(name, func):
    print(name)
    testruns = 10
    for i in range(1, 4):
        total = 0
        for j in range(testruns):
            game = TileGameState(i)
            game.draw()
            start = time.time()
            func(game)
            end = time.time()
            total += end - start
        avg = total / testruns
        print(name, "took: ", str(avg), f" in average for a {i}x{i} puzzle")


if __name__ == "__main__":
    average_of_ten("DFS", DFS)
    average_of_ten("BFS", BFS)
    average_of_ten("A*", lambda g: AStar(g, manhatten_distance))
