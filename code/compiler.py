import tkinter as tk
from tkinter import messagebox, ttk

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

def binary_to_hex(binary_str):
    try:
        # Remove spaces and newlines
        binary_str = binary_str.replace(" ", "").replace("\n", "")

        # Pad the binary string to make its length a multiple of 4
        while len(binary_str) % 4 != 0:
            binary_str = '0' + binary_str

        # Convert every 4 binary digits to hex
        hex_words = [hex(int(binary_str[i:i+4], 2))[2:].upper() for i in range(0, len(binary_str), 4)]
        return " ".join(hex_words)
    except Exception as e:
        return f"Error converting to hex: {e}"

def assemble_code(assembly_code):
    assembly_code = preprocess_variables(assembly_code)  # Handle variables
    assembly_code = preprocess_print_statements(assembly_code)  # Handle PRINT

    if assembly_code.startswith("Error"):
        return assembly_code  # Return error from preprocessing

    lines = assembly_code.splitlines()
    machine_code = []
    raw_hex_code = []
    labels = {}  # Dictionary to store label names and their line numbers
    instruction_lengths = {} # Store the length of each instruction
    current_address = 0  # Track the current memory address

    # First pass: Find labels and record their line number (address) and instruction length
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
            mnemonic = line.split()[0].upper()
            if mnemonic in ["LOAD", "STORE", "CJUMP" ]:
                instruction_lengths[line_num] = 6
                current_address += 6  # These take 2 words (16 bits)
            elif mnemonic in [ "LOADI" , "ALU"]:
                instruction_lengths[line_num] = 3
                current_address += 3
            elif mnemonic in [ "JUMP"]:
                instruction_lengths[line_num] = 5
                current_address += 5
            elif mnemonic in ["IOOUT"]:
                instruction_lengths[line_num] = 4
                current_address += 4
            elif mnemonic in [ "COPY"]:
                instruction_lengths[line_num] = 2
                current_address += 2
            elif mnemonic in [ "SAVE_KEY"]:
                instruction_lengths[line_num] = 2
                current_address += 2
            else:
                instruction_lengths[line_num] = 1
                current_address += 1  # Other instructions take 1 word

    # Second pass: Assemble code, replacing labels with addresses
    current_address = 0  # Reset the address
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
            binary_instruction = ""
            if mnemonic == "NOP":
                binary_instruction = opcode
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "ALU":
                op = ALU_OPS[parts[1].upper().strip(",")]
                dest = REGISTERS[parts[2].upper().strip(",")]
                src_a = REGISTERS[parts[3].upper().strip(",")]
                src_b = REGISTERS[parts[4].upper()]
                binary_instruction = opcode + src_a + src_b + op + dest
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "COPY":
                dest = REGISTERS[parts[1].upper().strip(",")]
                src = REGISTERS[parts[2].upper()]
                binary_instruction = opcode + dest + src
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "SAVE_KEY":
                dest = REGISTERS[parts[1].upper().strip(",")]
                binary_instruction = opcode + dest + "00"
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "LOAD":
                dest = REGISTERS[parts[1].upper().strip(",")]
                address = f"{int(parts[2], 16):016b}"
                binary_instruction = opcode + address + dest + "00"
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "STORE":
                src = REGISTERS[parts[1].upper().strip(",")]
                address = f"{int(parts[2], 16):016b}"
                binary_instruction = opcode + "00" + src + address
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "LOADI":
                dest = REGISTERS[parts[1].upper().strip(",")]
                value = f"{int(parts[2], 16):04b}"
                binary_instruction = opcode + dest + "00" + value
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "JUMP":
                label = parts[1].upper().strip(",")
                if label not in labels:
                    return f"Error on line {line_num}: Undefined label '{label}'"
                # Use the label's address here
                address = f"{labels[label]:016b}"
                binary_instruction = opcode + address
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "CJUMP":
                cond = CONDITIONS[parts[1].upper().strip(",")]
                label = parts[2].upper()
                if label not in labels:
                    return f"Error on line {line_num}: Undefined label '{label}'"
                # Use the label's address here
                address = f"{labels[label]:016b}"
                binary_instruction = opcode + cond + address
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            elif mnemonic == "IOOUT":  # New instruction logic
                port = f"{int(parts[1], 16):04b}"  # Convert port to binary (4 bits)
                value = f"{int(parts[2], 16):08b}"  # Convert value to binary (8 bits)
                binary_instruction = opcode + port + value
                machine_code.append(binary_instruction)
                raw_hex_code.append(binary_to_hex(binary_instruction))

            if binary_instruction:
                instruction_length = instruction_lengths.get(line_num, 1) # Default to 1 if not found
                current_address += instruction_length

        except (KeyError, ValueError, IndexError):
            return f"Error on line {line_num}: Invalid operands or syntax."

    formatted_hex = " ".join(raw_hex_code)

    return {
        "binary": "\n".join(machine_code),
        "hex": formatted_hex
    }

def compile_code():
    assembly_code = text_editor.get("1.0", tk.END).strip()
    if not assembly_code:
        messagebox.showerror("Error", "Assembly code is empty!")
        return

    result = assemble_code(assembly_code)
    if isinstance(result, str) and result.startswith("Error"):
        messagebox.showerror("Compilation Error", result)
    else:
        # Get current tab and show appropriate output
        current_tab = output_notebook.index(output_notebook.select())

        # Clear both output areas
        binary_output.delete("1.0", tk.END)
        hex_output.delete("1.0", tk.END)

        # Insert results
        binary_output.insert("1.0", result["binary"])
        hex_output.insert("1.0", result["hex"])

        messagebox.showinfo("Success", "Compilation successful!")

# GUI Setup
root = tk.Tk()
root.title("Assembly to Hex Converter")

# Main frame
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill=tk.BOTH, expand=True)

# Text editor for assembly code
editor_frame = ttk.LabelFrame(main_frame, text="Assembly Code")
editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)

text_editor = tk.Text(editor_frame, height=20, width=80, bg="white", fg="black", font=("Courier", 10))
text_editor.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Example code button
def load_example():
    example_code = """
START:
    COUNTER = 0x0

MAIN:
    PRINT "Hello, World!"
"""
    text_editor.delete("1.0", tk.END)
    text_editor.insert("1.0", example_code)

example_button = ttk.Button(editor_frame, text="Load Example", command=load_example)
example_button.pack(side=tk.RIGHT, padx=5, pady=5)

# Compile button
compile_button = ttk.Button(main_frame, text="Compile", command=compile_code)
compile_button.pack(pady=5)

# Output area with tabs for binary and hex
output_notebook = ttk.Notebook(main_frame)
output_notebook.pack(fill=tk.BOTH, expand=True, pady=5)

binary_frame = ttk.Frame(output_notebook)
hex_frame = ttk.Frame(output_notebook)

output_notebook.add(binary_frame, text="Binary Output")
output_notebook.add(hex_frame, text="Hex Output")

binary_output = tk.Text(binary_frame, height=10, width=80, bg="white", fg="black", font=("Courier", 10))
binary_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

hex_output = tk.Text(hex_frame, height=10, width=80, bg="white", fg="black", font=("Courier", 10))
hex_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

# Status bar
status_bar = ttk.Label(root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

# Start the application
root.mainloop()