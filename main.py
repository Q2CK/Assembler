import json
import os

# File path
here = os.path.dirname(os.path.abspath(__file__))


# Main class
class Assembler:

    def __init__(self) -> None:

        self.isa_file_name: list[str] = []  # Name of the config file for a give CPU
        self.asm_file_name: str = ""        # Name of the assembly file

        self.isa: dict = {}                 # Dictionary of assembly instructions and their properties
        self.define: dict = {}              # Dictionary of user-defined keywords in the .asm file

        self.labels: dict = {}              # Dictionary of branching labels and their memory addresses

        self.asm_lines: dict = {}           # Dictionary of .asm file lines, indexed by line number, counting from first
        # assembly instruction

        error: bool = True

        while error:
            try:
                self.asm_file_name = input("Assembly file name: ")
                self.asm_file = open(os.path.abspath(self.asm_file_name), "r")

            except FileNotFoundError:
                print("File not found")

            else:
                error, self.asm_lines = self.find_declarations()
                self.replace()

    def replace(self):  # Replace defined keywords and labels

        self.isa = json.loads(open(os.path.abspath(f"ISA/{self.isa_file_name[0]}"), "r").read().lower())

        tokenized_lines: dict = {}

        for line in self.asm_lines:
            tokens = self.asm_lines[line].replace("\n", "").replace(",", " ").split()

            for idx, token in enumerate(tokens[1:]):

                keywords_bases = self.isa["instructions"][tokens[0]]["keywords"]  # Find predefined keywords bases names

                for keywords_base in keywords_bases:

                    keywords = self.isa["define"][keywords_base]

                    for keyword in keywords:                        # Check for keywords from each base and replace them
                        if keyword == token:
                            tokens[idx + 1] = self.isa["define"][keywords_base][keyword]

                if token in self.labels:                            # Check for labels and replace them with addresses
                    tokens[idx + 1] = str(self.labels[token])

            tokenized_lines[line] = tokens

        print(tokenized_lines)

    def read_lines(self) -> dict:                      # Read the .asm file line-by-line and store to a dict
        asm_lines: dict = {}
        asm_line: str = self.asm_file.readline()

        line_nr = 0

        while asm_line != "":                          # Only append a new line if not empty
            asm_lines[line_nr] = asm_line
            asm_line = self.asm_file.readline()
            line_nr += 1

        return asm_lines

    def find_declarations(self) -> tuple[bool, dict]:  # Find "#define" and "#isa" statements and validate them

        asm_lines: dict = self.read_lines()
        output_lines: dict = {}

        output_line_nr = 0

        for line in asm_lines:
            tokens: list[str] = asm_lines[line].split()

            if len(tokens) == 2 and tokens[0] in ["#isa", "#ISA", "#Isa"]:
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
                    return True, {}

            elif len(tokens) == 1 and tokens[0].startswith("."):
                if tokens[0].replace(".", "").isalnum():
                    self.labels[tokens[0].replace(".", "")] = output_line_nr

            elif len(tokens) == 0:
                continue

            elif len(tokens) == 1 and tokens[0].isspace():
                continue

            else:
                output_lines[output_line_nr] = asm_lines[line]
                output_line_nr += 1

        if len(self.isa_file_name) > 1:
            print("Single ISA file declaration required")
            return True, {}

        elif len(self.isa_file_name) < 1:
            print("ISA file declaration required")
            return True, {}

        else:
            return False, output_lines


assembler: Assembler = Assembler()
