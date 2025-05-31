# 4-BIT CPU

## Instruction Set Architecture

| **Instruction**     | **Encoding**        | **Operation**                 | **Comment**                                                                 |
|---------------------|---------------------|-------------------------------|------------------------------------------------------------------------------|
| NOP                 | 0000                | N/A                           | Does nothing and proceeds to next instruction                               |
| ALU ADD A, B, dest  | 0001 AABB 01DD      | dest ← A + B                  | Adds the values of registers A and B, stores result in destination register |
| ALU SUB A, B, dest  | 0001 AABB 10DD      | dest ← A - B                  | Subtracts value of B from A, stores result in destination register          |
| ALU CMP A, B        | 0001 AABB 1111      | regFlag ← compare(A, B)       | Compares values of registers A and B, stores result in flag register        |
| COPY dest, src      | 0010 DDSS           | dest ← src                    | Copies value from one register to another                                   |
| LOAD addr, dest     | 0011 addr RR00      | dest ← M[addr]                | Loads value from memory into destination register                           |
| STORE src, addr     | 0100 addr           | M[addr] ← src                 | Stores value of source register into memory address                         |
| LOADI dest, XXXX    | 0101 RR00 XXXX      | dest ← XXXX                   | Loads an immediate value into a register                                    |
| JUMP addr           | 0110 addr           | PC = addr                     | Sets the program counter to the given address                               |
| CJUMP CMP, addr     | 0111 00CC addr      | if (CC == regFlag) PC = addr | Conditional jump based on flag register                                     |
| IOOUT port, value   | 1000 HHHH value     | port ← value                  | Sends value to I/O port and triggers write signal                           |
| SAVEKEY dest        | 1001 DD00           | dest ← keyboard value         | Stores value from keyboard into register                                    |


## ⚠️ Disclaimer
> This program is **not related to any financial advice, services, or real-world finance markets**.
> The "Finance Assembly Code" is purely a **simulation created for educational purposes only**.

<details>
  <summary>💰 Finance Assembly Code</summary>

```asm
  DO_ADD:
      SAVE_KEY R1
      LOADI R2, 0X1
      ALU ADD, R0, R0, R2
      ALU CMP, FLAGS R1, R2
      CJUMP EQ, SHOW_RESULT

      JUMP DO_SUB

  DO_SUB:
      SAVE_KEY R1
      LOADI R2, 0X1
      ALU SUB, R0, R0, R2
      ALU CMP, FLAGS R1, R2
      CJUMP EQ, SHOW_RESULT

      JUMP DO_ADD
.....
```
 [Read all the code in here ►](code/financeSimulation.txt)
</details>
