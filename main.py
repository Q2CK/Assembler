import json
import os
import re
from types import SimpleNamespace

here = os.path.dirname(os.path.abspath(__file__))


class Assembler:

    def __init__(self) -> None:

        self.isa_file_name: list[str] = []
        self.asm_file_name: str = ""

        self.isa: object = None
        self.define: dict = {}

        self.labels = []

        self.asm_lines: list[str] = []

        error: bool = True

        while error:
            try:
                self.asm_file_name = input("Assembly file name: ")
                self.asm_file = open(os.path.abspath(self.asm_file_name), "r")

            except FileNotFoundError:
                print("File not found")
                error = False
                self.asm_file.close()

            else:
                error, self.asm_lines = self.find_declarations()
                self.assemble()

    def assemble(self):
        self.isa = json.loads(
            open(os.path.abspath(f"ISA/{self.isa_file_name[0]}"), "r").read().lower(),
            object_hook=lambda d: SimpleNamespace(**d))

        for line in self.asm_lines:
            tokens = re.split(", |,|.| ", line.replace("\n", ""))
            print(tokens)

    def read_lines(self) -> list[str]:
        asm_lines: list[str] = []
        asm_line: str = self.asm_file.readline()

        while asm_line != "":
            asm_lines.append(asm_line)
            asm_line = self.asm_file.readline()

        return asm_lines

    def find_declarations(self) -> tuple[bool, list[str]]:
        asm_lines = self.read_lines()
        output_lines: list[str] = []

        for line in asm_lines:
            tokens: list[str] = line.split()

            if len(tokens) == 2 and tokens[0] in ["#isa", "#ISA", "#Isa"] :
                self.isa_file_name.append(tokens[1] + ".json")

            elif len(tokens) == 3 and tokens[0] in ["#DEFINE", "#Define", "#define"]:

                errors: list[str] = []

                for char in tokens[1]:
                    if not char.isalnum():
                        errors.append(char)

                for char in tokens[2]:
                    if not char.isalnum():
                        errors.append(char)

                if len(errors) == 0:
                    self.define[tokens[1]] = tokens[2]

                else:
                    print(f"Chars '{errors}' are not allowed in define statements")
                    return True, []

            elif len(tokens) == 0:
                continue

            elif len(tokens) == 1 and tokens[0].isspace():
                continue

            else:
                output_lines.append(line)

        if len(self.isa_file_name) > 1:
            print("Single ISA file declaration required")
            return True, []

        elif len(self.isa_file_name) < 1:
            print("ISA file declaration required")
            return True, []

        else:
            return False, output_lines


assembler: Assembler = Assembler()
