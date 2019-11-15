"""CPU functionality."""

import sys

# opcodes
HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PSH = 0b01000101
POP = 0b01000110
# reserved registers
IM = 5
IS = 6
SP = 7

class CPU:
    """Main CPU class."""
    def __init__(self):
        """Construct a new CPU."""
        self.halted = False
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.reg[SP] = 0xf4
        self.pc = 0 # program counter
        self.ir = self.ram[self.pc] # instruction register
        self.fl = 0 # flags -> 00000LGE -> L == <, G == >, E == == 

        self.bt = {
            HLT: self.halt,
            LDI: self.ldi,
            PRN: self.prn,
            MUL: self.mul,
            PSH: self.psh,
            POP: self.pop,
        }
    def load(self):
        """Load a program into memory."""
        address = 0
        filename = sys.argv[1]

        with open(filename) as fp:

            for line in fp:
                line = line.split("#")[0]
                line = line.strip()

                if line == "":
                    continue
                self.ram[address] = int(line, 2)
                address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")
    
    def ram_read(self, address):
        """
        should accept the address to read and return the value stored
        there
        """
        return self.ram[address]

    def ram_write(self, value, address):
        """
        should accept a value to write, and the address to write it to.
        """
        self.ram[address] = value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X | \n" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def halt(self, operand_a, operand_b):
        self.halted = True
    def ldi(self, operand_a, operand_b):
        self.reg[operand_a] = operand_b
    def prn(self, operand_a, operand_b):
        print(self.reg[operand_a])
    def mul(self, operand_a, operand_b):
        self.alu("MUL", operand_a, operand_b)
    def psh(self, operand_a, operand_b):
        self.reg[SP] -= 1
        self.ram_write(self.reg[operand_a], self.reg[7])
        
    def pop(self, operand_a, operand_b):
        num = self.ram_read(self.reg[7])
        self.reg[SP] += 1
        self.reg[operand_a] = num

    def run(self):
        """Run the CPU."""
        # opcodes
        while not self.halted:
            IR = self.ram[self.pc]
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            # inc_pc = int(str(IR)[:2], 2) + 1
            inc_pc = ((IR >> 6) & 0b11) + 1
            sets_pc = ((IR >> 4) & 0b1) == 1

            if IR in self.bt:
                self.bt[IR](operand_a, operand_b)
            else:
                print(f"ERROR: operation {IR} unknown")
                sys.exit(1)

            if not sets_pc:
                self.pc += inc_pc
