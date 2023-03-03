import json
import os
import math

# File path
here = os.path.dirname(os.path.abspath(__file__))
print(here)


# Main class
class Assembler:
    def __init__(self) -> None:

        self.errors: list = [""]

        while True:

            self.isa_file_name: list[str] = []  # Name of the config file for a given CPU
            final_isa_file_name: str = ""
            self.asm_file_name: str = input("Assembly file name: ")  # Name of the assembly file
            self.asm_file = None

            self.isa: dict = {}  # Dictionary of assembly instructions and their properties
            self.define: dict = {}  # Dictionary of user-defined keywords in the .asm file
            self.labels: dict = {}  # Dictionary of branching labels and their memory addresses

            self.asm_lines: dict = {}  # Dictionary of .asm file lines, indexed by program line number
            self.errors: list = []  # Dictionary of found errors, indexed by program line number
            self.length: int = 0

            output_string: str = ""  # Output

            if os.path.isfile(os.path.join(here, "ASM/" + self.asm_file_name)):
                self.asm_file = open(os.path.join(here, "ASM/" + self.asm_file_name), "r")
                self.asm_lines = self.find_declarations()

            else:
                self.errors += f"ASM file '{self.asm_file_name}' not found"

            if len(self.errors) == 0:
                self.asm_lines = self.replace()

            if len(self.errors) == 0:
                output_string = self.assemble()

                self.bin_file = open(
                    os.path.join(here, "BIN/" + self.asm_file_name[:len(self.asm_file_name) - 4] + ".bin"), "w")
                self.bin_file.write(output_string)
                self.bin_file.close()

            if len(self.errors) != 0:
                for error in self.errors:
                    output_string += error + "\n"

                if self.asm_file is not None:
                    self.asm_file.close()

            print("\n" + output_string)

            if len(self.isa_file_name) == 1:
                final_isa_file_name = self.isa_file_name[0]
                print(f"CPU config:     ISA/{final_isa_file_name}")
                print(f"Program size:   {self.length} lines")
                print(f"Saved to:       BIN/{self.asm_file_name[:len(self.asm_file_name) - 4]}.bin" + "\n")

    def read_lines(self) -> dict:  # Read the .asm file line-by-line and store to a dict

        asm_lines: dict = {}
        asm_line: str = self.asm_file.readline()

        line_nr = 0

        while asm_line != "":  # Only append a new line if not empty
            asm_lines[line_nr] = asm_line
            asm_line = self.asm_file.readline()
            line_nr += 1

        return asm_lines

    def find_declarations(self) -> dict:  # Find "#define" and "#isa" statements and validate them
        asm_lines: dict = self.read_lines()
        output_lines: dict = {}

        for idx in asm_lines:  # Remove comments from asm lines
            if asm_lines[idx].strip().startswith("//"):
                asm_lines[idx] = ""

        output_line_nr = 0

        for line in asm_lines:
            tokens: list[str] = asm_lines[line].split()

            if len(tokens) == 2 and tokens[0] in ["#isa", "#ISA", "#Isa"] \
                    and os.path.isfile(os.path.join(here, f"ISA/{tokens[1] + '.json'}")):
                self.isa_file_name.append(tokens[1] + ".json")

            elif len(tokens) == 2 and tokens[0] in ["#isa", "#ISA", "#Isa"] \
                    and not os.path.isfile(os.path.join(here, f"ISA/{tokens[1] + '.json'}")):
                self.errors.append(f"ISA file {tokens[1]}.json not found")
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
                    self.errors.append(f"Chars '{errors}' are not allowed in define statements")
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
        self.isa = json.loads(open(os.path.join(here, f"ISA/{self.isa_file_name[0]}"), "r").read().lower())

        tokenized_lines: dict = {}

        for line in self.asm_lines:
            tokens: list[str] = self.asm_lines[line].replace("\n", "").replace(",", " ").lower().split()

            for idx, token in enumerate(tokens[1:]):
                if tokens[0] in self.isa["instructions"]:
                    keywords_bases = self.isa["instructions"][tokens[0]]["keywords"]  # Find predefined keywords bases

                else:
                    keywords_bases = {}

                for keywords_base in keywords_bases:
                    keywords = self.isa["define"][keywords_base]

                    for keyword in keywords:  # Check for keywords from each base and replace them
                        if keyword == token:
                            tokens[idx + 1] = self.isa["define"][keywords_base][keyword]

                if token in self.labels:  # Check for labels and replace them with addresses
                    tokens[idx + 1] = str(self.labels[token])

                if token in self.define:  # Check for defined keywords and replace them
                    tokens[idx + 1] = str(self.define[token])

                if token in self.isa["define"]["general"]:
                    tokens[idx + 1] = str(self.isa["define"]["general"][token])

                if not tokens[idx + 1].isnumeric():
                    self.errors.append(f"Error: Unknown token '{tokens[idx + 1]}' in program line {line}")

            if tokens[0] in self.isa["instructions"]:
                if len(tokens) - 1 > len(self.isa["instructions"][tokens[0]]["operands"]):
                    self.errors.append(f"Error: Too many operands for '{tokens[0]}' in program line {line} - "
                                       f"found {len(tokens) - 1}, expected " 
                                       f"{len(self.isa['instructions'][tokens[0]]['operands'])}")

                elif len(tokens) - 1 < len(self.isa["instructions"][tokens[0]]["operands"]):
                    self.errors.append(f"Error: Too few operands for '{tokens[0]}' in program line {line} - "
                                       f"found {len(tokens) - 1}, expected "
                                       f"{len(self.isa['instructions'][tokens[0]]['operands'])}")

            else:
                self.errors.append(f"Error: Unknown instruction mnemonic '{tokens[0]}' in program line {line}")

            tokenized_lines[line] = tokens

        return tokenized_lines

    def assemble(self) -> str:
        output_string: str = ""
        line_counter: int = 0
        capacity: int = self.isa["cpu_data"]["program_memory_lines"]

        for line in self.asm_lines:
            new_line: str = ""
            tokens: list = self.asm_lines[line]

            for idx, token in enumerate(tokens):
                if idx == 0:
                    new_line += self.isa["instructions"][tokens[0]]["opcode"]  # Opcode in binary

                else:
                    operand_template: str = self.isa["instructions"][tokens[0]]["operands"][idx - 1]
                    operand_bits: int = operand_template.count("-")
                    operand_binary: str = format(int(token), f"0{operand_bits}b")

                    position: int = 0

                    for char in operand_template:  # Append binary representations of operands, according to templates
                        if char == "-":
                            new_line += operand_binary[position]
                            position += 1

                        else:
                            new_line += char

            max_length: int = self.isa["cpu_data"]["instruction_length"]

            # Find number of required hex chars for line number, based on memory size
            line_nr_hex_chars: int = math.ceil(math.log(capacity, 16))
            lines_split: list = [new_line[i:i + max_length] for i in range(0, len(new_line), max_length)]

            for fragment in lines_split:  # Multi-cycle instructions get separated into multiple lines
                output_string += "0x" + format(line_counter, f"0{line_nr_hex_chars}x").upper() + ": " + fragment + "\n"
                line_counter += 1

        self.length = line_counter

        if self.length > capacity:
            self.errors.append(f"Program memory exceeded - {line_counter + 1} lines generated, maximum is {capacity}")
            return ""
        else:
            return output_string


if __name__ == "__main__":
    assembler: Assembler = Assembler()
    input("Press Enter to quit...")
