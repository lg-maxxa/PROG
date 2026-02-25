# PROG

**PROG** is a simple, open-source programming language designed for AI model training data. Its clean, minimal syntax makes it easy to tokenise, parse, and learn from — ideal as a training corpus or as a target language for generative models.

---

## Features

- Simple, consistent syntax — no implicit semicolons, no special characters
- First-class functions with lexical (closure) scoping
- Integer and floating-point arithmetic
- String concatenation with `+`
- Boolean logic (`and`, `or`, `not`)
- `if / then / else / end` conditionals
- `while / do / end` loops
- Recursion supported out of the box
- **List literals** `[1, 2, 3]` with indexing and built-in list operations
- **Built-in functions**: `len`, `type`, `str`, `int`, `float`, `abs`, `max`, `min`, `append`, `pop`, `input`
- Single-line comments with `#`
- Implemented as a pure-Python tree-walking interpreter — easy to study and extend

---

## Installation

Follow these steps exactly to get PROG running on your machine.

### Step 1 — Check Python version

PROG requires **Python 3.10 or newer**.

```bash
python --version
# Should print Python 3.10.x or higher
```

If you need to upgrade, download Python from <https://python.org>.

### Step 2 — Clone the repository

```bash
git clone https://github.com/lg-maxxa/PROG.git
cd PROG
```

### Step 3 — Install PROG

```bash
pip install -e .
```

This installs the `prog` command into your Python environment.  
The `-e` flag means changes to the source take effect immediately (editable install).

### Step 4 — Verify the installation

```bash
prog --help        # or: python -m prog --help
```

You should see no errors. If `prog` is not found, try `python -m prog` instead.

---

## Running PROG Programs

### Run a `.prog` file

```bash
prog examples/hello.prog
```

Expected output:

```
Hello, World!
```

### Run any example program

```bash
prog examples/fibonacci.prog
prog examples/fizzbuzz.prog
prog examples/functions.prog
prog examples/lists.prog
prog examples/builtins.prog
```

### Start the interactive REPL

```bash
prog
```

The REPL greets you with a banner and a `>>>` prompt.  
Type any PROG expression or statement and press **Enter**:

```
>>> print "Hello!"
Hello!
>>> let x = 6 * 7
>>> print x
42
>>> exit
```

You can also run a `.prog` file from within the REPL using the `run` command:

```
>>> run examples/hello.prog
Hello, World!
```

Press **Ctrl-D** (Linux/macOS) or **Ctrl-Z** then **Enter** (Windows) to quit.

---

## Language Reference

### Comments

```
# This is a comment
let x = 42  # inline comment
```

### Variables

Variables are declared (and reassigned) with `let`:

```
let name = "Alice"
let score = 100
let active = true
let nothing = nil
```

### Data Types

| Type    | Examples                    |
|---------|-----------------------------|
| Number  | `0`, `42`, `3.14`, `.5`, `5.` |
| String  | `"hello"`, `""`             |
| Boolean | `true`, `false`             |
| Nil     | `nil`                       |
| List    | `[1, 2, 3]`, `["a", "b"]`  |

### Arithmetic

```
let a = 10 + 3   # 13
let b = 10 - 3   # 7
let c = 10 * 3   # 30
let d = 10 / 3   # 3.333...
let e = 10 % 3   # 1
let f = -a       # -13
```

String concatenation:

```
let msg = "Hello, " + "World!"   # "Hello, World!"
let info = "Score: " + 42        # "Score: 42"
```

### Comparisons

```
1 == 1   # true
1 != 2   # true
3 <  5   # true
3 <= 3   # true
5 >  3   # true
5 >= 6   # false
```

### Boolean Logic

```
true and false   # false
false or true    # true
not true         # false
```

`and` and `or` short-circuit: the right side is only evaluated when necessary.

### Print

```
print "hello"
print 42
print x
```

### If / Else

```
if score >= 90 then
  print "A"
else
  if score >= 80 then
    print "B"
  else
    print "C"
  end
end
```

### While Loop

```
let i = 1
while i <= 5 do
  print i
  let i = i + 1
end
```

### Functions

```
func greet(name)
  print "Hello, " + name + "!"
end

func add(a, b)
  return a + b
end

greet("Alice")
let result = add(3, 4)
print result
```

Functions support recursion:

```
func factorial(n)
  if n <= 1 then
    return 1
  end
  return n * factorial(n - 1)
end

print factorial(10)
```

### Lists

Create a list with square brackets:

```
let nums = [1, 2, 3, 4, 5]
```

Access elements by zero-based index:

```
print nums[0]   # 1
print nums[4]   # 5
```

Lists can be nested:

```
let grid = [[1, 2], [3, 4]]
print grid[0][1]   # 2
```

### Built-in Functions

| Function         | Description                                   | Example                        |
|------------------|-----------------------------------------------|--------------------------------|
| `len(x)`         | Length of a string or list                    | `len("hi")` → `2`             |
| `type(x)`        | Runtime type name as a string                 | `type(42)` → `"int"`          |
| `str(x)`         | Convert any value to a string                 | `str(3.14)` → `"3.14"`        |
| `int(x)`         | Convert a number or numeric string to integer | `int("7")` → `7`              |
| `float(x)`       | Convert to floating-point number              | `float("3.14")` → `3.14`      |
| `abs(x)`         | Absolute value                                | `abs(-5)` → `5`               |
| `max(a, b, ...)` | Largest of the arguments (or a list)          | `max(1, 9, 3)` → `9`          |
| `min(a, b, ...)` | Smallest of the arguments (or a list)         | `min(1, 9, 3)` → `1`          |
| `append(lst, v)` | Append value to list in-place, return list    | `append(nums, 6)`             |
| `pop(lst)`       | Remove and return last element of list        | `pop(nums)` → last item        |
| `input(prompt)`  | Read a line of user input                     | `let name = input("Name: ")`  |

---

## Example Programs

The `examples/` directory contains ready-to-run programs:

| File               | Description                        |
|--------------------|------------------------------------|
| `hello.prog`       | Classic "Hello, World!"            |
| `fibonacci.prog`   | First 10 Fibonacci numbers         |
| `fizzbuzz.prog`    | FizzBuzz up to 20                  |
| `functions.prog`   | User-defined functions & recursion |
| `lists.prog`       | List literals, indexing, operations|
| `builtins.prog`    | Built-in function showcase         |

---

## Project Structure

```
PROG/
├── src/
│   └── prog/
│       ├── __init__.py       # package & version
│       ├── __main__.py       # CLI entry point (python -m prog)
│       ├── lexer.py          # tokeniser
│       ├── parser.py         # AST parser
│       └── interpreter.py   # tree-walking evaluator
├── examples/                 # sample .prog programs
├── tests/                    # pytest test suite
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_interpreter.py
├── pyproject.toml
└── LICENSE
```

---

## Running Tests

### Step 1 — Install pytest

```bash
pip install pytest
```

### Step 2 — Run the test suite

```bash
python -m pytest tests/ -v
```

All tests should pass.  
The `-v` flag prints each test name so you can see exactly what is being verified.

---

## License

Apache 2.0 — see [LICENSE](LICENSE).

