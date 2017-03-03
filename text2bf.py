from sys import argv
from os import path

debug = False

class Encode(object):
    """Text goes in, code comes out"""
    def __init__(self, speech):
        self.input = [ord(c) for c in speech]
        self.length = len(speech)
        self.output = []

    def _get_least(self, num):
        """Returns the minimum multiples of num"""
        cases = [num + 1, 1, num]
        for x in range(2, num // 2 + 1):
            if num % x == 0:
                comp = x + num // x
                if comp < cases[0]:
                    cases = [comp, x, comp - x]
        return cases[1:]

    def _count(self, begin):
        """Counts occurances of the current char"""
        for index in range(begin, self.length):
            if self.input[index] != self.input[begin]:
                return index - begin
        return self.length - begin

    def recode(self):
        for index in range(self.length):
            if index != 0:
                if self.input[index] == self.input[index - 1]:
                    continue
                diff = self.input[index] - self.input[index - 1]
                diff, neg = abs(diff), diff < 0
            else:
                diff, neg = self.input[index], False
            mult = self._get_least(diff)
            append = mult[0] == 1 and mult[1] != 1
            if append:
                mult = self._get_least(diff - 1)
            if diff == 1:
                if neg:
                    self.output.append(">-")
                else:
                    self.output.append(">+")
            else:
                self.output.append("{}{}".format("+" * mult[0], "[>"))
                if neg:
                    self.output.append("-" * mult[1])
                    self.output.append("<-]>")
                    if append:
                        self.output.append("-")
                else:
                    self.output.append("+" * mult[1])
                    self.output.append("<-]>")
                    if append:
                        self.output.append("+")
            self.output.append("{}<".format("." * self._count(index)))
            if debug:
                self.output.append("{}\n".format(chr(self.input[index])))
        self.output = "".join(self.output)
        self.output = self.output[:self.output.rfind(".") + 1]
        return self.output.replace("<>", "")

if __name__ == "__main__":
    if len(argv) == 1:
        encoder = Encode(input("Text: "))
        name = "out.b"
    else:
        with open(argv[1], "rb") as input_text:
            text = input_text.read()
        text = text.decode(encoding="ASCII", errors="ignore")
        encoder = Encode(text)
        name = path.splitext(path.split(argv[1])[-1])[0] + ".b"
    out = encoder.recode()
    with open(name, "w") as output_text:
        output_text.write(out)
