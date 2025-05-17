import tkinter as tk
from tkinter import messagebox

# Instruction-to-hex mapping based on your ISA
OPCODES = {
    "NOP": "0000",
    "ALU": "0001",
    "COPY": "0010",
    "LOAD": "0011",
    "STORE": "0100",
    "LOADI": "0101",
    "JUMP": "0110",
    "CJUMP": "0111",
    "IOOUT": "1000",
    "SAVE_KEY": "1001"
}

ALU_OPS = {
    "NOP": "00",
    "ADD": "01",
    "SUB": "10",
    "CMP": "11"
}

REGISTERS = {
    "R0": "00",
    "R1": "01",
    "R2": "10",
    "FLAGS": "11"
}

CONDITIONS = {
    "CARRY": "0000",
    "GT": "0001",
    "EQ": "0010",
    "LT": "0011"
}

# Function to preprocess variable declarations and convert them into instructions
def preprocess_variables(assembly_code):
    lines = assembly_code.splitlines()
    processed_lines = []
    variables = {}  # Dictionary to store variable names and their addresses
    current_memory_address = 0xFFFF  # Start memory address for variables

    for line in lines:
        line = line.strip()
        if "=" in line:  # Variable declaration
            parts = line.split("=")
            var_name = parts[0].strip()
            var_value = parts[1].strip()

            if var_name in variables:
                return f"Error: Duplicate variable '{var_name}'"

            # Assign the variable an address
            variables[var_name] = current_memory_address
            current_memory_address -= 1  # Move to the next memory address

            # Replace variable with LOADI and STORE instructions
            processed_lines.append(f"LOADI R0, {var_value}")
            processed_lines.append(f"STORE R0, 0x{variables[var_name]:04X}")
        else:
            # Replace variable names in other lines with their addresses
            for var in variables:
                line = line.replace(var, f"0x{variables[var]:04X}")
            processed_lines.append(line)

    return "\n".join(processed_lines)


def preprocess_print_statements(assembly_code):
    lines = assembly_code.splitlines()
    processed_lines = []

    for line in lines:
        line = line.strip()
        if line.startswith("PRINT"):  # Detect PRINT instruction
            # Extract the string between quotes
            start = line.find('"') + 1
            end = line.rfind('"')
            if start == 0 or end == -1 or start >= end:
                return "Error: Invalid PRINT syntax. Missing or unclosed quotes."

            text_to_print = line[start:end]
            for char in text_to_print:
                ascii_value = ord(char)  # Convert character to ASCII
                processed_lines.append(f"IOOUT 0x1 0x{ascii_value:02X}")  # Format IOOUT instruction
        else:
            processed_lines.append(line)  # Keep other lines as is

    return "\n".join(processed_lines)


