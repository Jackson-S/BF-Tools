#!/usr/bin/env python3

"""
    bf_translator.py
    Compiles brainfuck code into various other languages

    Supported (Tested version):
        * C (Clang 800.0.42.1, GCC 6.3.0_1)
        * Python (2.7.13 / 3.6.0)
        * Java (Java SE 1.8.0_112)
        * Rust (1.14.0)
        * Arduino

    Partially supported (Cannot take input):
        * C# (Mono 4.6.2)
        * Swift (3.0.1)
        * JavaScript (Safari 10.0.3)
        * Shell script (Bash 3.2) (Very slow)

    Likely to be buggy, code is only output, not compiled.
"""

import argparse
from re import sub
from os import path


class Converter(object):
    """Base class, extend and fill self.op in subclass to add a new language"""
    def __init__(self, code):
        # Removes any comments from the code leaving only valid bf chars
        self.code = self._parse_code(code)
        self.code = self._optimize(self.code)
        self.output = []
        self.status = {"position": 0, "spaces": ""}
        self.length = len(self.code)
        self.op = {"add": "",
                   "sub": "",
                   "left": "",
                   "right": "",
                   "in": "",
                   "out": "",
                   "loop_begin": "",
                   "loop_end": "",
                   "zero": "",
                   "final": ""}
        self.extension = ""

    def _parse_code(self, code):
        """Removes non-bf characters from input code"""
        return sub(r"[^<>+\-.,\[\]]", "", code)

    def _optimize(self, code):
        """Adds optimizations to input bf code"""
        # [-] (zeroing loop) to 0, replaced in output by op_zero
        return sub(r"\[\-+\]", "0", self.code)

    def _count(self):
        """Counts occurances of char at self.position"""
        for index in range(self.status["position"], self.length):
            if self.code[index] != self.code[self.status["position"]]:
                return index - self.status["position"]
        return self.length - self.status["position"]

    def _construct(self):
        """ Constructs the output code by appending each op translation to
            output list and correctly indents output code.
        """
        length = len(self.code)
        while self.status["position"] < length:
            print("\r{}/{}".format(self.status["position"] + 1, length), end="")
            instruction = self.code[self.status["position"]]
            count = self._count()
            if instruction == "+":
                self.output.append(self.op["add"].format(count))
                self.status["position"] += count
            elif instruction == "-":
                self.output.append(self.op["sub"].format(count))
                self.status["position"] += count
            elif instruction == "<":
                self.output.append(self.op["left"].format(count))
                self.status["position"] += count
            elif instruction == ">":
                self.output.append(self.op["right"].format(count))
                self.status["position"] += count
            elif instruction == ".":
                self.output.append(self.op["out"])
                self.status["position"] += 1
            elif instruction == ",":
                self.output.append(self.op["in"])
                self.status["position"] += 1
            elif instruction == "[":
                self.output.append(self.op["loop_begin"])
                self.status["position"] += 1
            elif instruction == "]":
                self.output.append(self.op["loop_end"])
                self.status["position"] += 1
                self.status["spaces"] = self.status["spaces"][0:-4]
            elif instruction == "0":
                self.output.append(self.op["zero"])
                self.status["position"] += 1
            self.output[-1] = self.status["spaces"] + self.output[-1]
            if instruction == "[":
                self.status["spaces"] += "    "
        self.output.append(self.op["final"])
        print("")

    def _output(self):
        """Returns output code as a string"""
        return "\n".join(self.output)

    def convert(self):
        """Public method used to construct and output new code"""
        self._construct()
        return self._output()


