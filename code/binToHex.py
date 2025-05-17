import tkinter as tk
from tkinter import messagebox

def binary_to_hex(binary_str):
    try:
        # Remove spaces and newlines and validate the binary input
        binary_str = binary_str.replace(" ", "").replace("\n", "")
        if not all(c in '01' for c in binary_str):
            raise ValueError("Input must contain only 0 and 1.")

        # Pad the binary string to make its length a multiple of 4
        while len(binary_str) % 4 != 0:
            binary_str = '0' + binary_str

        # Convert every 4 binary digits to hex and add a space in between
        hex_result = ' '.join(hex(int(binary_str[i:i+4], 2))[2:].upper() for i in range(0, len(binary_str), 4))
        return hex_result
    except Exception as e:
        messagebox.showerror("Error", f"Invalid input: {e}")
        return ""

def on_convert():
    binary_input = binary_text.get("1.0", tk.END).strip()
    hex_output = binary_to_hex(binary_input)
    if hex_output:
        hex_output_text.delete("1.0", tk.END)  # Clear previous output
        hex_output_text.insert("1.0", hex_output)  # Insert new hex output

# Create the main window
root = tk.Tk()
root.title("Binary to Hex Converter")

# Create and place widgets
binary_label = tk.Label(root, text="Enter Binary:")
binary_label.grid(row=0, column=0, padx=10, pady=10)

binary_text = tk.Text(root, width=50, height=10)
binary_text.grid(row=0, column=1, padx=10, pady=10)

convert_button = tk.Button(root, text="Convert", command=on_convert)
convert_button.grid(row=1, column=0, columnspan=2, pady=10)

# Create a Text widget for displaying hex output (copy-paste enabled)
hex_output_text = tk.Text(root, width=50, height=5)
hex_output_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# Start the Tkinter event loop
root.mainloop()
