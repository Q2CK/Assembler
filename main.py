import json
import os

# File path
here = os.path.dirname(os.path.abspath(__file__))


# Main class
class Assembler:

    def __init__(self) -> None:

        self.errors: dict = {"": ""}

        while len(self.errors) != 0:

            self.isa_file_name: list[str] = []                       # Name of the config file for a given CPU
            self.asm_file_name: str = input("Assembly file name: ")  # Name of the assembly file
            self.asm_file = None

            self.isa: dict = {}        # Dictionary of assembly instructions and their properties
            self.define: dict = {}     # Dictionary of user-defined keywords in the .asm file
            self.labels: dict = {}     # Dictionary of branching labels and their memory addresses

            self.asm_lines: dict = {}  # Dictionary of .asm file lines, indexed by program line number

            self.errors: dict = {}     # Dictionary of found errors, indexed by program line number

            if os.path.isfile(os.path.abspath(self.asm_file_name)):

                self.asm_file = open(os.path.abspath(self.asm_file_name), "r")

                self.asm_lines = self.find_declarations()

            else:
                self.errors[0] = f"ASM file '{self.asm_file_name}' not found"

            if len(self.errors) == 0:

                self.asm_lines = self.replace()

            if len(self.errors) == 0:

                output_string = self.assemble()

            else:
                output_string = ""

                for error in self.errors:
                    output_string += self.errors[error]

                self.asm_file.close()

            print(output_string)

    def read_lines(self) -> dict:                      # Read the .asm file line-by-line and store to a dict

        asm_lines: dict = {}
        asm_line: str = self.asm_file.readline()

        line_nr = 0

        while asm_line != "":                          # Only append a new line if not empty
            asm_lines[line_nr] = asm_line
            asm_line = self.asm_file.readline()
            line_nr += 1

        return asm_lines

    def find_declarations(self) -> dict:  # Find "#define" and "#isa" statements and validate them

        asm_lines: dict = self.read_lines()
        output_lines: dict = {}

        for idx in asm_lines:  # Remove comments
            if asm_lines[idx].strip().startswith("//"):
                asm_lines[idx] = ""

        output_line_nr = 0

        for line in asm_lines:

            tokens: list[str] = asm_lines[line].split()

            if len(tokens) == 2 and tokens[0] in ["#isa", "#ISA", "#Isa"] \
                    and os.path.isfile(os.path.abspath(f"ISA/{tokens[1] + '.json'}")):

                self.isa_file_name.append(tokens[1] + ".json")

            elif len(tokens) == 2 and tokens[0] in ["#isa", "#ISA", "#Isa"] \
                    and not os.path.isfile(os.path.abspath(f"ISA/{tokens[1] + '.json'}")):

                self.errors[output_line_nr] = f"ISA file {tokens[1]}.json not found"
                return {}

            elif len(tokens) == 3 and tokens[0] in ["#DEFINE", "#Define", "#define"]:

                errors: str = ""

                for char in tokens[1]:
                    if not char.isalnum():
                        errors += char

                for char in tokens[2]:
                    if not char.isalnum():
                        errors += char

                if len(errors) == 0:
                    self.define[tokens[1]] = tokens[2]

                else:
                    self.errors[output_line_nr] = f"Chars '{errors}' are not allowed in define statements"
                    return {}

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
            return {}

        elif len(self.isa_file_name) < 1:

            print("ISA file declaration required")
            return {}

        else:
            return output_lines

    def replace(self) -> dict:  # Replace defined keywords and labels

        self.isa = json.loads(open(os.path.abspath(f"ISA/{self.isa_file_name[0]}"), "r").read().lower())

        tokenized_lines: dict = {}

        for line in self.asm_lines:

            tokens: list[str] = self.asm_lines[line].replace("\n", "").replace(",", " ").split()

            for idx, token in enumerate(tokens[1:]):

                keywords_bases = self.isa["instructions"][tokens[0]]["keywords"]  # Find predefined keywords bases names

                for keywords_base in keywords_bases:

                    keywords = self.isa["define"][keywords_base]

                    for keyword in keywords:                        # Check for keywords from each base and replace them
                        if keyword == token:
                            tokens[idx + 1] = self.isa["define"][keywords_base][keyword]

                if token in self.labels:                            # Check for labels and replace them with addresses
                    tokens[idx + 1] = str(self.labels[token])

                if token in self.define:                            # Check for defined keywords and replace them
                    tokens[idx + 1] = str(self.define[token])

                if not tokens[idx + 1].isnumeric():
                    self.errors[line] = f"Error: Unknown token '{tokens[idx + 1]}' in program line {line}"

            tokenized_lines[line] = tokens

        return tokenized_lines

    def assemble(self):

        return self.asm_lines


assembler: Assembler = Assembler()