class CConverter(Converter):
    """C code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["#include <stdio.h>\n",
                       "int main(void) {",
                       "    int index = 0;",
                       "    static char array[30000];"]
        self.op["add"] = "array[index] += {};"
        self.op["sub"] = "array[index] -= {};"
        self.op["left"] = "index -= {};"
        self.op["right"] = "index += {};"
        self.op["out"] = "putchar(array[index]);"
        self.op["in"] = "array[index] = getchar();"
        self.op["loop_begin"] = "while (array[index] != 0) {"
        self.op["loop_end"] = "}"
        self.op["zero"] = "array[index] = 0;"
        self.op["final"] = "}\n"
        self.extension = "c"
        self.status["spaces"] = " " * 4


class PyConverter(Converter):
    """Python code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["#!/usr/bin/env python",
                       "from __future__ import print_function",
                       "from sys import stdin, stdout\n",
                       "index = 0",
                       "array = [0] * 30000"]
        self.op["add"] = "array[index] += {}"
        self.op["sub"] = "array[index] -= {}"
        self.op["left"] = "index -= {}"
        self.op["right"] = "index += {}"
        self.op["in"] = "array[index] = ord(stdin.read(1))"
        self.op["out"] = "stdout.write(chr(array[index]))"
        self.op["loop_begin"] = "while array[index]:"
        self.op["zero"] = "array[index] = 0"
        self.extension = "py"


class ArduinoConverter(CConverter):
    """Arduino (.ino) code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["void setup() {",
                       "    Serial.begin(9600);",
                       "    int index = 0;",
                       "    static char array[1850];"]
        self.status["spaces"] = " " * 4
        self.op["in"] = "\n".join(["while (! Serial.available());",
                                   "{}array[index] = Serial.read();"])\
                                   .format(self.status["spaces"] + "    ")
        self.op["out"] = "Serial.print((char) array[index]);"
        self.op["loop_begin"] = "while (array[index]) {"
        self.op["final"] = "}\n\nvoid loop(){}\n"
        self.extension = "ino"


class JavaConverter(CConverter):
    """Java code converter class"""
    def __init__(self, code, package):
        super().__init__(code)
        self.output = ["import java.io.IOException;",
                       "public class {}{{".format(package.title()),
                       "    public static void main(String[] args) throws IOException {",
                       "        int[] array = new int[30000];",
                       "        int index = 0;"]
        self.status["spaces"] = " " * 8
        self.op["in"] = "array[index] = (int) System.in.read();"
        self.op["out"] = "System.out.print((char) array[index]);"
        self.op["final"] = "    }\n}"
        self.extension = "java"


class RustConverter(Converter):
    """Rust code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["use std::io::Read;\n",
                       "fn main() {",
                       "    let mut array: [u8; 30000] = [0; 30000];",
                       "    let mut index = 0;"]
        self.status["spaces"] = " " * 4
        self.op["add"] = "array[index] = array[index].wrapping_add({});"
        self.op["sub"] = "array[index] = array[index].wrapping_sub({});"
        self.op["left"] = "index -= {};"
        self.op["right"] = "index += {};"
        self.op["in"] = "\n".join(["let input: Option<u8> = std::io::stdin()",
                                   "{}    .bytes()"\
                                   .format(self.status["spaces"]),
                                   "{}    .next()"\
                                   .format(self.status["spaces"]),
                                   "{}    .and_then(|result| result.ok())"\
                                   .format(self.status["spaces"]),
                                   "{}    .map(|byte| byte as u8);"\
                                   .format(self.status["spaces"]),
                                   "{}array[index] = input.unwrap();"\
                                   .format(self.status["spaces"])])
        self.op["out"] = "print!(\"{}\", array[index] as char);"
        self.op["loop_begin"] = "while array[index] != 0 {"
        self.op["loop_end"] = "}"
        self.op["zero"] = "array[index] = 0;"
        self.op["final"] = "}"
        self.extension = "rs"


