from sys import stdout, argv

class BFTape:
    def __init__(self, size):
        self.tapeRoll = [0] * size
        self.pointer = 0

    def getCurrent(self):
        return self.tapeRoll[self.pointer]

    def zero(self):
        self.tapeRoll[self.pointer] = 0

    def add(self, c):
        self.tapeRoll[self.pointer] += c

    def sub(self, c):
        self.tapeRoll[self.pointer] -= c

    def left(self, c):
        self.pointer -= c

    def right(self, c):
        self.pointer += c

    def out(self):
        stdout.write(chr(self.tapeRoll[self.pointer]))
        stdout.flush()

class BFFile:
    def __init__(self, file):
        with open(file) as input:
            self.inputFile = input.read().replace("[-]", "!")
        self.length = len(self.inputFile)
        self.indexes = [1] * self.length
        self.pointer = 0
        self.concatFile()

    def _count(self, begin):
        for index in range(begin, self.length):
            if self.inputFile[index] != self.inputFile[begin]:
                return index - begin
        return self.length - begin

    def _find_end(self, begin):
        index = begin + 1
        while index < self.length:
            if self.inputFile[index] == ']':
                return index - begin
            elif self.inputFile[index] == '[':
                index += self._find_end(index)
            index += 1

    def concatFile(self):
        for index in range(self.length):
            if self.inputFile[index] == '[':
                self.indexes[index] = self._find_end(index)
                self.indexes[index + self.indexes[index]] = self.indexes[index]
            elif self.inputFile[index] in ['+', '-', '<', '>']:
                self.indexes[index] = self._count(index)

    def getChar(self):
        return self.inputFile[self.pointer]

    def movePointer(self, distance):
        self.pointer += distance

    def getOffset(self):
        return self.indexes[self.pointer]

    def isEnd(self):
        return self.pointer == self.length

if __name__ == "__main__":
    if (len(argv) == 0):
        print("Usage: {} filename.b".format(argv[0]))
        exit()

    file = BFFile(argv[1])
    tape = BFTape(30000)

    while not file.isEnd():
        current = file.getChar()

        if current == '>':
            tape.right(file.getOffset())
            file.movePointer(file.getOffset())

        elif current == '+':
            tape.add(file.getOffset())
            file.movePointer(file.getOffset())

        elif current == '<':
            tape.left(file.getOffset())
            file.movePointer(file.getOffset())

        elif current == ']':
            if tape.getCurrent() != 0:
                file.movePointer(1 - file.getOffset())
            else:
                file.movePointer(1)

        elif current == '-':
            tape.sub(file.getOffset())
            file.movePointer(file.getOffset())

        elif current == '!':
            tape.zero()
            file.movePointer(file.getOffset())

        elif current == '[':
            if tape.getCurrent() == 0:
                file.movePointer(file.getOffset() + 1)
            else:
                file.movePointer(1)

        elif current == '.':
            tape.out()
            file.movePointer(file.getOffset())

        else:
            file.movePointer(file.getOffset())
