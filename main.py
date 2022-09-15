import json

allowed_define_chars = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz0123456789"]


class Assembler:
    def __init__(self):
        self.asm_file = open(input("Assembly file name: "), "r")

        self.ISA: list[str] = []
        self.define: dict = {}

    def read_lines(self):
        asm_lines: list[str] = []
        asm_line: str = self.asm_file.readline()

        while asm_line != "":
            asm_lines.append(asm_line)
            asm_line = self.asm_file.readline()

        return asm_lines

    def find_declarations(self):
        asm_lines = self.read_lines()

        for line in asm_lines:
            tokens = line.split()

            if tokens[0] in ["#isa", "#ISA", "#Isa"] and len(tokens) == 2:
                self.ISA.append(tokens[1] + ".json")

            elif tokens[0] in ["#DEFINE", "#Define", "#define"] and len(tokens) == 3:
                self.define[tokens[1]] = tokens[2]

        if len(self.ISA) > 1:
            print("Single ISA file declaration required")
            return False

        elif len(self.ISA) < 1:
            print("Single ISA file declaration required")
            return False

        else:
            return True


assembler: Assembler = Assembler()