class SwiftConverter(Converter):
    """Swift code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["import Foundation\n",
                       "var array = [CInt](repeating: 0, count: 30000)",
                       "var index = 0"]
        self.op["add"] = "array[index] += {}"
        self.op["sub"] = "array[index] -= {}"
        self.op["left"] = "index -= {}"
        self.op["right"] = "index += {}"
        self.op["in"] = ""
        self.op["out"] = "print(String(format:\"%c\", array[index]), terminator:\"\")"
        self.op["loop_begin"] = "while array[index] != 0 {"
        self.op["loop_end"] = "}"
        self.op["zero"] = "array[index] = 0"
        self.extension = "swift"


class JavaScriptConverter(CConverter):
    """Javascript code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["<!DOCTYPE HTML>",
                       "<script>",
                       "    let array = Array.apply(0, Array(30000))"
                       ".map(function () {return 0;});",
                       "    let index = 0;",
                       "    let output = \"\";"]
        self.op["out"] = "output = output.concat(String.fromCharCode(array[index]));"
        self.op["in"] = ""
        self.op["final"] = "\n".join(["    alert(output);",
                                      "</script>"])
        self.extension = "html"


class CSharpConverter(JavaConverter):
    """C# code converter class"""
    def __init__(self, code, package):
        super().__init__(code, package)
        self.output = ["using System;\n"
                       "public class {}{{".format(package.title()),
                       "    public static void Main(string[] args) {",
                       "        int[] array = new int[30000];",
                       "        int index = 0;"]
        self.op["out"] = "Console.Write((char) array[index]);"
        self.op["in"] = "array[index] = (int) Console.read();"
        self.extension = "cs"


class BashConverter(Converter):
    """Shell script code converter class"""
    def __init__(self, code, *args):
        super().__init__(code)
        self.output = ["#!/bin/bash\n",
                       "declare -a ARRAY=( $(for i in {1..30000}; do echo 0; done) )",
                       "declare INDEX=0"]
        self.op["add"] = "ARRAY[$INDEX]=$((ARRAY[$INDEX]+{}))"
        self.op["sub"] = "ARRAY[$INDEX]=$((ARRAY[$INDEX]-{}))"
        self.op["left"] = "INDEX=$(($INDEX-{}))"
        self.op["right"] = "INDEX=$(($INDEX+{}))"
        self.op["out"] = "printf \\\\$(printf '%03o' $((ARRAY[$INDEX])))"
        self.op["loop_begin"] = "while [  ARRAY[$INDEX] != 0  ]; do"
        self.op["loop_end"] = "done"
        self.op["zero"] = "ARRAY[$INDEX]=0"
        self.extension = "sh"


if __name__ == "__main__":
    def get_arguments():
        """Retrieves command line arguments"""
        parser = argparse.ArgumentParser()
        parser.add_argument("input",
                            help="The file to be converted")
        parser.add_argument("-a", "--all",
                            action="store_true",
                            help="Output in all supported languages")
        parser.add_argument("-o", "--output",
                            action="store",
                            help="Path of output file, - for stdout")
        for language in ("python", "java", "c",
                         "csharp", "rust", "arduino",
                         "swift", "javascript", "shell"):
            parser.add_argument("--{}".format(language),
                                action="store_true",
                                help="Output {} code".format(language))
        return parser.parse_args()


    args = get_arguments()

    with open(args.input, "r") as input_file:
        bf_input = input_file.read()

    if args.output is not None:
        # Creates package/output file name by removing extension from input file
        name = path.splitext(path.split(args.output)[1])[0]
        if args.output == "-":
            name = None
    else:
        name = path.splitext(path.split(args.input)[1])[0]

    # List of all language arguments and corresponding converter classes
    language_arguments = [(args.python, PyConverter),
                          (args.java, JavaConverter),
                          (args.c, CConverter),
                          (args.rust, RustConverter),
                          (args.arduino, ArduinoConverter),
                          (args.swift, SwiftConverter),
                          (args.csharp, CSharpConverter),
                          (args.javascript, JavaScriptConverter),
                          (args.shell, BashConverter)]

    # Converts each selected option
    for arg, Converter in language_arguments:
        if arg or args.all:
            converter = Converter(bf_input, name)
            text = converter.convert()
            if name is not None:
                with open("{}.{}".format(name, converter.extension), "w") as outfile:
                    outfile.write(text)
            else:
                print(text)
