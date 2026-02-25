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
- Single-line comments with `#`
- Implemented as a pure-Python tree-walking interpreter — easy to study and extend

---

## Installation

```bash
git clone https://github.com/lg-maxxa/PROG.git
cd PROG
pip install -e .
```

Python 3.10 or newer is required.

---

## Quick Start

Create a file `hello.prog`:

```
print "Hello, World!"
```

Run it:

```bash
python -m prog hello.prog
# or, after pip install:
prog hello.prog
```

Start the interactive REPL:

```bash
prog
```

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
| Number  | `0`, `42`, `3.14`           |
| String  | `"hello"`, `""`             |
| Boolean | `true`, `false`             |
| Nil     | `nil`                       |

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

---

## Example Programs

The `examples/` directory contains ready-to-run programs:

| File               | Description                        |
|--------------------|------------------------------------|
| `hello.prog`       | Classic "Hello, World!"            |
| `fibonacci.prog`   | First 10 Fibonacci numbers         |
| `fizzbuzz.prog`    | FizzBuzz up to 20                  |
| `functions.prog`   | User-defined functions & recursion |

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

```bash
pip install pytest
python -m pytest tests/ -v
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
