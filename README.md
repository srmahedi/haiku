# Haiku Programming Language

**Haiku** is a modern, expressive programming language designed to be **simpler than Python** while remaining powerful enough for real-world tasks. Haiku features clean syntax, f-strings for easy string interpolation, module imports, first-class functions, object-oriented programming, pattern matching, and a rich standard library.

## What's New in Haiku 1.0 (Production-Ready)

### Major New Features

**Essential Systems:**
- **Real File I/O**: Read/write actual files from disk (`File` module)
- **HTTP Client**: Make HTTP requests to web APIs (`HTTP` module)
- **Threading**: Multi-threaded programming support (`Thread` module)
- **Async/Await**: Asynchronous programming support (`Async` module)
- **Database**: SQLite database connectivity (`DB` module)
- **Testing Framework**: Built-in testing tools (`Test` module)
- **Package Manager**: Install and manage packages (`Pkg` module)
- **GUI Module**: Create graphical user interfaces with Qt/PySide6 (`GUI` module)

**New Data Structures:**
- **Sets**: `#{1, 2, 3}` - unordered unique collections
- **Tuples**: `(1, 2, 3)` - immutable ordered collections
- **Enums**: `enum Name { VALUE1, VALUE2 }` - compile-time constants

**New Standard Library Modules:**
- **Regex**: Regular expressions (`Regex` module)
- **Date**: Date/time manipulation (`Date` module)
- **Compress**: ZIP and GZIP compression (`Compress` module)
- **XML**: XML parsing and generation (`XML` module)

### Haiku 2.0 Features
- **F-strings**: Easy string interpolation with `f"Hello {name}"`
- **R-strings**: Raw strings for regex and paths with `r"C:\\path\\to\\file"`
- **Module imports**: Import custom `.hku` files and built-in modules
- **Simpler syntax**: Cleaner, more intuitive than Python
- **Error tracebacks**: Full call-stack traceback with exact line numbers on every runtime error
- **Unclosed comment detection**: `/* ... */` comments that are never closed now raise a clear `LexerError` instead of silently skipping code

### Latest Updates
- **Distinct `int` and `float` types**: Whole numbers (e.g. `5`) now report type `"int"` and decimal numbers (e.g. `5.5`) report type `"float"` — `type(5)` → `"int"`, `type(5.5)` → `"float"`

