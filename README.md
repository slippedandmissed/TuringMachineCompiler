# Turing Machine Compiler

An assembly language, and a compiler to compile it into Turing machine instructions.

The Turing machine's tape is divided into two sections separated by a `#` character.

Extending to the right is the stack. This contains integers (including 0 and negative integers) in base 10 with one cell per digit (plus 1 for the `-` character if negative). The stack entries are separated by a `;` character.

Extending to the right is the environment. This consists of a variable name (set in assembly language) occupying one cell, and the cells to the left of it contain the digits of the value of that variable.

## Assembly language specifications

The assembly programs provided in `/examples/` are the files ending with `.alan`

Blank lines are ignored (even by the line numbering system. If the compiler tells you there is an error on line 5, this excludes blank lines. This will be fixed in a later version).

Instructions are written

```
[INSTR] [ARG0] [ARG1] [ARG2]...
```

Labels are created by putting a colon (`:`) followed by the label name.

Comments can be written after the characters `//`

See `/examples/` for details


Here is a list of the available assembly commands.

| Instruction | Argument Types   | Description                                                                                                                                                                                                                         |
|-------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `PUSH`      | integer          | Pushes the argument onto the stack                                                                                                                                                                                                  |
| `PUSHADDR`  | integer          | Pushes the address of the current instruction, plus the argument, to the stack                                                                                                                                                      |
| `POP`       |                  | Removes the last item from the stack                                                                                                                                                                                                |
| `SET`       | variable name    | Removes the last item from stack and stores it in the environment with the given variable name. If this variable name already has a value associated with it, this is not overwritten                                               |
| `LOAD`      | variable name    | Copies the most recent value associated with the given variable name from the environment to the stack                                                                                                                              |
| `UNSET`     | variable name    | Removes the most recent value associated with the given variable name from the stack                                                                                                                                                |
| `JUMP`      | integer          | Jumps the execution of the program forwards by the given number of instructions. The argument can be negative to jump backwards                                                                                                     |
| `JLZ`       | integer          | Removes the last item from the stack, and then jumps the execution of the program forwards by the given number of instructions if that item from the stack wass less than zero. The arguent can be negative to jump backwards       |
| `GOTO`      | label            | Moves the execution of the program to the address of the given label                                                                                                                                                                |
| `RETURN`    |                  | Removes the last item from the stack and moves the execution of the program to that address                                                                                                                                         |
| `ADD`       |                  | Removes the last two items from the stack and then pushes their sum onto the stack                                                                                                                                                  |
| `SUM`       |                  | Removes the last two item from the stack and then pushes the difference between the leftmost item of the two and the rightmost item of the two                                                                                      |
| `LSHIFT`    | natural number   | Adds the specified number of trailing zeros to the end of the last item in the stack                                                                                                                                                |
| `RSHIFT`    | natural number   | Removes the specified number of least significant digits from the end of the last item in the stack                                                                                                                                 |
| `REVERSE`   |                  | Reverses the order of the digits of the last item in the stack. If this number is negative, the `-` sign stays at the front                                                                                                         |
| `LAST`      | positive integer | Removes the last item from the stack and then pushes on the given number of its least significant digits onto the stack as a single number                                                                                          |
| `DIGITS`    |                  | Removes the last item from the stack and then pushes the number of digits in that number in base 10 to the stack (this does not include leading `0`s or `-`. If the number itself is zero, the number of digits is defined to be 1) |

## Compiling the assembly

To compile assembly source code run:

```bash
python3.9 compile.py /path/to/src.alan
```

This will create a file called `src.tur` which contains turing machine instructions of the form

&Delta;(`current_state`,`observed_symbol`) = (`replaced_symbol`,&larr; or &rarr;,`new_state`)


With one instruction per line.

In future versions this output will also optionally be available in JSON format.

## Running compiled code

The output `.tur` file can be executed using either of the two Turing machine simulators contained within this repo.

### Graphical user interface

One of them is graphical and grants you much more control over the execution of the program. It can be run with:

```bash
python3.9 gui.py /path/to/executable.tur
```

To run the program with an initially empty tape, or

```bash
python3.9 gui.py /path/to/executable.tur "1234;5678"
```

To start with the numbers 1234 and 5678 on the tape. These will automatically be put (in order) onto the stack, and so can be thought of as arguments to the executable.

### Command line interpreter

The other simulator is entirely in the command line and it is much faster. It can be run with:

```bash
python3.9 cli.py /path/to/executable.tur
```

To run the program with an initially empty tape, or

```bash
python3.9 cli.py /path/to/executable.tur "1234;5678"
```

To start with the numbers 1234 and 5678 on the tape. These will automatically be put (in order) onto the stack, and so can be thought of as arguments to the executable.