def assemble_code(assembly_code):
    assembly_code = preprocess_variables(assembly_code)  # Handle variables
    assembly_code = preprocess_print_statements(assembly_code)  # Handle PRINT

    if assembly_code.startswith("Error"):
        return assembly_code  # Return error from preprocessing


    lines = assembly_code.splitlines()
    machine_code = []
    labels = {}  # Dictionary to store label names and their line numbers
    current_address = 0  # Track the current memory address
    label_addresses = {}  # Track the resolved address for each label

    # First pass: Find labels and record their line number (address)
    for line_num, line in enumerate(lines, start=1):
        line = line.split(";")[0].strip()  # Remove comments and trim whitespace
        if not line:
            continue  # Skip empty lines

        if line.endswith(":"):  # Label detection
            label_name = line[:-1].strip()  # Remove the colon
            if label_name in labels:
                return f"Error on line {line_num}: Duplicate label '{label_name}'"
            labels[label_name] = current_address  # Record label position
        else:
            # Calculate address based on instruction size
            mnemonic = line.split()[0].upper()
            if mnemonic in ["LOAD", "STORE", "CJUMP" ]:
                current_address += 6  # These take 2 words (16 bits)
            elif mnemonic in [ "LOADI" , "ALU"]:  
                current_address += 3  
            elif mnemonic in [ "JUMP"]:  
                current_address += 5
            elif mnemonic in ["IOOUT"]:  
                current_address += 4    
            elif mnemonic in [ "COPY"]:  
                current_address += 2
            elif mnemonic in [ "SAVE_KEY"]:  
                current_address += 2             
            else:
                current_address += 1  # Other instructions take 1 word

    # Second pass: Assemble code, replacing labels with addresses
    current_address = 0  # Reset the address counter
    for line_num, line in enumerate(lines, start=1):
        line = line.split(";")[0].strip()  # Remove comments and trim whitespace
        if not line:
            continue  # Skip empty lines

        if line.endswith(":"):  # Skip label lines
            continue

        parts = line.split()
        mnemonic = parts[0].upper()

        if mnemonic not in OPCODES:
            return f"Error on line {line_num}: Unknown instruction '{mnemonic}'"

        opcode = OPCODES[mnemonic]

        try:
            if mnemonic == "NOP":
                machine_code.append(opcode)
                current_address += 1

            elif mnemonic == "ALU":
                op = ALU_OPS[parts[1].upper().strip(",")]
                dest = REGISTERS[parts[2].upper().strip(",")]
                src_a = REGISTERS[parts[3].upper().strip(",")]
                src_b = REGISTERS[parts[4].upper()]
                machine_code.append(opcode + src_a + src_b + op + dest)
                current_address += 3

            elif mnemonic == "COPY":
                dest = REGISTERS[parts[1].upper().strip(",")]
                src = REGISTERS[parts[2].upper()]
                machine_code.append(opcode + dest + src)
                current_address += 2

            elif mnemonic == "SAVE_KEY":
                dest = REGISTERS[parts[1].upper().strip(",")]
                machine_code.append(opcode + dest + "00")
                current_address += 2

            elif mnemonic == "LOAD":
                dest = REGISTERS[parts[1].upper().strip(",")]
                address = f"{int(parts[2], 16):016b}"
                machine_code.append(opcode + address + dest + "00")
                current_address += 6

            elif mnemonic == "STORE":
                src = REGISTERS[parts[1].upper().strip(",")]
                address = f"{int(parts[2], 16):016b}"
                machine_code.append(opcode + "00" + src  + address)
                current_address += 6

            elif mnemonic == "LOADI":
                dest = REGISTERS[parts[1].upper().strip(",")]
                value = f"{int(parts[2], 16):04b}"
                machine_code.append(opcode + dest + "00" + value)
                current_address += 3

            elif mnemonic == "JUMP":
                label = parts[1].upper().strip(",")
                if label not in labels:
                    return f"Error on line {line_num}: Undefined label '{label}'"
                # Use the label's address here
                address = f"{labels[label]:016b}"
                machine_code.append(opcode + address)
                current_address += 5

            elif mnemonic == "CJUMP":
                cond = CONDITIONS[parts[1].upper().strip(",")]
                label = parts[2].upper()
                if label not in labels:
                    return f"Error on line {line_num}: Undefined label '{label}'"
                # Use the label's address here
                address = f"{labels[label]:016b}"
                machine_code.append(opcode + cond + address)
                current_address += 6
            elif mnemonic == "IOOUT":  # New instruction logic
                port = f"{int(parts[1], 16):04b}"  # Convert port to binary (4 bits)
                value = f"{int(parts[2], 16):08b}"  # Convert value to binary (8 bits)
                machine_code.append(opcode + port + value)
                current_address += 4   

        except (KeyError, ValueError, IndexError):
            return f"Error on line {line_num}: Invalid operands or syntax."

    return "\n".join(machine_code)


def compile_code():
    assembly_code = text_editor.get("1.0", tk.END).strip()
    if not assembly_code:
        messagebox.showerror("Error", "Assembly code is empty!")
        return

    result = assemble_code(assembly_code)
    if result.startswith("Error"):
        messagebox.showerror("Compilation Error", result)
    else:
        output_area.delete("1.0", tk.END)
        output_area.insert("1.0", result)
        messagebox.showinfo("Success", "Compilation successful!")

# GUI Setup
root = tk.Tk()
root.title("4-Bit CPU Assembler")

# Text editor for assembly code
text_editor = tk.Text(root, height=40, width=80, bg="white", fg="black", font=("Courier", 8))
text_editor.pack(pady=10)

# Compile button
compile_button = tk.Button(root, text="Compile", command=compile_code, bg="green", fg="white", font=("Arial", 10, "bold"))
compile_button.pack(pady=5)

# Output area for machine code
output_area = tk.Text(root, height=20, width=80, bg="white", fg="black", font=("Courier", 8))
output_area.pack(pady=10)

root.mainloop()