- **File Extension**: `.hku`
- **Base Language**: Python (interpreter written in Python)
- **Paradigm**: Multi-paradigm (procedural, object-oriented, functional)

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Language Syntax](#language-syntax)
3. [F-Strings & R-Strings](#f-strings--r-strings)
4. [Imports](#imports)
5. [Data Types](#data-types)
6. [Variables & Constants](#variables--constants)
7. [Operators](#operators)
8. [Control Flow](#control-flow)
9. [Functions](#functions)
10. [Object-Oriented Programming](#object-oriented-programming)
11. [Collections](#collections)
12. [Standard Library](#standard-library)
13. [Error Handling](#error-handling)
14. [Running Haiku](#running-haiku)
15. [Project Structure](#project-structure)
16. [Complete Example Programs](#complete-example-programs)

---

## Quick Start

```haiku
// Hello World in Haiku with f-strings
println("Hello, World!")

let name = "Haiku"
let version = 1.0

// Use f-strings for cleaner string interpolation
println(f"Language: {name}")
println(f"Version: {version}")
```

Run it:
```bash
python main.py hello.hku
```

Or use the interactive REPL:
```bash
python main.py
haiku> println(2 + 2)
4
```

---

## Language Syntax

### Comments
```haiku
// Single-line comment

/*
   Multi-line
   comment
*/
```

### Identifiers
- Must start with a letter or underscore
- Can contain letters, digits, and underscores
- Case-sensitive

### Keywords
```
let, const, fn, if, else, elif, for, while, return
class, this, super, import, from, as, true, false, none
and, or, not, try, catch, finally, throw, match, case
default, break, continue, in, async, await, yield
static, private, public, enum
```

---

## F-Strings & R-Strings

### F-Strings (Formatted Strings)
F-strings provide an easy way to embed expressions inside string literals using curly braces.

```haiku
let name = "Alice"
let age = 30

// Simple interpolation
println(f"Hello, {name}!")
println(f"You are {age} years old")

// Expressions inside f-strings
println(f"Next year you'll be {age + 1}")

// Method calls
let text = "hello world"
println(f"Uppercase: {text.upper()}")

// Escaped braces
println(f"Literal braces: {{ and }}")
```

### R-Strings (Raw Strings)
R-strings treat backslashes as literal characters, perfect for regex patterns and file paths.

```haiku
// Regex pattern (no need to double-escape)
let pattern = r"\d+\w+"

// File paths (Windows-style)
let path = r"C:\Users\Documents\file.txt"

// Raw text with backslashes
let raw = r"Line 1\nLine 2\nLine 3"
println(raw)  // Prints: Line 1\nLine 2\nLine 3
```

---

## Imports

Haiku supports importing from custom `.hku` files and built-in modules.

### Import Built-in Modules
```haiku
// Import entire module
import Math
println(f"PI = {Math.PI}")
println(f"sqrt(16) = {Math.sqrt(16)}")

// Import Time module
import Time
let now = Time.now()
println(f"Timestamp: {now}")
```

### Import Custom .hku Files
```haiku
// Import from a custom file
import { greet, farewell } from 'my_module.hku'

greet("Alice")
farewell("Bob")

// Import entire module with alias
import 'utils.hku' as Utils
Utils.helperFunction()

// Import all exports
import * from 'helpers.hku'
```

### Creating Importable Modules
Create a file `my_module.hku`:
```haiku
// my_module.hku
let version = "1.0"

fn greet(name) {
    return f"Hello, {name}!"
}

fn farewell(name) {
    return f"Goodbye, {name}!"
}
```

Then import it in another file:
```haiku
import { greet, farewell, version } from 'my_module.hku'
println(greet("World"))
println(f"Module version: {version}")
```

---

## Data Types

### Primitive Types

| Type | Example | `type()` returns | Description |
|------|---------|-----------------|-------------|
| `int` | `42`, `0`, `-7` | `"int"` | Whole numbers |
| `float` | `3.14`, `19.99` | `"float"` | Decimal / floating-point numbers |
| `string` | `"hello"`, `'world'` | `"string"` | Text with escape sequences |
| `boolean` | `true`, `false` | `"boolean"` | Logical values |
| `none` | `none` | `"none"` | Absence of value |

```haiku
let count = 42       // int
let price = 19.99    // float
let message = "Hello" // string
let active = true    // boolean
let empty = none     // none

println(type(count))    // int
println(type(price))    // float
println(type(message))  // string
println(type(active))   // boolean
println(type(empty))    // none
```

### Collection Types

**List** - ordered, mutable sequence:
```haiku
let fruits = ["apple", "banana", "cherry"]
let numbers = [1, 2, 3, 4, 5]
```

**Map** - key-value dictionary:
```haiku
let scores = {
    "alice": 95,
    "bob": 87,
    "charlie": 92
}
```

**Set** - unordered unique collection:
```haiku
let uniqueNumbers = #{1, 2, 3, 2, 1}  // #{1, 2, 3}
let colors = #{"red", "green", "blue"}
```

**Tuple** - immutable ordered collection:
```haiku
let coordinates = (10, 20)
let person = ("Alice", 30, "Engineer")
```

---

## Variables & Constants

```haiku
// Mutable variable
let name = "Alice"
name = "Bob"  // OK

// Immutable constant
const PI = 3.14159
// PI = 3.14  // ERROR!
```

Variables are block-scoped. Functions and classes create new scopes.

---

## Operators

### Arithmetic
```haiku
a + b    // Addition (also string concatenation, list concatenation)
a - b    // Subtraction
a * b    // Multiplication (also string repetition)
a / b    // Division
a % b    // Modulo
a ** b   // Power
```

### Comparison
```haiku
a == b   // Equal
a != b   // Not equal
a < b    // Less than
a > b    // Greater than
a <= b   // Less than or equal
a >= b   // Greater than or equal
```

### Logical
```haiku
a && b   // Logical AND (short-circuit)
a || b   // Logical OR (short-circuit)
!a       // Logical NOT
not a    // Alternative NOT
```

### Bitwise
```haiku
a & b    // Bitwise AND
a | b    // Bitwise OR
a ^ b    // Bitwise XOR
a << b   // Left shift
a >> b   // Right shift
~a       // Bitwise NOT
```

### Assignment
```haiku
a = b
a += b
a -= b
a *= b
a /= b
```

### Range
```haiku
1..5     // Creates [1, 2, 3, 4, 5]
```

### Ternary
```haiku
let status = age >= 18 ? "adult" : "minor"
```

### Optional Chaining
```haiku
obj?.property   // Returns none if obj is none instead of error
```

---

## Control Flow

### If / Elif / Else
```haiku
let score = 85

if score >= 90 {
    println("Grade: A")
} elif score >= 80 {
    println("Grade: B")
} elif score >= 70 {
    println("Grade: C")
} else {
    println("Grade: F")
}
```

### For Loop
```haiku
for i in range(1, 6) {
    println(i)
}

for fruit in ["apple", "banana", "cherry"] {
    println(fruit)
}

for key in {"a": 1, "b": 2} {
    println(key)
}
```

### While Loop
```haiku
let n = 5
let fact = 1
while n > 1 {
    fact = fact * n
    n = n - 1
}
println(f"5! = {fact}")
```

### Match (Pattern Matching)
```haiku
let day = "monday"
match day {
    "monday" => println("Start of week")
    "friday" => println("End of week")
    "saturday" => println("Weekend!")
    "sunday" => println("Weekend!")
    default => println("Midweek")
}
```

### Break & Continue
```haiku
for i in range(1, 10) {
    if i == 3 {
        continue
    }
    if i == 7 {
        break
    }
    println(i)
}
```

---

## Functions

### Function Declaration
```haiku
fn greet(name) {
    return f"Hello, {name}!"
}

println(greet("Haiku"))
```

### Default Parameters
```haiku
fn greetWithTitle(name, title = "Mr./Ms.") {
    return f"Hello, {title} {name}"
}

println(greetWithTitle("Smith"))        // Hello, Mr./Ms. Smith
println(greetWithTitle("Doe", "Dr."))   // Hello, Dr. Doe
```

### Lambda Functions
```haiku
let multiply = (a, b) => a * b
let square = (x) => x * x

println(multiply(4, 7))   // 28
println(square(5))        // 25
```

### Anonymous Functions
```haiku
let double = fn(x) {
    return x * 2
}
```

### Recursion
```haiku
fn factorial(n) {
    if n <= 1 {
        return 1
    }
    return n * factorial(n - 1)
}

println(factorial(5))  // 120
```

### Higher-Order Functions
```haiku
fn applyTwice(fn f, x) {
    return f(f(x))
}

let addTen = (x) => x + 10
println(applyTwice(addTen, 5))  // 25
```

### Closures
```haiku
fn makeCounter() {
    let count = 0
    return () => {
        count = count + 1
        return count
    }
}

let counter = makeCounter()
println(counter())  // 1
println(counter())  // 2
println(counter())  // 3
```

---

## Object-Oriented Programming

### Classes
```haiku
class Animal {
    fn init(name) {
        this.name = name
    }

    fn speak() {
        return f"{this.name} makes a sound"
    }
}

let animal = Animal("Creature")
println(animal.speak())
```

### Inheritance
```haiku
class Dog(Animal) {
    fn init(name, breed) {
        super.init(name)
        this.breed = breed
    }

    fn speak() {
        return f"{this.name} barks!"
    }

    fn info() {
        return f"{super.info()} ({this.breed})"
    }
}

let dog = Dog("Buddy", "Golden Retriever")
println(dog.speak())
println(dog.info())
println(f"Breed: {dog.breed}")
```

### Static Methods
```haiku
class Counter {
    static fn create() {
        return Counter()
    }
}

let c = Counter.create()
```

### Enums
```haiku
enum Status {
    PENDING
    APPROVED
    REJECTED
}

let currentStatus = Status.APPROVED
println(f"Status: {currentStatus}")
```

---

## Collections

### List Operations
```haiku
let nums = [1, 2, 3, 4, 5]

nums.push(6)           // Add to end
nums.pop()             // Remove from end
nums.shift()           // Remove from start
nums.unshift(0)        // Add to start

let first = nums.get(0)
nums.set(0, 10)

let hasThree = nums.contains(3)
let doubled = nums.map((x) => x * 2)
let evens = nums.filter((x) => x % 2 == 0)
let sum = nums.reduce((acc, x) => acc + x, 0)
let sorted = nums.sort()
let reversed = nums.reverse()
let joined = nums.join(", ")
let sliced = nums.slice(1, 3)

println(f"Length: {nums.len()}")
```

### Map Operations
```haiku
let scores = {"alice": 95, "bob": 87}

println(scores["alice"])
println(f"Keys: {scores.keys()}")
println(f"Values: {scores.values()}")
println(f"Entries: {scores.entries()}")
println(f"Has 'alice': {scores.has('alice')}")

scores.delete("bob")
scores.clear()
println(f"Length: {scores.len()}")
```

### String Methods
```haiku
let text = "  Hello, Haiku!  "

text.upper()
text.lower()
text.trim()
text.split(",")
text.contains("Haiku")
text.replace("Haiku", "World")
text.startsWith("Hello")
text.endsWith("!")
text.slice(0, 5)

text.len()
```

---

## Standard Library

### I/O Functions
```haiku
print("no newline")
println("with newline")

let name = input("Enter your name: ")
println(f"Hello, {name}")
```

### Type Functions
```haiku
type(value)     // Get type name as string
len(value)      // Get length of string/list/map
str(value)      // Convert to string
int(value)      // Convert to integer (truncates decimals)
float(value)    // Convert to float
bool(value)     // Convert to boolean
```

Type name reference:
```haiku
println(type(5))        // int
println(type(5.5))      // float
println(type("hello"))  // string
println(type(true))     // boolean
println(type(none))     // none
println(type([1,2,3]))  // list
println(type({"a":1}))  // map
```

### Range
```haiku
range(5)        // [0, 1, 2, 3, 4]
range(1, 6)     // [1, 2, 3, 4, 5]
range(0, 10, 2) // [0, 2, 4, 6, 8]
```

### Math Module
```haiku
Math.PI
Math.E
Math.TAU

Math.abs(-5)
Math.sin(x)
Math.cos(x)
Math.tan(x)
Math.sqrt(16)
Math.pow(2, 8)
Math.log(x)
Math.log10(x)
Math.exp(x)
Math.floor(3.7)
Math.ceil(3.2)
Math.round(3.5)
Math.max(10, 20, 5)
Math.min(10, 20, 5)
Math.random()
Math.randint(1, 100)
```

### Time Module
```haiku
let now = Time.now()
Time.sleep(1000)  // milliseconds
Time.format(now, "%Y-%m-%d %H:%M:%S")
```

### JSON Module
```haiku
let data = {"name": "Haiku", "version": 1.0}
let jsonStr = JSON.stringify(data)
let parsed = JSON.parse(jsonStr)
```

### File Module (Real File I/O)
```haiku
// Real file operations on disk
File.write("hello.txt", "Hello, World!")
let content = File.read("hello.txt")
println(content)

File.append("hello.txt", "\nMore text.")
println(File.exists("hello.txt"))

File.mkdir("data")
println(File.listDir("."))
println(File.isFile("hello.txt"))
println(File.isDir("data"))

File.delete("hello.txt")
```

### HTTP Module (Networking)
```haiku
// HTTP requests
let response = HTTP.get("https://api.example.com/data")
println(response)

// POST request with data
let data = {"name": "Haiku", "version": 3.0}
let result = HTTP.post("https://api.example.com/submit", data)
println(result)

// Custom request
let custom = HTTP.request("https://api.example.com", "GET", {}, {"User-Agent": "Haiku"})
```

### Thread Module (Concurrency)
```haiku
fn computeHeavyTask() {
    let sum = 0
    for i in range(1, 1000000) {
        sum = sum + i
    }
    return sum
}

let threadId = Thread.spawn(computeHeavyTask)
let result = Thread.join(threadId)
println(f"Result: {result}")

Thread.sleep(1000)  // Sleep for 1 second
```

### Async Module (Async/Await)
```haiku
fn asyncTask() {
    println("Starting async task")
    Async.sleep(500)
    println("Task completed")
    return "Done"
}

let result = Async.spawn(asyncTask)
println(result)
```

### Test Module (Testing Framework)
```haiku
Test.reset()

fn testAddition() {
    Test.assertEqual(2 + 2, 4, "Addition failed")
    Test.assertTrue(5 > 3, "Comparison failed")
}

fn testStrings() {
    Test.assertEqual("hello" + " world", "hello world", "String concat failed")
}

Test.run(testAddition)
Test.run(testStrings)

let results = Test.results()
println(f"Passed: {results['passed']}")
println(f"Failed: {results['failed']}")
```

### Pkg Module (Package Manager)
```haiku
// Search for packages
let results = Pkg.search("http")
println(results)

// Install a package
Pkg.install("http-client")

// List installed packages
let installed = Pkg.list()
println(installed)

// Remove a package
Pkg.remove("http-client")
```

### Regex Module (Regular Expressions)
```haiku
let text = "Hello, World! 123"

// Match pattern
let hasNumber = Regex.match(r"\d+", text)
println(f"Has number: {hasNumber}")

// Find all matches
let numbers = Regex.findAll(r"\d+", text)
println(f"Numbers: {numbers}")

// Replace
let replaced = Regex.replace(r"\d+", "XXX", text)
println(f"Replaced: {replaced}")

// Split
let parts = Regex.split(r",\s*", "a, b, c")
println(f"Parts: {parts}")
```

### Date Module (Date/Time Manipulation)
```haiku
// Current time
let now = Date.now()
println(f"Now: {now}")

// Parse date
let parsed = Date.parse("2024-01-15T10:30:00")
println(f"Year: {parsed['year']}")
println(f"Month: {parsed['month']}")

// Format date
let formatted = Date.format("2024-01-15", "%Y-%m-%d")
println(f"Formatted: {formatted}")

// Add days
let future = Date.addDays("2024-01-15", 7)
println(f"Next week: {future}")

// Add hours
let later = Date.addHours("2024-01-15T10:00:00", 5)
println(f"5 hours later: {later}")
```

### Compress Module (ZIP/GZIP)
```haiku
// GZIP compression
let data = "Hello, World! This is a test string."
let compressed = Compress.gzipCompress(data)
println(f"Compressed: {compressed}")

let decompressed = Compress.gzipDecompress(compressed)
println(f"Decompressed: {decompressed}")

// ZIP archive
let files = {
    "file1.txt": "Content of file 1",
    "file2.txt": "Content of file 2"
}
let zipData = Compress.zipCreate(files)
let extracted = Compress.zipExtract(zipData)
println(f"Extracted: {extracted}")
```

### DB Module (SQLite Database)
```haiku
// Connect to database
let conn = DB.connect(":memory:")

// Create table
DB.execute(conn, "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)")

// Insert data
DB.execute(conn, "INSERT INTO users (name, age) VALUES (?, ?)", ["Alice", 30])
DB.execute(conn, "INSERT INTO users (name, age) VALUES (?, ?)", ["Bob", 25])

// Query data
let results = DB.execute(conn, "SELECT * FROM users")
println(f"Users: {results}")

// Update data
DB.execute(conn, "UPDATE users SET age = ? WHERE name = ?", [31, "Alice"])

// Close connection
DB.close(conn)
```

### XML Module (XML Parsing)
```haiku
// Parse XML
let xmlStr = "<root><user><name>Alice</name><age>30</age></user></root>"
let parsed = XML.parse(xmlStr)
println(f"Tag: {parsed['tag']}")
println(f"Text: {parsed['text']}")
println(f"Children: {parsed['children']}")

// Convert back to XML
let xmlBack = XML.toString(parsed)
println(f"XML: {xmlBack}")
```

### GUI Module (Graphical User Interface)

Haiku provides a comprehensive GUI module built on PySide6/Qt, covering ~90-95% of common GUI use cases while maintaining a simplified API.

```haiku
// Create GUI applications using PySide6/Qt
import GUI

// Initialize the GUI application
GUI.init()

// Create a window
let window = GUI.createWindow("My App", 400, 300)

// Add widgets
GUI.addLabel(window, "Hello, GUI!")
GUI.addTextInput(window, "Enter text...")

// Add button with callback
fn onButtonClick() {
    GUI.messageBox("Info", "Button clicked!", "info")
}
GUI.addButton(window, "Click Me", onButtonClick)

// Show and run
GUI.showWindow(window)
GUI.run()
```

#### Core GUI Functions
- `GUI.init()` - Initialize the Qt application
- `GUI.createWindow(title, width, height)` - Create a new window
- `GUI.createWindowWithGrid(title, width, height, rows, cols)` - Create window with grid layout
- `GUI.showWindow(window_id)` - Show a window
- `GUI.closeWindow(window_id)` - Close a window
- `GUI.run()` - Start the GUI event loop

#### Basic Widgets
- `GUI.addLabel(window_id, text)` - Add a label
- `GUI.addButton(window_id, text, callback)` - Add a button with callback
- `GUI.addTextInput(window_id, placeholder)` - Add a text input field
- `GUI.addTextArea(window_id, text)` - Add a multi-line text area
- `GUI.addCheckbox(window_id, text, checked)` - Add a checkbox
- `GUI.addCombobox(window_id, items)` - Add a dropdown combobox
- `GUI.addSlider(window_id, min, max, initial)` - Add a slider
- `GUI.addProgressBar(window_id, value)` - Add a progress bar
- `GUI.addRadioButton(window_id, text, checked)` - Add a radio button
- `GUI.addListWidget(window_id, items)` - Add a list widget

#### Advanced Widgets
- `GUI.addTreeWidget(window_id)` - Add tree widget
- `GUI.addTableWidget(window_id, rows, cols)` - Add table widget
- `GUI.addTabWidget(window_id)` - Add tab widget
- `GUI.addTabToTabWidget(window_id, tab_index, title)` - Add tab to tab widget
- `GUI.addScrollArea(window_id, content)` - Add scroll area
- `GUI.addGroupBox(window_id, title)` - Add group box
- `GUI.addFrame(window_id, shape)` - Add frame widget
- `GUI.addSplitter(window_id, orientation)` - Add splitter widget
- `GUI.addDockWidget(window_id, title)` - Add dock widget
- `GUI.addStackedWidget(window_id)` - Add stacked widget
- `GUI.addSpinBox(window_id, min, max, initial)` - Add spin box
- `GUI.addDoubleSpinBox(window_id, min, max, initial)` - Add double spin box
- `GUI.addDateEdit(window_id)` - Add date edit widget
- `GUI.addTimeEdit(window_id)` - Add time edit widget
- `GUI.addLCDNumber(window_id, value)` - Add LCD number display
- `GUI.addDial(window_id, min, max, initial)` - Add dial widget
- `GUI.addCalendarWidget(window_id)` - Add calendar widget
- `GUI.addToolButton(window_id, text, callback)` - Add tool button
- `GUI.addCommandLinkButton(window_id, text, description, callback)` - Add command link button
- `GUI.addImageLabel(window_id, image_path)` - Add image label
- `GUI.addScrollBar(window_id, orientation)` - Add scroll bar

#### Widget Operations
- `GUI.getInput(window_id, widget_index)` - Get text from a widget
- `GUI.setText(window_id, widget_index, text)` - Set text for a widget
- `GUI.setWidgetEnabled(window_id, widget_index, enabled)` - Enable/disable widget
- `GUI.setWidgetVisible(window_id, widget_index, visible)` - Show/hide widget
- `GUI.removeWidget(window_id, widget_index)` - Remove widget from layout
- `GUI.setWidgetSize(window_id, widget_index, width, height)` - Set widget size
- `GUI.setWidgetFont(window_id, widget_index, family, size, bold)` - Set widget font
- `GUI.setWidgetColor(window_id, widget_index, part, color)` - Set widget color
- `GUI.setWidgetStyle(window_id, widget_index, css)` - Set widget CSS style
- `GUI.setTooltip(window_id, widget_index, text)` - Set widget tooltip
- `GUI.setTextAlignment(window_id, widget_index, alignment)` - Set text alignment

#### Window Management
- `GUI.setWindowTitle(window_id, title)` - Set window title
- `GUI.setWindowSize(window_id, width, height)` - Set window size
- `GUI.setWindowPosition(window_id, x, y)` - Set window position
- `GUI.setWindowOpacity(window_id, opacity)` - Set window opacity (0.0-1.0)
- `GUI.maximizeWindow(window_id)` - Maximize window
- `GUI.minimizeWindow(window_id)` - Minimize window
- `GUI.fullscreenWindow(window_id)` - Toggle fullscreen
- `GUI.hideWindow(window_id)` - Hide window
- `GUI.showNormalWindow(window_id)` - Show in normal state
- `GUI.setWindowIcon(window_id, icon_path)` - Set window icon

#### Layouts
- `GUI.createHorizontalLayout(id)` - Create horizontal layout
- `GUI.createVerticalLayout(id)` - Create vertical layout
- `GUI.createGridLayout(id, rows, cols)` - Create grid layout
- `GUI.createFormLayout(id)` - Create form layout
- `GUI.setWindowLayout(window_id, layout_id)` - Set layout for window
- `GUI.setLayoutSpacing(window_id, spacing)` - Set layout spacing
- `GUI.setLayoutMargins(window_id, left, top, right, bottom)` - Set layout margins
- `GUI.addStretch(window_id, stretch)` - Add stretchable space
- `GUI.addSpacing(window_id, size)` - Add fixed spacing
- `GUI.addToGrid(window_id, widget_type, text, callback, row_span, col_span)` - Add widget to grid

#### Dialogs
- `GUI.messageBox(title, message, type)` - Show message dialog
- `GUI.fileDialog(type, title, filter)` - Show file dialog (open/save/directory)
- `GUI.colorDialog()` - Show color picker dialog
- `GUI.fontDialog()` - Show font picker dialog
- `GUI.inputDialog(title, label, default)` - Show input dialog
- `GUI.showProgressDialog(title, text, maximum)` - Show progress dialog
- `GUI.updateProgressDialog(dialog_id, value)` - Update progress dialog
- `GUI.closeProgressDialog(dialog_id)` - Close progress dialog

#### Menu and Toolbar
- `GUI.addMenuBar(window_id)` - Add menu bar to window
- `GUI.addMenu(menu_bar_id, name)` - Add menu to menu bar
- `GUI.addMenuItem(menu_id, name, callback)` - Add menu item
- `GUI.addMenuSeparator(menu_id)` - Add menu separator
- `GUI.addToolBar(window_id, name)` - Add toolbar to window
- `GUI.addToolBarAction(toolbar_id, name, callback)` - Add toolbar action
- `GUI.addStatusBar(window_id)` - Add status bar to window
- `GUI.setStatusBarText(status_bar_id, text)` - Set status bar text

#### Timers
- `GUI.createTimer(interval, callback)` - Create timer
- `GUI.startTimer(timer_id)` - Start timer
- `GUI.stopTimer(timer_id)` - Stop timer

#### Stylesheets and Themes
- `GUI.setStylesheet(window_id, css)` - Apply CSS-like stylesheet
- `GUI.setStyle(style)` - Set application style (e.g., "Fusion")
- `GUI.setTheme(window_id, theme_name)` - Set application theme

#### MDI (Multiple Document Interface)
- `GUI.setMDIMode(window_id)` - Enable MDI mode
- `GUI.addMDISubwindow(window_id, title)` - Add MDI subwindow

#### Rich Text Editing
- `GUI.addRichTextEdit(window_id, html_content)` - Add rich text editor
- `GUI.setRichText(window_id, widget_index, html)` - Set HTML content

#### Graphics and Painting
- `GUI.addGraphicsView(window_id)` - Add graphics view for custom painting
- `GUI.drawRectangle(graphics_id, x, y, width, height, color)` - Draw rectangle
- `GUI.drawEllipse(graphics_id, x, y, width, height, color)` - Draw ellipse
- `GUI.drawLine(graphics_id, x1, y1, x2, y2, color, width)` - Draw line
- `GUI.drawText(graphics_id, text, x, y, color)` - Draw text
- `GUI.animateColor(graphics_id, widget_index, duration, from_color, to_color)` - Animate color
- `GUI.animateRotation(graphics_id, widget_index, duration, from_angle, to_angle)` - Animate rotation
- `GUI.animateScale(graphics_id, widget_index, duration, from_scale, to_scale)` - Animate scale
- `GUI.animatePixmapSequence(graphics_id, widget_index, duration, images)` - Animate pixmap sequence

#### Web Integration
- `GUI.addWebView(window_id, url)` - Add web browser widget (requires PySide6-WebEngine)

#### Data Visualization
- `GUI.addPlotWidget(window_id)` - Add matplotlib plot widget (requires matplotlib)

#### Clipboard and System Tray
- `GUI.copyToClipboard(text)` - Copy text to clipboard
- `GUI.pasteFromClipboard()` - Paste text from clipboard
- `GUI.clearClipboard()` - Clear clipboard
- `GUI.addSystemTrayIcon(icon_path)` - Add system tray icon
- `GUI.showSystemTrayMessage(title, message)` - Show system tray notification
- `GUI.addSystemTrayMenu(menu_id)` - Add menu to system tray

#### Table and Tree Operations
- `GUI.setTableHeader(window_id, widget_index, headers)` - Set table headers
- `GUI.setTableItem(window_id, widget_index, row, col, text)` - Set table cell
- `GUI.getTableItem(window_id, widget_index, row, col)` - Get table cell
- `GUI.addTreeItem(window_id, widget_index, parent, text)` - Add tree item
- `GUI.setTreeItemText(window_id, widget_index, item, text)` - Set tree item text

#### Input Validation
- `GUI.setInputValidator(window_id, widget_index, validator_type)` - Set input validator
- `GUI.setInputMask(window_id, widget_index, mask)` - Set input mask

#### Event Handling
- `GUI.setWidgetCallback(window_id, widget_index, event_type, callback)` - Set widget event callback
- Supported events: `clicked`, `changed`, `return_pressed`, `value_changed`, `current_changed`

#### Drag and Drop
- `GUI.enableDragDrop(window_id, widget_index)` - Enable drag and drop for widget
- `GUI.setDragDropMode(window_id, widget_index, mode)` - Set drag/drop mode

#### Advanced Combo Box and Spin Box
- `GUI.addComboBoxAdvanced(window_id, items, editable)` - Add advanced combo box
- `GUI.addSpinBoxAdvanced(window_id, type, min, max, initial, step, suffix)` - Add advanced spin box
- `GUI.addSliderAdvancedWithCallback(window_id, orientation, min, max, initial, callback)` - Add slider with callback
- `GUI.addProgressBarAdvanced(window_id, orientation, min, max, initial, text_visible, format)` - Add advanced progress bar

#### Window States
- `GUI.getWindowState(window_id)` - Get window state
- `GUI.setWindowState(window_id, state)` - Set window state

#### Advanced Features
- `GUI.setStyle(style)` - Set application style (e.g., "Fusion")
- `GUI.widgetRepaint(window_id, widget_index)` - Force widget repaint
- `GUI.widgetUpdate(window_id, widget_index)` - Force widget update
- `GUI.getWidgetGeometry(window_id, widget_index)` - Get widget geometry
- `GUI.setWidgetGeometry(window_id, widget_index, x, y, width, height)` - Set widget geometry

**Note:** Requires PySide6 to be installed (`pip install PySide6 matplotlib PySide6-WebEngine`)

### Assertions
```haiku
assert(2 + 2 == 4, "Math still works")
```

---

## Error Handling

### try / catch / finally
```haiku
try {
    let x = 10
    let y = 0
    if y == 0 {
        throw "Cannot divide by zero!"
    }
    println(f"Result: {x / y}")
} catch e {
    println(f"Caught error: {e}")
} finally {
    println("Cleanup complete")
}
```

### throw
Use `throw` to raise an error from anywhere:
```haiku
fn divide(a, b) {
    if b == 0 {
        throw "Division by zero"
    }
    return a / b
}
```

### Error Tracebacks
When an unhandled error occurs, Haiku prints a full **call-stack traceback** with the exact line number where the error happened and every function call that led to it.

Example program (`bad_math.hku`):
```haiku
fn divide(a, b) {
    return a / b        // line 2 — error happens here
}

fn calc(x) {
    return divide(x, 0) // line 6
}

fn main() {
    let v = calc(10)    // line 10
}

main()                  // line 13
```

Output:
```
Traceback (most recent call last):
  at line 13 in fn 'main'
  at line 10 in fn 'calc'
  at line 6 in fn 'divide'
RuntimeError at line 2: Division by zero
```

The traceback reads **bottom-up** — the last line is where the error actually occurred, and the frames above it show the call chain that got there.

### Catching the error message
The `catch` variable receives the error message string:
```haiku
try {
    let result = 1 / 0
} catch err {
    println(f"Handled: {err}")   // Handled: Division by zero
}
```

### Unclosed Block Comments
If a `/* ... */` block comment is never closed, Haiku raises a clear error instead of silently swallowing the rest of the file:
```haiku
/* this comment is never closed
println("this line is NOT skipped — you get an error instead")
```
```
LexerError: Unterminated block comment starting at line 1
```

---

## Running Haiku

### Run a File
```bash
python main.py script.hku
# or
python -m haiku script.hku
```

### Interactive REPL
```bash
python main.py
# or
python -m haiku
```

### Run Inline Code
```bash
python main.py -c "println(42)"
# or
python -m haiku -c "println(42)"
```

### Package Mode (`python -m haiku`)
Because the `haiku/` directory contains a `__main__.py`, the entire package can be invoked directly with `-m`. This is handy when Haiku is installed as a library or when `main.py` is not in your working directory.

```bash
# From any directory where haiku/ is importable:
python -m haiku script.hku
python -m haiku --version
python -m haiku --help
```

### From Python
```python
from haiku import run

result = run('''
let x = 10
let y = 20
println(x + y)
''')

print(result.output)   # 30
if result.error:
    print(result.error)  # formatted traceback if something went wrong
```

---

## Project Structure

```
Haiku-main/
├── main.py               # Root entry point  →  python main.py
├── icon.ico
├── README.md
├── examples/
│   ├── hello.hku
│   ├── variables.hku
│   ├── functions.hku
│   ├── collections.hku
│   ├── control_flow.hku
│   ├── classes.hku
│   ├── math.hku
│   ├── json_file.hku
│   └── advanced.hku
└── haiku/                # The language package
    ├── __init__.py       # Public API + run() helper
    ├── __main__.py       # Package entry point  →  python -m haiku
    ├── cli.py            # CLI logic (shared by main.py & __main__.py)
    ├── lexer.py          # Tokenizer
    ├── parser.py         # Recursive-descent parser
    ├── ast_nodes.py      # AST node definitions (all nodes carry line numbers)
    ├── interpreter.py    # Tree-walking interpreter + traceback engine
    ├── values.py         # Runtime value types
    └── stdlib.py         # Built-in functions and modules
```

---

## Complete Example Programs

### Example 1: FizzBuzz
```haiku
for i in range(1, 21) {
    if i % 3 == 0 && i % 5 == 0 {
        println("FizzBuzz")
    } elif i % 3 == 0 {
        println("Fizz")
    } elif i % 5 == 0 {
        println("Buzz")
    } else {
        println(i)
    }
}
```

### Example 2: Fibonacci Sequence
```haiku
fn fibonacci(n) {
    if n <= 1 {
        return n
    }
    return fibonacci(n - 1) + fibonacci(n - 2)
}

for i in range(0, 10) {
    println(f"fib({i}) = {fibonacci(i)}")
}
```

### Example 3: Working with Data
```haiku
let users = [
    {"name": "Alice", "age": 30},
    {"name": "Bob", "age": 25},
    {"name": "Charlie", "age": 35}
]

let adults = users.filter((u) => u["age"] >= 30)
println(f"Adults: {adults}")

let names = users.map((u) => u["name"])
println(f"Names: {names}")

let totalAge = users.reduce((acc, u) => acc + u["age"], 0)
println(f"Average age: {totalAge / users.len()}")
```

---

## Language Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| F-Strings | Complete | Easy string interpolation with f"text {expr}" |
| R-Strings | Complete | Raw strings for regex/paths with r"text" |
| Module Imports | Complete | Import .hku files and built-in modules |
| Lexical Analysis | Complete | Keywords, identifiers, literals, comments, operators |
| Primitive Types | Complete | `int`, `float`, `string`, `boolean`, `none` — integers and floats are distinct types |
| Collections | Complete | List, Map, Set, Tuple with rich native methods |
| Variables | Complete | let (mutable), const (immutable), block scope |
| Operators | Complete | Arithmetic, comparison, logical, bitwise, assignment, ternary |
| Control Flow | Complete | if/elif/else, for, while, match, break, continue |
| Functions | Complete | Named, anonymous, lambda, default params, variadic, closures, higher-order |
| OOP | Complete | Classes, inheritance, super, static methods, encapsulation |
| Enums | Complete | Compile-time constants with enum syntax |
| Error Handling | Complete | try/catch/finally, throw |
| Error Tracebacks | Complete | Full call-stack with exact line numbers on every runtime error |
| Unclosed Comment Detection | Complete | `/* */` that is never closed raises LexerError with line number |
| Package Mode | Complete | `python -m haiku` works alongside `python main.py` via `haiku/__main__.py` |
| Real File I/O | Complete | Read/write actual files from disk |
| HTTP Client | Complete | Make HTTP requests to web APIs |
| Threading | Complete | Multi-threaded programming support |
| Async/Await | Complete | Asynchronous programming support |
| Database | Complete | SQLite database connectivity |
| Testing Framework | Complete | Built-in testing tools |
| Package Manager | Complete | Install and manage packages |
| Regex | Complete | Regular expressions support |
| Date/Time | Complete | Date/time manipulation |
| Compression | Complete | ZIP and GZIP compression |
| XML | Complete | XML parsing and generation |
| Standard Library | Complete | I/O, Math, Time, JSON, File, type utilities |
| String Processing | Complete | Methods: upper, lower, trim, split, contains, replace, slice |
| List Processing | Complete | Methods: push, pop, shift, map, filter, reduce, sort, find |
| Map Processing | Complete | Methods: keys, values, entries, has, delete, clear |
| Assertions | Complete | assert(condition, message) |

---

## Packaging

### 1. Compile to Executable (`PyInstaller`)
To bundle the application into exe:
```powershell
pyinstaller --onefile --icon icon.ico --name haiku main.py
```

## License

Haiku is open source. Use it, modify it, and build amazing things with it!

---

**Happy Coding in Haiku!**
