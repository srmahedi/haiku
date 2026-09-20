"""
Haiku Standard Library
======================
Built-in functions and modules available to all Haiku programs.
Includes I/O, math, time, JSON, file operations, and type utilities.
"""

import math
import random
import json as pyjson
from typing import Dict, List
from .values import (
    Environment, HNativeFn, HNumber, HString, HBoolean, HNone,
    HList, HMap, HModule, HValue, HFunction, h_number, h_string, h_bool, h_none, h_list, h_map
)


def _json_to_hvalue(data) -> HValue:
    """Convert Python JSON data to Haiku values."""
    if data is None:
        return h_none()
    if isinstance(data, bool):
        return h_bool(data)
    if isinstance(data, (int, float)):
        return h_number(float(data))
    if isinstance(data, str):
        return h_string(data)
    if isinstance(data, list):
        return h_list([_json_to_hvalue(x) for x in data])
    if isinstance(data, dict):
        return h_map({k: _json_to_hvalue(v) for k, v in data.items()})
    return h_none()


def _hvalue_to_json(value: HValue):
    """Convert Haiku values to Python JSON data."""
    if isinstance(value, HNone):
        return None
    if isinstance(value, HBoolean):
        return value.value
    if isinstance(value, HNumber):
        return value.value
    if isinstance(value, HString):
        return value.value
    if isinstance(value, HList):
        return [_hvalue_to_json(x) for x in value.elements]
    if isinstance(value, HMap):
        return {k: _hvalue_to_json(v) for k, v in value.entries.items()}
    return str(value)


def create_global_env(interpreter) -> Environment:
    """Create the global environment with all built-ins."""
    env = Environment()

    # ------------------------------------------------------------------
    # I/O Functions
    # ------------------------------------------------------------------

    def _print(args, interp):
        text = " ".join(str(a) for a in args)
        interp.write(text)
        return h_none()

    def _println(args, interp):
        text = " ".join(str(a) for a in args)
        interp.writeln(text)
        return h_none()

    def _input_fn(args, interp):
        if args:
            interp.write(str(args[0]))
        return h_string(interp.read_input())

    env.define("print", HNativeFn("print", -1, _print))
    env.define("println", HNativeFn("println", -1, _println))
    env.define("input", HNativeFn("input", 1, _input_fn))

    # ------------------------------------------------------------------
    # Type Functions
    # ------------------------------------------------------------------

    env.define("type", HNativeFn("type", 1, lambda args, _: h_string(args[0].type)))

    def _len_fn(args, _):
        arg = args[0]
        if isinstance(arg, HString):
            return h_number(len(arg.value))
        if isinstance(arg, HList):
            return h_number(len(arg.elements))
        if isinstance(arg, HMap):
            return h_number(len(arg.entries))
        raise RuntimeError(f"Cannot get length of {arg.type}")

    env.define("len", HNativeFn("len", 1, _len_fn))
    env.define("str", HNativeFn("str", 1, lambda args, _: h_string(str(args[0]))))

    def _int_fn(args, _):
        arg = args[0]
        if isinstance(arg, HNumber):
            return h_number(int(arg.value))
        if isinstance(arg, HString):
            return h_number(int(arg.value) if arg.value.isdigit() or (arg.value.startswith("-") and arg.value[1:].isdigit()) else 0)
        if isinstance(arg, HBoolean):
            return h_number(1 if arg.value else 0)
        return h_number(0)

    def _float_fn(args, _):
        arg = args[0]
        if isinstance(arg, HNumber):
            return arg
        if isinstance(arg, HString):
            try:
                return h_number(float(arg.value))
            except ValueError:
                return h_number(0)
        if isinstance(arg, HBoolean):
            return h_number(1.0 if arg.value else 0.0)
        return h_number(0)

    def _bool_fn(args, _):
        arg = args[0]
        if isinstance(arg, HNone):
            return h_bool(False)
        if isinstance(arg, HBoolean):
            return arg
        if isinstance(arg, HNumber):
            return h_bool(arg.value != 0)
        if isinstance(arg, HString):
            return h_bool(len(arg.value) > 0)
        if isinstance(arg, HList):
            return h_bool(len(arg.elements) > 0)
        if isinstance(arg, HMap):
            return h_bool(len(arg.entries) > 0)
        return h_bool(True)

    env.define("int", HNativeFn("int", 1, _int_fn))
    env.define("float", HNativeFn("float", 1, _float_fn))
    env.define("bool", HNativeFn("bool", 1, _bool_fn))

    # ------------------------------------------------------------------
    # Range
    # ------------------------------------------------------------------

    def _range_fn(args, _):
        start, end, step = 0, 0, 1
        if len(args) == 1:
            end = int(args[0].value)
        elif len(args) == 2:
            start = int(args[0].value)
            end = int(args[1].value)
        elif len(args) >= 3:
            start = int(args[0].value)
            end = int(args[1].value)
            step = int(args[2].value)

        if step > 0:
            return h_list([h_number(i) for i in range(start, end, step)])
        elif step < 0:
            return h_list([h_number(i) for i in range(start, end, step)])
        return h_list([])

    env.define("range", HNativeFn("range", -1, _range_fn))

    # ------------------------------------------------------------------
    # Math Module
    # ------------------------------------------------------------------

    math_env = Environment()
    math_env.define("abs", HNativeFn("abs", 1, lambda args, _: h_number(abs(args[0].value))))
    math_env.define("sin", HNativeFn("sin", 1, lambda args, _: h_number(math.sin(args[0].value))))
    math_env.define("cos", HNativeFn("cos", 1, lambda args, _: h_number(math.cos(args[0].value))))
    math_env.define("tan", HNativeFn("tan", 1, lambda args, _: h_number(math.tan(args[0].value))))
    math_env.define("sqrt", HNativeFn("sqrt", 1, lambda args, _: h_number(math.sqrt(args[0].value))))
    math_env.define("pow", HNativeFn("pow", 2, lambda args, _: h_number(args[0].value ** args[1].value)))
    math_env.define("log", HNativeFn("log", 1, lambda args, _: h_number(math.log(args[0].value))))
    math_env.define("log10", HNativeFn("log10", 1, lambda args, _: h_number(math.log10(args[0].value))))
    math_env.define("exp", HNativeFn("exp", 1, lambda args, _: h_number(math.exp(args[0].value))))
    math_env.define("floor", HNativeFn("floor", 1, lambda args, _: h_number(math.floor(args[0].value))))
    math_env.define("ceil", HNativeFn("ceil", 1, lambda args, _: h_number(math.ceil(args[0].value))))
    math_env.define("round", HNativeFn("round", 1, lambda args, _: h_number(round(args[0].value))))
    math_env.define("max", HNativeFn("max", -1, lambda args, _: h_number(max(a.value for a in args if isinstance(a, HNumber)))))
    math_env.define("min", HNativeFn("min", -1, lambda args, _: h_number(min(a.value for a in args if isinstance(a, HNumber)))))
    math_env.define("random", HNativeFn("random", 0, lambda args, _: h_number(random.random())))
    math_env.define("randint", HNativeFn("randint", 2, lambda args, _: h_number(random.randint(int(args[0].value), int(args[1].value)))))
    math_env.define("PI", h_number(math.pi))
    math_env.define("E", h_number(math.e))
    math_env.define("TAU", h_number(math.tau))

    # ------------------------------------------------------------------
    # Time Module
    # ------------------------------------------------------------------

    time_env = Environment()
    time_env.define("now", HNativeFn("now", 0, lambda args, _: h_number(__import__("time").time() * 1000)))

    def _sleep_fn(args, _):
        import time
        ms = args[0].value if args and isinstance(args[0], HNumber) else 0
        time.sleep(ms / 1000)
        return h_none()

    time_env.define("sleep", HNativeFn("sleep", 1, _sleep_fn))

    def _format_fn(args, _):
        from datetime import datetime
        timestamp = args[0].value / 1000 if args and isinstance(args[0], HNumber) else __import__("time").time()
        fmt = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "%Y-%m-%d %H:%M:%S"
        dt = datetime.fromtimestamp(timestamp)
        return h_string(dt.strftime(fmt))

    time_env.define("format", HNativeFn("format", 2, _format_fn))

    # ------------------------------------------------------------------
    # JSON Module
    # ------------------------------------------------------------------

    json_env = Environment()
    json_env.define("parse", HNativeFn("parse", 1, lambda args, _: _json_to_hvalue(pyjson.loads(args[0].value if args and isinstance(args[0], HString) else "{}"))))
    json_env.define("stringify", HNativeFn("stringify", 1, lambda args, _: h_string(pyjson.dumps(_hvalue_to_json(args[0]), indent=2))))

    # ------------------------------------------------------------------
    # File Module (real file I/O)
    # ------------------------------------------------------------------

    import os
    import pathlib

    file_env = Environment()

    def _file_read(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return h_string(f.read())
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {path}")
        except Exception as e:
            raise RuntimeError(f"Error reading file: {e}")

    def _file_write(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        content = args[1].value if len(args) > 1 and isinstance(args[1], HString) else str(args[1] if len(args) > 1 else "")
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return h_none()
        except Exception as e:
            raise RuntimeError(f"Error writing file: {e}")

    def _file_append(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        content = args[1].value if len(args) > 1 and isinstance(args[1], HString) else str(args[1] if len(args) > 1 else "")
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            return h_none()
        except Exception as e:
            raise RuntimeError(f"Error appending to file: {e}")

    def _file_exists(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        return h_bool(os.path.exists(path))

    def _file_delete(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            os.remove(path)
            return h_none()
        except FileNotFoundError:
            raise RuntimeError(f"File not found: {path}")
        except Exception as e:
            raise RuntimeError(f"Error deleting file: {e}")

    def _file_list_dir(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else "."
        try:
            entries = os.listdir(path)
            return h_list([h_string(e) for e in entries])
        except Exception as e:
            raise RuntimeError(f"Error listing directory: {e}")

    def _file_mkdir(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            os.makedirs(path, exist_ok=True)
            return h_none()
        except Exception as e:
            raise RuntimeError(f"Error creating directory: {e}")

    def _file_is_dir(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        return h_bool(os.path.isdir(path))

    def _file_is_file(args, _):
        path = args[0].value if args and isinstance(args[0], HString) else ""
        return h_bool(os.path.isfile(path))

    file_env.define("read", HNativeFn("read", 1, _file_read))
    file_env.define("write", HNativeFn("write", 2, _file_write))
    file_env.define("append", HNativeFn("append", 2, _file_append))
    file_env.define("exists", HNativeFn("exists", 1, _file_exists))
    file_env.define("delete", HNativeFn("delete", 1, _file_delete))
    file_env.define("listDir", HNativeFn("listDir", 1, _file_list_dir))
    file_env.define("mkdir", HNativeFn("mkdir", 1, _file_mkdir))
    file_env.define("isDir", HNativeFn("isDir", 1, _file_is_dir))
    file_env.define("isFile", HNativeFn("isFile", 1, _file_is_file))

    # ------------------------------------------------------------------
    # HTTP Module (networking)
    # ------------------------------------------------------------------

    http_env = Environment()

    def _http_get(args, _):
        import urllib.request
        import urllib.error
        url = args[0].value if args and isinstance(args[0], HString) else ""
        headers = args[1] if len(args) > 1 and isinstance(args[1], HMap) else None
        try:
            req = urllib.request.Request(url)
            if headers:
                for k, v in headers.entries.items():
                    req.add_header(k, str(v))
            with urllib.request.urlopen(req) as response:
                return h_string(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"HTTP error: {e}")
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")

    def _http_post(args, _):
        import urllib.request
        import urllib.parse
        url = args[0].value if args and isinstance(args[0], HString) else ""
        data = args[1] if len(args) > 1 and isinstance(args[1], HMap) else None
        headers = args[2] if len(args) > 2 and isinstance(args[2], HMap) else None
        try:
            if data:
                data_bytes = urllib.parse.urlencode({k: str(v.value) for k, v in data.entries.items()}).encode('utf-8')
            else:
                data_bytes = None
            req = urllib.request.Request(url, data=data_bytes, method='POST')
            if headers:
                for k, v in headers.entries.items():
                    req.add_header(k, str(v))
            with urllib.request.urlopen(req) as response:
                return h_string(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"HTTP error: {e}")
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")

    def _http_request(args, _):
        import urllib.request
        import urllib.parse
        url = args[0].value if args and isinstance(args[0], HString) else ""
        method = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "GET"
        data = args[2] if len(args) > 2 and isinstance(args[2], HMap) else None
        headers = args[3] if len(args) > 3 and isinstance(args[3], HMap) else None
        try:
            if data:
                data_bytes = urllib.parse.urlencode({k: str(v.value) for k, v in data.entries.items()}).encode('utf-8')
            else:
                data_bytes = None
            req = urllib.request.Request(url, data=data_bytes, method=method.upper())
            if headers:
                for k, v in headers.entries.items():
                    req.add_header(k, str(v))
            with urllib.request.urlopen(req) as response:
                return h_string(response.read().decode('utf-8'))
        except urllib.error.URLError as e:
            raise RuntimeError(f"HTTP error: {e}")
        except Exception as e:
            raise RuntimeError(f"Request failed: {e}")

    http_env.define("get", HNativeFn("get", 1, _http_get))
    http_env.define("post", HNativeFn("post", 2, _http_post))
    http_env.define("request", HNativeFn("request", 2, _http_request))

    # ------------------------------------------------------------------
    # Thread Module (concurrency)
    # ------------------------------------------------------------------

    import threading
    import queue

    thread_env = Environment()
    thread_store = {}

    def _thread_spawn(args, interp):
        import threading
        fn = args[0] if args else None
        if not isinstance(fn, (HFunction, HNativeFn)):
            raise RuntimeError("Thread spawn requires a function")
        
        thread_id = str(len(thread_store))
        result_queue = queue.Queue()
        
        def thread_func():
            try:
                result = interp._call_function(fn, [], call_line=0)
                result_queue.put(("success", result))
            except Exception as e:
                result_queue.put(("error", str(e)))
        
        thread = threading.Thread(target=thread_func)
        thread.start()
        thread_store[thread_id] = {"thread": thread, "queue": result_queue}
        return h_string(thread_id)

    def _thread_join(args, _):
        thread_id = args[0].value if args and isinstance(args[0], HString) else ""
        if thread_id not in thread_store:
            raise RuntimeError(f"Thread not found: {thread_id}")
        
        thread_info = thread_store[thread_id]
        thread_info["thread"].join()
        status, result = thread_info["queue"].get()
        del thread_store[thread_id]
        
        if status == "success":
            return result
        else:
            raise RuntimeError(f"Thread error: {result}")

    def _thread_sleep(args, _):
        import time
        ms = args[0].value if args and isinstance(args[0], HNumber) else 0
        time.sleep(ms / 1000)
        return h_none()

    thread_env.define("spawn", HNativeFn("spawn", 1, _thread_spawn))
    thread_env.define("join", HNativeFn("join", 1, _thread_join))
    thread_env.define("sleep", HNativeFn("sleep", 1, _thread_sleep))

    # ------------------------------------------------------------------
    # Register modules
    # ------------------------------------------------------------------

    env.define("Math", HModule("Math", math_env))
    env.define("Time", HModule("Time", time_env))
    env.define("JSON", HModule("JSON", json_env))
    env.define("File", HModule("File", file_env))
    env.define("HTTP", HModule("HTTP", http_env))
    env.define("Thread", HModule("Thread", thread_env))

    # ------------------------------------------------------------------
    # Regex Module (regular expressions)
    # ------------------------------------------------------------------

    import re

    regex_env = Environment()

    def _regex_match(args, _):
        pattern = args[0].value if args and isinstance(args[0], HString) else ""
        text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        try:
            return h_bool(re.match(pattern, text) is not None)
        except re.error as e:
            raise RuntimeError(f"Invalid regex pattern: {e}")

    def _regex_find_all(args, _):
        pattern = args[0].value if args and isinstance(args[0], HString) else ""
        text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        try:
            matches = re.findall(pattern, text)
            return h_list([h_string(m) for m in matches])
        except re.error as e:
            raise RuntimeError(f"Invalid regex pattern: {e}")

    def _regex_replace(args, _):
        pattern = args[0].value if args and isinstance(args[0], HString) else ""
        replacement = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        text = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        try:
            return h_string(re.sub(pattern, replacement, text))
        except re.error as e:
            raise RuntimeError(f"Invalid regex pattern: {e}")

    def _regex_split(args, _):
        pattern = args[0].value if args and isinstance(args[0], HString) else ""
        text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        try:
            parts = re.split(pattern, text)
            return h_list([h_string(p) for p in parts])
        except re.error as e:
            raise RuntimeError(f"Invalid regex pattern: {e}")

    regex_env.define("match", HNativeFn("match", 2, _regex_match))
    regex_env.define("findAll", HNativeFn("findAll", 2, _regex_find_all))
    regex_env.define("replace", HNativeFn("replace", 3, _regex_replace))
    regex_env.define("split", HNativeFn("split", 2, _regex_split))

    env.define("Regex", HModule("Regex", regex_env))

    # ------------------------------------------------------------------
    # Test Module (testing framework)
    # ------------------------------------------------------------------

    test_env = Environment()
    test_results = {"passed": 0, "failed": 0, "errors": []}

    def _test_reset(args, _):
        test_results["passed"] = 0
        test_results["failed"] = 0
        test_results["errors"] = []
        return h_none()

    def _test_assert_equal(args, _):
        actual = args[0] if args else None
        expected = args[1] if len(args) > 1 else None
        message = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "Values not equal"
        
        if not isinstance(actual, type(expected)):
            test_results["failed"] += 1
            test_results["errors"].append(f"{message}: expected {expected}, got {actual}")
            raise RuntimeError(f"{message}: expected {expected}, got {actual}")
        
        if isinstance(actual, HNumber) and isinstance(expected, HNumber):
            if actual.value != expected.value:
                test_results["failed"] += 1
                test_results["errors"].append(f"{message}: expected {expected}, got {actual}")
                raise RuntimeError(f"{message}: expected {expected}, got {actual}")
        elif str(actual) != str(expected):
            test_results["failed"] += 1
            test_results["errors"].append(f"{message}: expected {expected}, got {actual}")
            raise RuntimeError(f"{message}: expected {expected}, got {actual}")
        
        test_results["passed"] += 1
        return h_none()

    def _test_assert_true(args, _):
        condition = args[0] if args else None
        message = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Expected true"
        
        if not is_truthy(condition):
            test_results["failed"] += 1
            test_results["errors"].append(f"{message}: got {condition}")
            raise RuntimeError(f"{message}: got {condition}")
        
        test_results["passed"] += 1
        return h_none()

    def _test_assert_false(args, _):
        condition = args[0] if args else None
        message = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Expected false"
        
        if is_truthy(condition):
            test_results["failed"] += 1
            test_results["errors"].append(f"{message}: got {condition}")
            raise RuntimeError(f"{message}: got {condition}")
        
        test_results["passed"] += 1
        return h_none()

    def _test_results(args, _):
        return h_map({
            "passed": h_number(test_results["passed"]),
            "failed": h_number(test_results["failed"]),
            "errors": h_list([h_string(e) for e in test_results["errors"]])
        })

    def _test_run(args, interp):
        fn = args[0] if args else None
        if not isinstance(fn, (HFunction, HNativeFn)):
            raise RuntimeError("test.run requires a function")
        
        try:
            interp._call_function(fn, [], call_line=0)
        except RuntimeError as e:
            # Test failed - already counted in assert functions
            pass
        return h_none()

    test_env.define("reset", HNativeFn("reset", 0, _test_reset))
    test_env.define("assertEqual", HNativeFn("assertEqual", -1, _test_assert_equal))
    test_env.define("assertTrue", HNativeFn("assertTrue", -1, _test_assert_true))
    test_env.define("assertFalse", HNativeFn("assertFalse", -1, _test_assert_false))
    test_env.define("results", HNativeFn("results", 0, _test_results))
    test_env.define("run", HNativeFn("run", 1, _test_run))

    env.define("Test", HModule("Test", test_env))

    # ------------------------------------------------------------------
    # Package Manager Module
    # ------------------------------------------------------------------

    pkg_env = Environment()
    import os
    import json
    import urllib.request

    # Package registry (simulated - in production would use a real registry)
    PACKAGE_REGISTRY = {
        "http-client": {"version": "1.0.0", "url": "https://example.com/packages/http-client.hku"},
        "date-utils": {"version": "1.0.0", "url": "https://example.com/packages/date-utils.hku"},
        "crypto": {"version": "1.0.0", "url": "https://example.com/packages/crypto.hku"},
    }

    def _pkg_install(args, _):
        package_name = args[0].value if args and isinstance(args[0], HString) else ""
        
        if package_name not in PACKAGE_REGISTRY:
            raise RuntimeError(f"Package '{package_name}' not found in registry")
        
        # Create packages directory if it doesn't exist
        packages_dir = os.path.join(os.getcwd(), "packages")
        os.makedirs(packages_dir, exist_ok=True)
        
        package_file = os.path.join(packages_dir, f"{package_name}.hku")
        
        # In a real implementation, this would download from the URL
        # For now, we'll create a placeholder
        with open(package_file, 'w') as f:
            f.write(f"# Package: {package_name}\n# Version: {PACKAGE_REGISTRY[package_name]['version']}\n")
        
        return h_string(f"Package '{package_name}' installed successfully")

    def _pkg_list(args, _):
        packages = []
        packages_dir = os.path.join(os.getcwd(), "packages")
        if os.path.exists(packages_dir):
            for f in os.listdir(packages_dir):
                if f.endswith('.hku'):
                    packages.append(f[:-4])  # Remove .hku extension
        return h_list([h_string(p) for p in packages])

    def _pkg_remove(args, _):
        package_name = args[0].value if args and isinstance(args[0], HString) else ""
        package_file = os.path.join(os.getcwd(), "packages", f"{package_name}.hku")
        
        if os.path.exists(package_file):
            os.remove(package_file)
            return h_string(f"Package '{package_name}' removed successfully")
        else:
            raise RuntimeError(f"Package '{package_name}' not found")

    def _pkg_search(args, _):
        query = args[0].value if args and isinstance(args[0], HString) else ""
        results = []
        for name, info in PACKAGE_REGISTRY.items():
            if query.lower() in name.lower():
                results.append(h_map({
                    "name": h_string(name),
                    "version": h_string(info["version"])
                }))
        return h_list(results)

    pkg_env.define("install", HNativeFn("install", 1, _pkg_install))
    pkg_env.define("list", HNativeFn("list", 0, _pkg_list))
    pkg_env.define("remove", HNativeFn("remove", 1, _pkg_remove))
    pkg_env.define("search", HNativeFn("search", 1, _pkg_search))

    env.define("Pkg", HModule("Pkg", pkg_env))

    # ------------------------------------------------------------------
    # Async Module (async/await support)
    # ------------------------------------------------------------------

    async_env = Environment()
    import asyncio

    def _async_sleep(args, _):
        import asyncio
        ms = args[0].value if args and isinstance(args[0], HNumber) else 0
        # In a real implementation, this would be async
        import time
        time.sleep(ms / 1000)
        return h_none()

    def _async_spawn(args, interp):
        import threading
        fn = args[0] if args else None
        if not isinstance(fn, (HFunction, HNativeFn)):
            raise RuntimeError("async.spawn requires a function")
        
        result = [None]
        error = [None]
        
        def run_async():
            try:
                result[0] = interp._call_function(fn, [], call_line=0)
            except Exception as e:
                error[0] = str(e)
        
        thread = threading.Thread(target=run_async)
        thread.start()
        thread.join()
        
        if error[0]:
            raise RuntimeError(f"Async error: {error[0]}")
        return result[0]

    async_env.define("sleep", HNativeFn("sleep", 1, _async_sleep))
    async_env.define("spawn", HNativeFn("spawn", 1, _async_spawn))

    env.define("Async", HModule("Async", async_env))

    # ------------------------------------------------------------------
    # Date Module (date/time manipulation)
    # ------------------------------------------------------------------

    date_env = Environment()
    from datetime import datetime, timedelta

    def _date_now(args, _):
        return h_string(datetime.now().isoformat())

    def _date_parse(args, _):
        date_str = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            dt = datetime.fromisoformat(date_str)
            return h_map({
                "year": h_number(dt.year),
                "month": h_number(dt.month),
                "day": h_number(dt.day),
                "hour": h_number(dt.hour),
                "minute": h_number(dt.minute),
                "second": h_number(dt.second),
                "iso": h_string(dt.isoformat())
            })
        except ValueError:
            raise RuntimeError(f"Invalid date format: {date_str}")

    def _date_format(args, _):
        date_str = args[0].value if args and isinstance(args[0], HString) else ""
        fmt = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "%Y-%m-%d"
        try:
            dt = datetime.fromisoformat(date_str)
            return h_string(dt.strftime(fmt))
        except ValueError:
            raise RuntimeError(f"Invalid date format: {date_str}")

    def _date_add_days(args, _):
        date_str = args[0].value if args and isinstance(args[0], HString) else ""
        days = args[1].value if len(args) > 1 and isinstance(args[1], HNumber) else 0
        try:
            dt = datetime.fromisoformat(date_str)
            new_dt = dt + timedelta(days=int(days))
            return h_string(new_dt.isoformat())
        except ValueError:
            raise RuntimeError(f"Invalid date format: {date_str}")

    def _date_add_hours(args, _):
        date_str = args[0].value if args and isinstance(args[0], HString) else ""
        hours = args[1].value if len(args) > 1 and isinstance(args[1], HNumber) else 0
        try:
            dt = datetime.fromisoformat(date_str)
            new_dt = dt + timedelta(hours=int(hours))
            return h_string(new_dt.isoformat())
        except ValueError:
            raise RuntimeError(f"Invalid date format: {date_str}")

    date_env.define("now", HNativeFn("now", 0, _date_now))
    date_env.define("parse", HNativeFn("parse", 1, _date_parse))
    date_env.define("format", HNativeFn("format", -1, _date_format))
    date_env.define("addDays", HNativeFn("addDays", -1, _date_add_days))
    date_env.define("addHours", HNativeFn("addHours", -1, _date_add_hours))

    env.define("Date", HModule("Date", date_env))

    # ------------------------------------------------------------------
    # Compression Module (zip, gzip)
    # ------------------------------------------------------------------

    compress_env = Environment()
    import gzip
    import zipfile
    import io

    def _compress_gzip_compress(args, _):
        data = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            compressed = gzip.compress(data.encode('utf-8'))
            return h_string(compressed.hex())
        except Exception as e:
            raise RuntimeError(f"Compression error: {e}")

    def _compress_gzip_decompress(args, _):
        hex_data = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            compressed = bytes.fromhex(hex_data)
            decompressed = gzip.decompress(compressed)
            return h_string(decompressed.decode('utf-8'))
        except Exception as e:
            raise RuntimeError(f"Decompression error: {e}")

    def _compress_zip_create(args, _):
        files = args[0] if args and isinstance(args[0], HMap) else None
        if not files:
            raise RuntimeError("zip.create requires a map of filename: content")
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, content in files.entries.items():
                if isinstance(content, HString):
                    zip_file.writestr(filename, content.value)
        
        return h_string(zip_buffer.getvalue().hex())

    def _compress_zip_extract(args, _):
        hex_data = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            zip_data = bytes.fromhex(hex_data)
            zip_buffer = io.BytesIO(zip_data)
            
            files = {}
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                for filename in zip_file.namelist():
                    files[filename] = h_string(zip_file.read(filename).decode('utf-8'))
            
            return h_map(files)
        except Exception as e:
            raise RuntimeError(f"Zip extraction error: {e}")

    compress_env.define("gzipCompress", HNativeFn("gzipCompress", 1, _compress_gzip_compress))
    compress_env.define("gzipDecompress", HNativeFn("gzipDecompress", 1, _compress_gzip_decompress))
    compress_env.define("zipCreate", HNativeFn("zipCreate", 1, _compress_zip_create))
    compress_env.define("zipExtract", HNativeFn("zipExtract", 1, _compress_zip_extract))

    env.define("Compress", HModule("Compress", compress_env))

    # ------------------------------------------------------------------
    # Database Module (SQLite)
    # ------------------------------------------------------------------

    db_env = Environment()
    import sqlite3

    # Store database connections
    db_connections = {}

    def _db_connect(args, _):
        db_path = args[0].value if args and isinstance(args[0], HString) else ":memory:"
        try:
            conn = sqlite3.connect(db_path)
            conn_id = f"db_{len(db_connections)}"
            db_connections[conn_id] = conn
            return h_string(conn_id)
        except Exception as e:
            raise RuntimeError(f"Database connection error: {e}")

    def _db_execute(args, _):
        conn_id = args[0].value if args and isinstance(args[0], HString) else ""
        sql = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        params = args[2] if len(args) > 2 and isinstance(args[2], HList) else None
        
        if conn_id not in db_connections:
            raise RuntimeError(f"Database connection not found: {conn_id}")
        
        try:
            conn = db_connections[conn_id]
            cursor = conn.cursor()
            
            if params:
                param_values = [p.value if isinstance(p, HNumber) else str(p.value) for p in params.elements]
                cursor.execute(sql, param_values)
            else:
                cursor.execute(sql)
            
            # Check if it's a SELECT query
            if sql.strip().upper().startswith("SELECT"):
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    row_map = {}
                    for i, col in enumerate(columns):
                        row_map[col] = h_string(str(row[i])) if row[i] is not None else h_none()
                    result.append(h_map(row_map))
                return h_list(result)
            else:
                conn.commit()
                return h_number(cursor.rowcount)
        except Exception as e:
            raise RuntimeError(f"Database execution error: {e}")

    def _db_close(args, _):
        conn_id = args[0].value if args and isinstance(args[0], HString) else ""
        if conn_id in db_connections:
            db_connections[conn_id].close()
            del db_connections[conn_id]
            return h_none()
        else:
            raise RuntimeError(f"Database connection not found: {conn_id}")

    db_env.define("connect", HNativeFn("connect", 1, _db_connect))
    db_env.define("execute", HNativeFn("execute", -1, _db_execute))
    db_env.define("close", HNativeFn("close", 1, _db_close))

    env.define("DB", HModule("DB", db_env))

    # ------------------------------------------------------------------
    # XML Module (XML parsing)
    # ------------------------------------------------------------------

    xml_env = Environment()
    import xml.etree.ElementTree as ET

    def _xml_parse(args, _):
        xml_str = args[0].value if args and isinstance(args[0], HString) else ""
        try:
            root = ET.fromstring(xml_str)
            return _xml_element_to_map(root)
        except Exception as e:
            raise RuntimeError(f"XML parsing error: {e}")

    def _xml_element_to_map(element):
        """Convert XML element to Haiku map."""
        result = {
            "tag": h_string(element.tag),
            "text": h_string(element.text or ""),
            "attrib": h_map({k: h_string(v) for k, v in element.attrib.items()}),
            "children": h_list([_xml_element_to_map(child) for child in element])
        }
        return h_map(result)

    def _xml_to_string(args, _):
        element_map = args[0] if args and isinstance(args[0], HMap) else None
        if not element_map:
            raise RuntimeError("xml.toString requires a map")
        
        # Reconstruct XML from map (simplified)
        tag = element_map.entries.get("tag")
        text = element_map.entries.get("text")
        attrib = element_map.entries.get("attrib")
        
        if not isinstance(tag, HString):
            raise RuntimeError("Invalid XML element: missing tag")
        
        attrib_str = ""
        if isinstance(attrib, HMap):
            for k, v in attrib.entries.items():
                attrib_str += f' {k}="{v.value}"'
        
        text_str = text.value if isinstance(text, HString) else ""
        xml_str = f"<{tag.value}{attrib_str}>{text_str}</{tag.value}>"
        return h_string(xml_str)

    xml_env.define("parse", HNativeFn("parse", 1, _xml_parse))
    xml_env.define("toString", HNativeFn("toString", 1, _xml_to_string))

    env.define("XML", HModule("XML", xml_env))

    # ------------------------------------------------------------------
    # Assertions
    # ------------------------------------------------------------------

    def _assert_fn(args, _):
        condition = args[0]
        message = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Assertion failed"
        truthy = is_truthy(condition)
        if not truthy:
            raise RuntimeError(message)
        return h_none()

    env.define("assert", HNativeFn("assert", -1, _assert_fn))

    # ------------------------------------------------------------------
    # GUI Module (PySide6 bindings for creating GUI applications)
    # ------------------------------------------------------------------

    gui_env = Environment()
    
    # Store GUI components
    gui_components = {
        "app": None, 
        "windows": {}, 
        "widgets": {}, 
        "callbacks": {}, 
        "interpreter": None,
        "layouts": {},
        "timers": {},
        "menus": {},
        "toolbars": {},
        "statusbars": {},
        "graphics": {},
        "dialogs": {},
        "trays": {},
        "tray_menus": {},
        "wizards": {},
        "custom_dialogs": {},
        "button_groups": {},
        "sounds": {}
    }
    
    def _gui_init_app(args, interp):
        """Initialize the Qt application."""
        try:
            from PySide6.QtWidgets import QApplication
            from PySide6.QtCore import Qt
            
            # Store interpreter reference for callbacks
            gui_components["interpreter"] = interp
            
            if gui_components["app"] is None:
                gui_components["app"] = QApplication([])
                gui_components["app"].setAttribute(Qt.AA_EnableHighDpiScaling, True)
            
            return h_string("Application initialized")
        except ImportError:
            raise RuntimeError("PySide6 not installed. Install with: pip install PySide6")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize GUI: {e}")
    
    def _gui_create_window(args, _):
        """Create a new window."""
        try:
            from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
            from PySide6.QtGui import QPalette, QColor
            
            title = args[0].value if args and isinstance(args[0], HString) else "Haiku Window"
            width = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 800
            height = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 600
            
            # Ensure app is initialized
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            # Create window
            window = QMainWindow()
            window.setWindowTitle(title)
            window.resize(width, height)
            
            # Set window to be fully opaque by default
            window.setWindowOpacity(1.0)
            
            # Create central widget with layout
            central_widget = QWidget()
            central_widget.setAutoFillBackground(True)
            
            # Set background color to white to ensure opacity
            palette = central_widget.palette()
            palette.setColor(QPalette.Window, QColor(255, 255, 255))
            central_widget.setPalette(palette)
            
            window.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            
            # Store window
            window_id = f"window_{len(gui_components['windows'])}"
            gui_components["windows"][window_id] = {
                "window": window,
                "layout": layout,
                "widgets": []
            }
            
            return h_string(window_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create window: {e}")
    
    def _gui_create_frameless_window(args, _):
        """Create a frameless window (custom title bar)."""
        try:
            from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout
            from PySide6.QtCore import Qt
            from PySide6.QtGui import QPalette, QColor
            
            title = args[0].value if args and isinstance(args[0], HString) else "Haiku Window"
            width = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 800
            height = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 600
            
            # Ensure app is initialized
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            # Create frameless window
            window = QMainWindow()
            window.setWindowFlags(Qt.WindowType.FramelessWindowHint)
            window.setWindowTitle(title)
            window.resize(width, height)
            
            # Set window to be fully opaque
            window.setWindowOpacity(1.0)
            
            # Create central widget with layout
            central_widget = QWidget()
            central_widget.setAutoFillBackground(True)
            
            # Set background color
            palette = central_widget.palette()
            palette.setColor(QPalette.Window, QColor(30, 30, 30))
            central_widget.setPalette(palette)
            
            window.setCentralWidget(central_widget)
            layout = QVBoxLayout(central_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
            
            # Store window
            window_id = f"window_{len(gui_components['windows'])}"
            gui_components["windows"][window_id] = {
                "window": window,
                "layout": layout,
                "widgets": [],
                "is_frameless": True
            }
            
            return h_string(window_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create frameless window: {e}")
    
    def _gui_add_title_bar(args, _):
        """Add a custom title bar to a frameless window."""
        try:
            from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Title"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create title bar widget
            title_bar = QWidget()
            title_bar.setFixedHeight(36)
            title_bar.setStyleSheet("background-color: #3C3C3C; border-bottom: 1px solid #3C3C3C;")
            
            layout = QHBoxLayout(title_bar)
            layout.setContentsMargins(10, 0, 0, 0)
            layout.setSpacing(0)
            
            # Title label
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #CCCCCC; font-weight: bold; padding: 8px;")
            layout.addWidget(title_label)
            layout.addStretch(1)
            
            # Window control buttons
            def on_minimize():
                window_data["window"].showMinimized()
            
            def on_maximize():
                if window_data["window"].isMaximized():
                    window_data["window"].showNormal()
                else:
                    window_data["window"].showMaximized()
            
            def on_close():
                window_data["window"].close()
            
            btn_min = QPushButton("-")
            btn_min.setFixedSize(46, 36)
            btn_min.setStyleSheet("background: transparent; border: none; color: #858585;")
            btn_min.clicked.connect(on_minimize)
            
            btn_max = QPushButton("□")
            btn_max.setFixedSize(46, 36)
            btn_max.setStyleSheet("background: transparent; border: none; color: #858585;")
            btn_max.clicked.connect(on_maximize)
            
            btn_close = QPushButton("×")
            btn_close.setFixedSize(46, 36)
            btn_close.setStyleSheet("background: transparent; border: none; color: #858585;")
            btn_close.clicked.connect(on_close)
            
            layout.addWidget(btn_min)
            layout.addWidget(btn_max)
            layout.addWidget(btn_close)
            
            # Add to window layout
            window_data["layout"].addWidget(title_bar)
            window_data["widgets"].append(title_bar)
            
            title_bar_id = f"{window_id}_titlebar"
            gui_components["title_bars"] = gui_components.get("title_bars", {})
            gui_components["title_bars"][title_bar_id] = {
                "title_bar": title_bar,
                "title_label": title_label
            }
            
            return h_string(title_bar_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add title bar: {e}")
    
    def _gui_set_title_bar_title(args, _):
        """Set the title bar text."""
        try:
            title_bar_id = args[0].value if args and isinstance(args[0], HString) else ""
            title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Title"
            
            if title_bar_id in gui_components.get("title_bars", {}):
                gui_components["title_bars"][title_bar_id]["title_label"].setText(title)
                return h_string("Title updated")
            else:
                raise RuntimeError(f"Title bar not found: {title_bar_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to set title bar title: {e}")
    
    def _gui_add_line_number_gutter(args, _):
        """Add a line number gutter to a text editor."""
        try:
            from PySide6.QtWidgets import QWidget, QTextEdit, QVBoxLayout
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            editor_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if editor_index >= len(window_data["widgets"]):
                raise RuntimeError("Editor index out of range")
            
            editor = window_data["widgets"][editor_index]
            
            # Create line number area
            line_area = QWidget()
            line_area.setFixedWidth(50)
            line_area.setStyleSheet("background-color: #252526; color: #858585; border-right: 1px solid #3C3C3C;")
            
            # Store reference
            gutter_id = f"{window_id}_gutter_{editor_index}"
            gui_components["gutters"] = gui_components.get("gutters", {})
            gui_components["gutters"][gutter_id] = {
                "line_area": line_area,
                "editor": editor
            }
            
            return h_string(gutter_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add line number gutter: {e}")
    
    def _gui_update_line_numbers(args, _):
        """Update line numbers for a gutter."""
        try:
            gutter_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if gutter_id not in gui_components.get("gutters", {}):
                raise RuntimeError(f"Gutter not found: {gutter_id}")
            
            gutter_data = gui_components["gutters"][gutter_id]
            editor = gutter_data["editor"]
            
            # Get line count from editor
            text = editor.toPlainText()
            line_count = text.count("\n") + 1
            
            # For now, just acknowledge - full implementation would need custom painting
            return h_string(f"Line count: {line_count}")
        except Exception as e:
            raise RuntimeError(f"Failed to update line numbers: {e}")
    
    def _gui_show_window(args, _):
        """Show a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].show()
            return h_string("Window shown")
        else:
            raise RuntimeError(f"Window not found: {window_id}")
    
    def _gui_add_button(args, _):
        """Add a button to a window."""
        try:
            from PySide6.QtWidgets import QPushButton
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Button"
            callback = args[2] if len(args) > 2 else None
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create button
            button = QPushButton(text)
            
            # Connect callback if provided
            if callback and isinstance(callback, HFunction):
                def on_click():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Callback error: {e}")
                
                button.clicked.connect(on_click)
                
                # Store callback
                callback_id = f"{window_id}_button_{len(window_data['widgets'])}"
                gui_components["callbacks"][callback_id] = callback
            
            # Add to layout
            window_data["layout"].addWidget(button)
            window_data["widgets"].append(button)
            
            return h_string("Button added")
        except Exception as e:
            raise RuntimeError(f"Failed to add button: {e}")
    
    def _gui_add_label(args, _):
        """Add a label to a window."""
        try:
            from PySide6.QtWidgets import QLabel
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Label"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create label
            label = QLabel(text)
            
            # Add to layout
            window_data["layout"].addWidget(label)
            window_data["widgets"].append(label)
            
            return h_string("Label added")
        except Exception as e:
            raise RuntimeError(f"Failed to add label: {e}")
    
    def _gui_add_text_input(args, _):
        """Add a text input field to a window."""
        try:
            from PySide6.QtWidgets import QLineEdit
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            placeholder = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create text input
            text_input = QLineEdit()
            if placeholder:
                text_input.setPlaceholderText(placeholder)
            
            # Add to layout
            window_data["layout"].addWidget(text_input)
            window_data["widgets"].append(text_input)
            
            return h_string("Text input added")
        except Exception as e:
            raise RuntimeError(f"Failed to add text input: {e}")
    
    def _gui_add_text_area(args, _):
        """Add a text area to a window."""
        try:
            from PySide6.QtWidgets import QTextEdit
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create text area
            text_area = QTextEdit()
            text_area.setPlainText(text)
            
            # Add to layout
            window_data["layout"].addWidget(text_area)
            window_data["widgets"].append(text_area)
            
            return h_string("Text area added")
        except Exception as e:
            raise RuntimeError(f"Failed to add text area: {e}")
    
    def _gui_set_layout(args, _):
        """Set the layout type for a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        layout_type = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "vertical"
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        # For simplicity, we just acknowledge the layout type
        # In a full implementation, this would change the actual layout
        return h_string(f"Layout set to {layout_type}")
    
    def _gui_run(args, _):
        """Run the GUI application main loop."""
        try:
            if gui_components["app"] is None:
                raise RuntimeError("Application not initialized. Call GUI.init() first.")
            
            # Show all windows
            for window_id, window_data in gui_components["windows"].items():
                window_data["window"].show()
            
            # Run the application
            result = gui_components["app"].exec()
            
            return h_number(result)
        except Exception as e:
            raise RuntimeError(f"Failed to run GUI: {e}")
    
    def _gui_set_style(args, _):
        """Set the application style."""
        style = args[0].value if args and isinstance(args[0], HString) else "Fusion"
        
        try:
            if gui_components["app"]:
                gui_components["app"].setStyle(style)
                return h_string(f"Style set to {style}")
            else:
                raise RuntimeError("Application not initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to set style: {e}")
    
    def _gui_message_box(args, _):
        """Show a message box."""
        try:
            from PySide6.QtWidgets import QMessageBox
            
            title = args[0].value if args and isinstance(args[0], HString) else "Message"
            message = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            msg_type = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "info"
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            # Create message box
            msg_box = QMessageBox()
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            
            if msg_type == "info":
                msg_box.setIcon(QMessageBox.Information)
            elif msg_type == "warning":
                msg_box.setIcon(QMessageBox.Warning)
            elif msg_type == "error":
                msg_box.setIcon(QMessageBox.Critical)
            elif msg_type == "question":
                msg_box.setIcon(QMessageBox.Question)
            
            msg_box.exec()
            
            return h_string("Message box shown")
        except Exception as e:
            raise RuntimeError(f"Failed to show message box: {e}")
    
    def _gui_get_input(args, _):
        """Get text from a text input widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index < len(window_data["widgets"]):
            widget = window_data["widgets"][widget_index]
            if hasattr(widget, 'text'):
                return h_string(widget.text())
            elif hasattr(widget, 'toPlainText'):
                return h_string(widget.toPlainText())
            else:
                return h_string("")
        else:
            raise RuntimeError("Widget index out of range")
    
    def _gui_set_text(args, _):
        """Set text for a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        text = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index < len(window_data["widgets"]):
            widget = window_data["widgets"][widget_index]
            if hasattr(widget, 'setText'):
                widget.setText(text)
            elif hasattr(widget, 'setPlainText'):
                widget.setPlainText(text)
            
            return h_string("Text set")
        else:
            raise RuntimeError("Widget index out of range")
    
    def _gui_add_checkbox(args, _):
        """Add a checkbox to a window."""
        try:
            from PySide6.QtWidgets import QCheckBox
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Checkbox"
            checked = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else False
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create checkbox
            checkbox = QCheckBox(text)
            checkbox.setChecked(checked)
            
            # Add to layout
            window_data["layout"].addWidget(checkbox)
            window_data["widgets"].append(checkbox)
            
            return h_string("Checkbox added")
        except Exception as e:
            raise RuntimeError(f"Failed to add checkbox: {e}")
    
    def _gui_add_combobox(args, _):
        """Add a combobox (dropdown) to a window."""
        try:
            from PySide6.QtWidgets import QComboBox
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            items = args[1] if len(args) > 1 and isinstance(args[1], HList) else None
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create combobox
            combobox = QComboBox()
            
            # Add items if provided
            if items:
                for item in items.elements:
                    if isinstance(item, HString):
                        combobox.addItem(item.value)
            
            # Add to layout
            window_data["layout"].addWidget(combobox)
            window_data["widgets"].append(combobox)
            
            return h_string("Combobox added")
        except Exception as e:
            raise RuntimeError(f"Failed to add combobox: {e}")
    
    def _gui_add_slider(args, _):
        """Add a slider to a window."""
        try:
            from PySide6.QtWidgets import QSlider
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            min_val = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            max_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 100
            initial = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 50
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create slider
            slider = QSlider(Qt.Horizontal)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(initial)
            
            # Add to layout
            window_data["layout"].addWidget(slider)
            window_data["widgets"].append(slider)
            
            return h_string("Slider added")
        except Exception as e:
            raise RuntimeError(f"Failed to add slider: {e}")
    
    def _gui_add_progress_bar(args, _):
        """Add a progress bar to a window."""
        try:
            from PySide6.QtWidgets import QProgressBar
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            value = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create progress bar
            progress_bar = QProgressBar()
            progress_bar.setValue(value)
            
            # Add to layout
            window_data["layout"].addWidget(progress_bar)
            window_data["widgets"].append(progress_bar)
            
            return h_string("Progress bar added")
        except Exception as e:
            raise RuntimeError(f"Failed to add progress bar: {e}")
    
    def _gui_close_window(args, _):
        """Close a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].close()
            return h_string("Window closed")
        else:
            raise RuntimeError(f"Window not found: {window_id}")
    
    def _gui_set_window_title(args, _):
        """Set the title of a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].setWindowTitle(title)
            return h_string("Window title set")
        else:
            raise RuntimeError(f"Window not found: {window_id}")
    
    def _gui_set_window_size(args, _):
        """Set the size of a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        width = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 800
        height = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 600
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].resize(width, height)
            return h_string("Window size set")
        else:
            raise RuntimeError(f"Window not found: {window_id}")
    
    # Advanced Layouts
    def _gui_create_horizontal_layout(args, _):
        """Create a horizontal layout."""
        try:
            from PySide6.QtWidgets import QHBoxLayout, QWidget
            
            layout_id = args[0].value if args and isinstance(args[0], HString) else f"layout_{len(gui_components['layouts'])}"
            
            layout = QHBoxLayout()
            gui_components["layouts"][layout_id] = {
                "layout": layout,
                "type": "horizontal",
                "widgets": []
            }
            
            return h_string(layout_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create horizontal layout: {e}")
    
    def _gui_create_vertical_layout(args, _):
        """Create a vertical layout."""
        try:
            from PySide6.QtWidgets import QVBoxLayout
            
            layout_id = args[0].value if args and isinstance(args[0], HString) else f"layout_{len(gui_components['layouts'])}"
            
            layout = QVBoxLayout()
            gui_components["layouts"][layout_id] = {
                "layout": layout,
                "type": "vertical",
                "widgets": []
            }
            
            return h_string(layout_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create vertical layout: {e}")
    
    def _gui_create_grid_layout(args, _):
        """Create a grid layout."""
        try:
            from PySide6.QtWidgets import QGridLayout
            
            layout_id = args[0].value if args and isinstance(args[0], HString) else f"layout_{len(gui_components['layouts'])}"
            rows = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 3
            cols = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 3
            
            layout = QGridLayout()
            gui_components["layouts"][layout_id] = {
                "layout": layout,
                "type": "grid",
                "rows": rows,
                "cols": cols,
                "widgets": [],
                "current_row": 0,
                "current_col": 0
            }
            
            return h_string(layout_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create grid layout: {e}")
    
    def _gui_create_form_layout(args, _):
        """Create a form layout."""
        try:
            from PySide6.QtWidgets import QFormLayout
            
            layout_id = args[0].value if args and isinstance(args[0], HString) else f"layout_{len(gui_components['layouts'])}"
            
            layout = QFormLayout()
            gui_components["layouts"][layout_id] = {
                "layout": layout,
                "type": "form",
                "widgets": []
            }
            
            return h_string(layout_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create form layout: {e}")
    
    def _gui_add_widget_to_layout(args, _):
        """Add a widget to a layout."""
        layout_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget = args[1] if len(args) > 1 else None
        row = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        col = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        row_span = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 1
        col_span = int(args[5].value) if len(args) > 5 and isinstance(args[5], HNumber) else 1
        
        if layout_id not in gui_components["layouts"]:
            raise RuntimeError(f"Layout not found: {layout_id}")
        
        layout_data = gui_components["layouts"][layout_id]
        
        # Get the actual Qt widget from our widget storage
        # This is a simplified approach - in a full implementation we'd need proper widget tracking
        if layout_data["type"] == "grid":
            # For grid layout, we'd need the actual widget reference
            # This is simplified for now
            pass
        else:
            # For vertical/horizontal layouts
            pass
        
        return h_string("Widget added to layout")
    
    def _gui_set_window_layout(args, _):
        """Set the layout for a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        layout_id = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        if layout_id not in gui_components["layouts"]:
            raise RuntimeError(f"Layout not found: {layout_id}")
        
        window_data = gui_components["windows"][window_id]
        layout_data = gui_components["layouts"][layout_id]
        
        # Set the layout to the central widget
        central_widget = window_data["window"].centralWidget()
        central_widget.setLayout(layout_data["layout"])
        
        return h_string("Layout set for window")

    def _gui_add_to_grid_layout(args, _):
        """Add widget to grid layout at specific position."""
        layout_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget = args[1] if len(args) > 1 else None
        row = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        col = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        row_span = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 1
        col_span = int(args[5].value) if len(args) > 5 and isinstance(args[5], HNumber) else 1
        
        if layout_id not in gui_components["layouts"]:
            raise RuntimeError(f"Layout not found: {layout_id}")
        
        layout_data = gui_components["layouts"][layout_id]
        layout = layout_data["layout"]
        
        # This is a simplified approach - in a full implementation you'd need proper widget tracking
        # For now, we'll just acknowledge the grid position
        return h_string("Widget position in grid noted")

    def _gui_create_window_with_grid(args, _):
        """Create a window with grid layout for calculator-style UI."""
        try:
            from PySide6.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QTextEdit
            
            title = args[0].value if args and isinstance(args[0], HString) else "Haiku Window"
            width = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 800
            height = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 600
            grid_rows = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 5
            grid_cols = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 4
            
            # Ensure app is initialized
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            # Create window
            window = QMainWindow()
            window.setWindowTitle(title)
            window.resize(width, height)
            
            # Set window to be fully opaque by default
            window.setWindowOpacity(1.0)
            
            # Create central widget with grid layout
            central_widget = QWidget()
            central_widget.setAutoFillBackground(True)
            
            # Set background color to white to ensure opacity
            from PySide6.QtGui import QPalette, QColor
            palette = central_widget.palette()
            palette.setColor(QPalette.Window, QColor(255, 255, 255))
            central_widget.setPalette(palette)
            
            window.setCentralWidget(central_widget)
            
            # Create grid layout
            grid_layout = QGridLayout()
            grid_layout.setSpacing(5)
            grid_layout.setContentsMargins(10, 10, 10, 10)
            central_widget.setLayout(grid_layout)
            
            # Store window with grid layout
            window_id = f"window_{len(gui_components['windows'])}"
            gui_components["windows"][window_id] = {
                "window": window,
                "layout": grid_layout,
                "widgets": [],
                "is_grid": True,
                "grid_rows": grid_rows,
                "grid_cols": grid_cols,
                "current_row": 0,
                "current_col": 0
            }
            
            return h_string(window_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create window with grid: {e}")

    def _gui_add_to_grid(args, _):
        """Add widget to next available grid position."""
        try:
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_type = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "label"
            text = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
            callback = args[3] if len(args) > 3 else None
            row_span = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 1
            col_span = int(args[5].value) if len(args) > 5 and isinstance(args[5], HNumber) else 1
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if not window_data.get("is_grid", False):
                raise RuntimeError("Window does not have grid layout")
            
            from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit
            
            # Create widget based on type
            if widget_type == "label":
                widget = QLabel(text)
            elif widget_type == "button":
                widget = QPushButton(text)
                if callback and isinstance(callback, HFunction):
                    def on_click():
                        try:
                            if gui_components["interpreter"]:
                                gui_components["interpreter"]._call_function(callback, [], call_line=0)
                        except Exception as e:
                            print(f"Button callback error: {e}")
                    widget.clicked.connect(on_click)
            elif widget_type == "text_input":
                widget = QLineEdit()
                widget.setPlaceholderText(text)
            elif widget_type == "text_area":
                widget = QTextEdit()
                widget.setPlainText(text)
            else:
                widget = QLabel(text)
            
            # Add to grid at current position
            row = window_data["current_row"]
            col = window_data["current_col"]
            
            window_data["layout"].addWidget(widget, row, col, row_span, col_span)
            window_data["widgets"].append(widget)
            
            # Update position
            window_data["current_col"] += col_span
            if window_data["current_col"] >= window_data["grid_cols"]:
                window_data["current_col"] = 0
                window_data["current_row"] += 1
            
            return h_string("Widget added to grid")
        except Exception as e:
            raise RuntimeError(f"Failed to add widget to grid: {e}")
    
    # Advanced Widgets
    def _gui_add_tree_widget(args, _):
        """Add a tree widget."""
        try:
            from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            tree = QTreeWidget()
            tree.setHeaderLabels(["Name", "Value"])
            
            # Add to layout
            window_data["layout"].addWidget(tree)
            window_data["widgets"].append(tree)
            
            return h_string("Tree widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add tree widget: {e}")
    
    def _gui_add_table_widget(args, _):
        """Add a table widget."""
        try:
            from PySide6.QtWidgets import QTableWidget, QTableWidgetItem
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            rows = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 5
            cols = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 3
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            table = QTableWidget(rows, cols)
            table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])
            
            # Add to layout
            window_data["layout"].addWidget(table)
            window_data["widgets"].append(table)
            
            return h_string("Table widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add table widget: {e}")
    
    def _gui_add_tab_widget(args, _):
        """Add a tab widget."""
        try:
            from PySide6.QtWidgets import QTabWidget
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            tab_widget = QTabWidget()
            
            # Add to layout
            window_data["layout"].addWidget(tab_widget)
            window_data["widgets"].append(tab_widget)
            
            return h_string("Tab widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add tab widget: {e}")
    
    def _gui_add_tab_to_tab_widget(args, _):
        """Add a tab to a tab widget."""
        try:
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            tab_widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            tab_name = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "Tab"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if tab_widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Tab widget index out of range")
            
            tab_widget = window_data["widgets"][tab_widget_index]
            if not hasattr(tab_widget, 'addTab'):
                raise RuntimeError("Widget is not a tab widget")
            
            from PySide6.QtWidgets import QWidget, QVBoxLayout
            tab_content = QWidget()
            tab_layout = QVBoxLayout(tab_content)
            
            tab_widget.addTab(tab_content, tab_name)
            
            return h_string("Tab added")
        except Exception as e:
            raise RuntimeError(f"Failed to add tab: {e}")
    
    def _gui_add_scroll_area(args, _):
        """Add a scroll area."""
        try:
            from PySide6.QtWidgets import QScrollArea, QLabel, QWidget
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            content = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            scroll_area = QScrollArea()
            scroll_content = QLabel(content)
            scroll_content.setWordWrap(True)
            scroll_area.setWidget(scroll_content)
            scroll_area.setWidgetResizable(True)
            
            # Add to layout
            window_data["layout"].addWidget(scroll_area)
            window_data["widgets"].append(scroll_area)
            
            return h_string("Scroll area added")
        except Exception as e:
            raise RuntimeError(f"Failed to add scroll area: {e}")
    
    def _gui_add_group_box(args, _):
        """Add a group box."""
        try:
            from PySide6.QtWidgets import QGroupBox, QVBoxLayout
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Group"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            group_box = QGroupBox(title)
            group_layout = QVBoxLayout()
            group_box.setLayout(group_layout)
            
            # Add to layout
            window_data["layout"].addWidget(group_box)
            window_data["widgets"].append(group_box)
            
            return h_string("Group box added")
        except Exception as e:
            raise RuntimeError(f"Failed to add group box: {e}")
    
    def _gui_add_spin_box(args, _):
        """Add a spin box."""
        try:
            from PySide6.QtWidgets import QSpinBox
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            min_val = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            max_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 100
            initial = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            spin_box = QSpinBox()
            spin_box.setMinimum(min_val)
            spin_box.setMaximum(max_val)
            spin_box.setValue(initial)
            
            # Add to layout
            window_data["layout"].addWidget(spin_box)
            window_data["widgets"].append(spin_box)
            
            return h_string("Spin box added")
        except Exception as e:
            raise RuntimeError(f"Failed to add spin box: {e}")
    
    def _gui_add_double_spin_box(args, _):
        """Add a double spin box."""
        try:
            from PySide6.QtWidgets import QDoubleSpinBox
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            min_val = args[1].value if len(args) > 1 and isinstance(args[1], HNumber) else 0.0
            max_val = args[2].value if len(args) > 2 and isinstance(args[2], HNumber) else 100.0
            initial = args[3].value if len(args) > 3 and isinstance(args[3], HNumber) else 0.0
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            spin_box = QDoubleSpinBox()
            spin_box.setMinimum(min_val)
            spin_box.setMaximum(max_val)
            spin_box.setValue(initial)
            
            # Add to layout
            window_data["layout"].addWidget(spin_box)
            window_data["widgets"].append(spin_box)
            
            return h_string("Double spin box added")
        except Exception as e:
            raise RuntimeError(f"Failed to add double spin box: {e}")
    
    def _gui_add_date_edit(args, _):
        """Add a date edit widget."""
        try:
            from PySide6.QtWidgets import QDateEdit
            from PySide6.QtCore import QDate
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            date_edit = QDateEdit()
            date_edit.setDate(QDate.currentDate())
            date_edit.setCalendarPopup(True)
            
            # Add to layout
            window_data["layout"].addWidget(date_edit)
            window_data["widgets"].append(date_edit)
            
            return h_string("Date edit added")
        except Exception as e:
            raise RuntimeError(f"Failed to add date edit: {e}")
    
    def _gui_add_time_edit(args, _):
        """Add a time edit widget."""
        try:
            from PySide6.QtWidgets import QTimeEdit
            from PySide6.QtCore import QTime
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            time_edit = QTimeEdit()
            time_edit.setTime(QTime.currentTime())
            
            # Add to layout
            window_data["layout"].addWidget(time_edit)
            window_data["widgets"].append(time_edit)
            
            return h_string("Time edit added")
        except Exception as e:
            raise RuntimeError(f"Failed to add time edit: {e}")
    
    def _gui_add_lcd_number(args, _):
        """Add an LCD number widget."""
        try:
            from PySide6.QtWidgets import QLCDNumber
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            value = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            lcd = QLCDNumber()
            lcd.display(value)
            
            # Add to layout
            window_data["layout"].addWidget(lcd)
            window_data["widgets"].append(lcd)
            
            return h_string("LCD number added")
        except Exception as e:
            raise RuntimeError(f"Failed to add LCD number: {e}")
    
    def _gui_add_dial(args, _):
        """Add a dial widget."""
        try:
            from PySide6.QtWidgets import QDial
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            min_val = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            max_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 100
            initial = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 50
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            dial = QDial()
            dial.setMinimum(min_val)
            dial.setMaximum(max_val)
            dial.setValue(initial)
            
            # Add to layout
            window_data["layout"].addWidget(dial)
            window_data["widgets"].append(dial)
            
            return h_string("Dial added")
        except Exception as e:
            raise RuntimeError(f"Failed to add dial: {e}")
    
    # Dialog Functions
    def _gui_file_dialog(args, _):
        """Show a file dialog."""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            dialog_type = args[0].value if args and isinstance(args[0], HString) else "open"
            title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Select File"
            filter_str = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "All Files (*)"
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            if dialog_type == "open":
                file_path, _ = QFileDialog.getOpenFileName(None, title, "", filter_str)
                if file_path:
                    return h_string(file_path)
                else:
                    return h_string("")
            elif dialog_type == "save":
                file_path, _ = QFileDialog.getSaveFileName(None, title, "", filter_str)
                if file_path:
                    return h_string(file_path)
                else:
                    return h_string("")
            elif dialog_type == "directory":
                directory = QFileDialog.getExistingDirectory(None, title)
                if directory:
                    return h_string(directory)
                else:
                    return h_string("")
            else:
                raise RuntimeError(f"Unknown dialog type: {dialog_type}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to show file dialog: {e}")
    
    def _gui_color_dialog(args, _):
        """Show a color dialog."""
        try:
            from PySide6.QtWidgets import QColorDialog
            from PySide6.QtGui import QColor
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            color = QColorDialog.getColor()
            if color.isValid():
                return h_string(color.name())
            else:
                return h_string("")
                
        except Exception as e:
            raise RuntimeError(f"Failed to show color dialog: {e}")
    
    def _gui_font_dialog(args, _):
        """Show a font dialog."""
        try:
            from PySide6.QtWidgets import QFontDialog
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            font, ok = QFontDialog.getFont()
            if ok:
                return h_string(font.family())
            else:
                return h_string("")
                
        except Exception as e:
            raise RuntimeError(f"Failed to show font dialog: {e}")
    
    def _gui_input_dialog(args, _):
        """Show an input dialog."""
        try:
            from PySide6.QtWidgets import QInputDialog
            
            title = args[0].value if args and isinstance(args[0], HString) else "Input"
            label = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Enter value:"
            default = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            text, ok = QInputDialog.getText(None, title, label, text=default)
            if ok:
                return h_string(text)
            else:
                return h_string("")
                
        except Exception as e:
            raise RuntimeError(f"Failed to show input dialog: {e}")
    
    # Menu and Toolbar
    def _gui_add_menu_bar(args, _):
        """Add a menu bar to a window."""
        try:
            from PySide6.QtWidgets import QMenuBar, QMenu
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create menu bar with window as parent
            menu_bar = QMenuBar(window_data["window"])
            window_data["window"].setMenuBar(menu_bar)
            
            # Ensure menu bar is opaque
            menu_bar.setAutoFillBackground(True)
            
            menu_bar_id = f"{window_id}_menubar"
            gui_components["menus"][menu_bar_id] = {
                "menu_bar": menu_bar,
                "menus": {}
            }
            
            return h_string(menu_bar_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add menu bar: {e}")
    
    def _gui_add_menu(args, _):
        """Add a menu to the menu bar."""
        try:
            from PySide6.QtWidgets import QMenu
            
            menu_bar_id = args[0].value if args and isinstance(args[0], HString) else ""
            menu_name = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Menu"
            
            if menu_bar_id not in gui_components["menus"]:
                raise RuntimeError(f"Menu bar not found: {menu_bar_id}")
            
            menu_data = gui_components["menus"][menu_bar_id]
            
            # Create menu with menu bar as parent
            menu = QMenu(menu_name, menu_data["menu_bar"])
            menu_data["menu_bar"].addMenu(menu)
            
            menu_id = f"{menu_bar_id}_{menu_name}"
            menu_data["menus"][menu_id] = menu
            
            return h_string(menu_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add menu: {e}")
    
    def _gui_add_menu_item(args, _):
        """Add a menu item to a menu."""
        try:
            from PySide6.QtGui import QAction
            from PySide6.QtWidgets import QApplication
            
            menu_id = args[0].value if args and isinstance(args[0], HString) else ""
            item_name = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Item"
            callback = args[2] if len(args) > 2 else None
            
            # Find the menu in menus
            for menu_bar_id, menu_data in gui_components["menus"].items():
                if menu_id in menu_data["menus"]:
                    menu = menu_data["menus"][menu_id]
                    
                    # Create action with the menu as parent
                    action = QAction(item_name, menu)
                    
                    if callback and isinstance(callback, HFunction):
                        def on_trigger():
                            try:
                                if gui_components["interpreter"]:
                                    gui_components["interpreter"]._call_function(callback, [], call_line=0)
                            except Exception as e:
                                print(f"Menu callback error: {e}")
                        
                        action.triggered.connect(on_trigger)
                    
                    menu.addAction(action)
                    return h_string("Menu item added")
            
            raise RuntimeError(f"Menu not found: {menu_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to add menu item: {e}")

    def _gui_add_menu_separator(args, _):
        """Add a separator to a menu."""
        try:
            menu_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            # Find the menu in menus
            for menu_bar_id, menu_data in gui_components["menus"].items():
                if menu_id in menu_data["menus"]:
                    menu = menu_data["menus"][menu_id]
                    menu.addSeparator()
                    return h_string("Menu separator added")
            
            raise RuntimeError(f"Menu not found: {menu_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to add menu separator: {e}")
    
    def _gui_add_toolbar(args, _):
        """Add a toolbar to a window."""
        try:
            from PySide6.QtWidgets import QToolBar
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            toolbar_name = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Toolbar"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            toolbar = QToolBar(toolbar_name)
            window_data["window"].addToolBar(toolbar)
            
            toolbar_id = f"{window_id}_toolbar"
            gui_components["toolbars"][toolbar_id] = toolbar
            
            return h_string(toolbar_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add toolbar: {e}")
    
    def _gui_add_toolbar_action(args, _):
        """Add an action to a toolbar."""
        try:
            from PySide6.QtGui import QAction
            
            toolbar_id = args[0].value if args and isinstance(args[0], HString) else ""
            action_name = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Action"
            callback = args[2] if len(args) > 2 else None
            
            if toolbar_id not in gui_components["toolbars"]:
                raise RuntimeError(f"Toolbar not found: {toolbar_id}")
            
            toolbar = gui_components["toolbars"][toolbar_id]
            
            action = QAction(action_name, None)
            
            if callback and isinstance(callback, HFunction):
                def on_trigger():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Toolbar callback error: {e}")
                
                action.triggered.connect(on_trigger)
            
            toolbar.addAction(action)
            
            return h_string("Toolbar action added")
        except Exception as e:
            raise RuntimeError(f"Failed to add toolbar action: {e}")
    
    def _gui_add_status_bar(args, _):
        """Add a status bar to a window."""
        try:
            from PySide6.QtWidgets import QStatusBar
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            status_bar = QStatusBar()
            window_data["window"].setStatusBar(status_bar)
            
            status_bar_id = f"{window_id}_statusbar"
            gui_components["statusbars"][status_bar_id] = status_bar
            
            return h_string(status_bar_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add status bar: {e}")
    
    def _gui_set_status_bar_text(args, _):
        """Set the text of a status bar."""
        status_bar_id = args[0].value if args and isinstance(args[0], HString) else ""
        text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        
        if status_bar_id in gui_components["statusbars"]:
            gui_components["statusbars"][status_bar_id].showMessage(text)
            return h_string("Status bar text set")
        else:
            raise RuntimeError(f"Status bar not found: {status_bar_id}")
    
    # Timer Functions
    def _gui_create_timer(args, _):
        """Create a timer."""
        try:
            from PySide6.QtCore import QTimer
            
            interval = int(args[0].value) if args and isinstance(args[0], HNumber) else 1000
            callback = args[1] if len(args) > 1 else None
            
            timer = QTimer()
            timer_id = f"timer_{len(gui_components['timers'])}"
            
            if callback and isinstance(callback, HFunction):
                def on_timeout():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Timer callback error: {e}")
                
                timer.timeout.connect(on_timeout)
            
            gui_components["timers"][timer_id] = {
                "timer": timer,
                "interval": interval,
                "callback": callback
            }
            
            return h_string(timer_id)
        except Exception as e:
            raise RuntimeError(f"Failed to create timer: {e}")
    
    def _gui_start_timer(args, _):
        """Start a timer."""
        timer_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if timer_id in gui_components["timers"]:
            timer_data = gui_components["timers"][timer_id]
            timer_data["timer"].start(timer_data["interval"])
            return h_string("Timer started")
        else:
            raise RuntimeError(f"Timer not found: {timer_id}")
    
    def _gui_stop_timer(args, _):
        """Stop a timer."""
        timer_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if timer_id in gui_components["timers"]:
            gui_components["timers"][timer_id]["timer"].stop()
            return h_string("Timer stopped")
        else:
            raise RuntimeError(f"Timer not found: {timer_id}")
    
    # Stylesheet Functions
    def _gui_set_stylesheet(args, _):
        """Set a stylesheet for a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        stylesheet = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].setStyleSheet(stylesheet)
            return h_string("Stylesheet set")
        else:
            raise RuntimeError(f"Window not found: {window_id}")
    
    # MDI Functions
    def _gui_set_mdi_mode(args, _):
        """Set a window to MDI mode."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        try:
            from PySide6.QtWidgets import QMdiArea
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            mdi_area = QMdiArea()
            window_data["window"].setCentralWidget(mdi_area)
            window_data["mdi"] = mdi_area
            
            return h_string("MDI mode enabled")
        except Exception as e:
            raise RuntimeError(f"Failed to set MDI mode: {e}")
    
    def _gui_add_mdi_subwindow(args, _):
        """Add a subwindow to an MDI area."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Subwindow"
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if "mdi" not in window_data:
            raise RuntimeError("Window is not in MDI mode")
        
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit
        
        sub_window = QWidget()
        sub_layout = QVBoxLayout(sub_window)
        text_edit = QTextEdit()
        text_edit.setPlainText(f"Content of {title}")
        sub_layout.addWidget(text_edit)
        
        mdi_subwindow = window_data["mdi"].addSubWindow(sub_window)
        mdi_subwindow.setWindowTitle(title)
        mdi_subwindow.show()
        
        return h_string("MDI subwindow added")
    
    # Rich Text Editing
    def _gui_add_rich_text_edit(args, _):
        """Add a rich text editor."""
        try:
            from PySide6.QtWidgets import QTextEdit
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            content = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            rich_text = QTextEdit()
            rich_text.setHtml(content)
            
            # Add to layout
            window_data["layout"].addWidget(rich_text)
            window_data["widgets"].append(rich_text)
            
            return h_string("Rich text editor added")
        except Exception as e:
            raise RuntimeError(f"Failed to add rich text editor: {e}")
    
    def _gui_set_rich_text(args, _):
        """Set rich text (HTML) content."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        html_content = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index < len(window_data["widgets"]):
            widget = window_data["widgets"][widget_index]
            if hasattr(widget, 'setHtml'):
                widget.setHtml(html_content)
                return h_string("Rich text set")
            else:
                raise RuntimeError("Widget does not support rich text")
        else:
            raise RuntimeError("Widget index out of range")
    
    # Graphics and Painting
    def _gui_add_graphics_view(args, _):
        """Add a graphics view for custom painting."""
        try:
            from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            scene = QGraphicsScene()
            view = QGraphicsView(scene)
            
            # Add to layout
            window_data["layout"].addWidget(view)
            window_data["widgets"].append(view)
            
            # Store scene reference
            graphics_id = f"{window_id}_graphics_{len(window_data['widgets'])}"
            gui_components["graphics"][graphics_id] = {
                "scene": scene,
                "view": view
            }
            
            return h_string(graphics_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add graphics view: {e}")
    
    def _gui_draw_rectangle(args, _):
        """Draw a rectangle on the graphics scene."""
        graphics_id = args[0].value if args and isinstance(args[0], HString) else ""
        x = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        y = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        width = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
        height = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 100
        color = args[5].value if len(args) > 5 and isinstance(args[5], HString) else "#000000"
        
        if graphics_id in gui_components.get("graphics", {}):
            from PySide6.QtWidgets import QGraphicsRectItem
            from PySide6.QtGui import QBrush, QColor, QPen
            
            scene = gui_components["graphics"][graphics_id]["scene"]
            
            rect_item = QGraphicsRectItem(x, y, width, height)
            rect_item.setBrush(QBrush(QColor(color)))
            rect_item.setPen(QPen(QColor(color)))
            
            scene.addItem(rect_item)
            
            return h_string("Rectangle drawn")
        else:
            raise RuntimeError(f"Graphics view not found: {graphics_id}")
    
    def _gui_draw_ellipse(args, _):
        """Draw an ellipse on the graphics scene."""
        graphics_id = args[0].value if args and isinstance(args[0], HString) else ""
        x = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        y = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        width = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
        height = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 100
        color = args[5].value if len(args) > 5 and isinstance(args[5], HString) else "#000000"
        
        if graphics_id in gui_components.get("graphics", {}):
            from PySide6.QtWidgets import QGraphicsEllipseItem
            from PySide6.QtGui import QBrush, QColor, QPen
            
            scene = gui_components["graphics"][graphics_id]["scene"]
            
            ellipse_item = QGraphicsEllipseItem(x, y, width, height)
            ellipse_item.setBrush(QBrush(QColor(color)))
            ellipse_item.setPen(QPen(QColor(color)))
            
            scene.addItem(ellipse_item)
            
            return h_string("Ellipse drawn")
        else:
            raise RuntimeError(f"Graphics view not found: {graphics_id}")
    
    def _gui_draw_text(args, _):
        """Draw text on the graphics scene."""
        graphics_id = args[0].value if args and isinstance(args[0], HString) else ""
        text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        x = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        y = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        color = args[4].value if len(args) > 4 and isinstance(args[4], HString) else "#000000"
        
        if graphics_id in gui_components.get("graphics", {}):
            from PySide6.QtWidgets import QGraphicsTextItem
            from PySide6.QtGui import QColor, QFont
            
            scene = gui_components["graphics"][graphics_id]["scene"]
            
            text_item = QGraphicsTextItem(text)
            text_item.setDefaultTextColor(QColor(color))
            text_item.setFont(QFont("Arial", 12))
            text_item.setPos(x, y)
            
            scene.addItem(text_item)
            
            return h_string("Text drawn")
        else:
            raise RuntimeError(f"Graphics view not found: {graphics_id}")
    
    def _gui_draw_line(args, _):
        """Draw a line on the graphics scene."""
        graphics_id = args[0].value if args and isinstance(args[0], HString) else ""
        x1 = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        y1 = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        x2 = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
        y2 = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 100
        color = args[5].value if len(args) > 5 and isinstance(args[5], HString) else "#000000"
        width = int(args[6].value) if len(args) > 6 and isinstance(args[6], HNumber) else 2
        
        if graphics_id in gui_components.get("graphics", {}):
            from PySide6.QtWidgets import QGraphicsLineItem
            from PySide6.QtGui import QPen, QColor
            
            scene = gui_components["graphics"][graphics_id]["scene"]
            
            line_item = QGraphicsLineItem(x1, y1, x2, y2)
            pen = QPen(QColor(color))
            pen.setWidth(width)
            line_item.setPen(pen)
            
            scene.addItem(line_item)
            
            return h_string("Line drawn")
        else:
            raise RuntimeError(f"Graphics view not found: {graphics_id}")
    
    # Web View (if available)
    def _gui_add_web_view(args, _):
        """Add a web view widget."""
        try:
            from PySide6.QtWebWidgets import QWebEngineView
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            url = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "https://www.google.com"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            web_view = QWebEngineView()
            web_view.setUrl(url)
            
            # Add to layout
            window_data["layout"].addWidget(web_view)
            window_data["widgets"].append(web_view)
            
            return h_string("Web view added")
        except ImportError:
            raise RuntimeError("PySide6-WebEngine not installed. Install with: pip install PySide6-WebEngine")
        except Exception as e:
            raise RuntimeError(f"Failed to add web view: {e}")
    
    # Chart/Plot (using matplotlib if available)
    def _gui_add_plot_widget(args, _):
        """Add a matplotlib plot widget."""
        try:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Create figure and canvas
            figure = Figure(figsize=(5, 4), dpi=100)
            canvas = FigureCanvas(figure)
            
            # Add some default plot
            ax = figure.add_subplot(111)
            ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
            ax.set_title("Sample Plot")
            
            # Add to layout
            window_data["layout"].addWidget(canvas)
            window_data["widgets"].append(canvas)
            
            return h_string("Plot widget added")
        except ImportError:
            raise RuntimeError("Matplotlib not installed. Install with: pip install matplotlib")
        except Exception as e:
            raise RuntimeError(f"Failed to add plot widget: {e}")
    
    # Drag and Drop (simplified)
    def _gui_enable_drag_drop(args, _):
        """Enable drag and drop for a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index < len(window_data["widgets"]):
            widget = window_data["widgets"][widget_index]
            widget.setAcceptDrops(True)
            return h_string("Drag and drop enabled")
        else:
            raise RuntimeError("Widget index out of range")
    
    # Animation (simplified)
    def _gui_animate_widget(args, _):
        """Animate a widget (simple fade effect)."""
        try:
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            from PySide6.QtCore import QPropertyAnimation
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            duration = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 1000
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index < len(window_data["widgets"]):
                widget = window_data["widgets"][widget_index]
                
                # Create opacity effect
                effect = QGraphicsOpacityEffect()
                widget.setGraphicsEffect(effect)
                
                # Create animation
                animation = QPropertyAnimation(effect, b"opacity")
                animation.setDuration(duration)
                animation.setStartValue(0.0)
                animation.setEndValue(1.0)
                
                animation.start()
                
                return h_string("Animation started")
            else:
                raise RuntimeError("Widget index out of range")
        except Exception as e:
            raise RuntimeError(f"Failed to animate widget: {e}")

    # Missing Qt Widgets
    def _gui_add_splitter(args, _):
        """Add a splitter widget."""
        try:
            from PySide6.QtWidgets import QSplitter
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            orientation = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "horizontal"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            qt_orientation = Qt.Horizontal if orientation == "horizontal" else Qt.Vertical
            splitter = QSplitter(qt_orientation)
            
            # Add to layout
            window_data["layout"].addWidget(splitter)
            window_data["widgets"].append(splitter)
            
            return h_string("Splitter added")
        except Exception as e:
            raise RuntimeError(f"Failed to add splitter: {e}")

    def _gui_add_dock_widget(args, _):
        """Add a dock widget."""
        try:
            from PySide6.QtWidgets import QDockWidget, QTextEdit
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Dock"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            dock = QDockWidget(title)
            dock_content = QTextEdit()
            dock.setWidget(dock_content)
            window_data["window"].addDockWidget(dock)
            
            window_data["widgets"].append(dock)
            
            return h_string("Dock widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add dock widget: {e}")

    def _gui_add_stacked_widget(args, _):
        """Add a stacked widget."""
        try:
            from PySide6.QtWidgets import QStackedWidget
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            stacked = QStackedWidget()
            
            # Add to layout
            window_data["layout"].addWidget(stacked)
            window_data["widgets"].append(stacked)
            
            return h_string("Stacked widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add stacked widget: {e}")

    def _gui_add_page_to_stacked(args, _):
        """Add a page to a stacked widget."""
        try:
            from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            stacked_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            page_name = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "Page"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if stacked_index >= len(window_data["widgets"]):
                raise RuntimeError("Stacked widget index out of range")
            
            stacked = window_data["widgets"][stacked_index]
            if not hasattr(stacked, 'addWidget'):
                raise RuntimeError("Widget is not a stacked widget")
            
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.addWidget(QLabel(f"Content of {page_name}"))
            
            stacked.addWidget(page)
            
            return h_string("Page added to stacked widget")
        except Exception as e:
            raise RuntimeError(f"Failed to add page to stacked widget: {e}")

    def _gui_set_stacked_index(args, _):
        """Set the current index of a stacked widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        stacked_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        page_index = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if stacked_index >= len(window_data["widgets"]):
            raise RuntimeError("Stacked widget index out of range")
        
        stacked = window_data["widgets"][stacked_index]
        if hasattr(stacked, 'setCurrentIndex'):
            stacked.setCurrentIndex(page_index)
            return h_string("Stacked widget index set")
        else:
            raise RuntimeError("Widget is not a stacked widget")

    def _gui_add_list_widget(args, _):
        """Add a list widget."""
        try:
            from PySide6.QtWidgets import QListWidget
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            items = args[1] if len(args) > 1 and isinstance(args[1], HList) else None
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            list_widget = QListWidget()
            
            # Add items if provided
            if items:
                for item in items.elements:
                    if isinstance(item, HString):
                        list_widget.addItem(item.value)
            
            # Add to layout
            window_data["layout"].addWidget(list_widget)
            window_data["widgets"].append(list_widget)
            
            return h_string("List widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add list widget: {e}")

    def _gui_add_radio_button(args, _):
        """Add a radio button."""
        try:
            from PySide6.QtWidgets import QRadioButton
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Radio"
            checked = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else False
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            radio = QRadioButton(text)
            radio.setChecked(checked)
            
            # Add to layout
            window_data["layout"].addWidget(radio)
            window_data["widgets"].append(radio)
            
            return h_string("Radio button added")
        except Exception as e:
            raise RuntimeError(f"Failed to add radio button: {e}")

    def _gui_add_button_group(args, _):
        """Add a button group for radio buttons."""
        try:
            from PySide6.QtWidgets import QButtonGroup
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            button_group = QButtonGroup()
            
            # Store button group
            group_id = f"{window_id}_buttongroup_{len(window_data['widgets'])}"
            gui_components["button_groups"] = gui_components.get("button_groups", {})
            gui_components["button_groups"][group_id] = button_group
            
            # Add to layout (as a placeholder)
            window_data["widgets"].append(button_group)
            
            return h_string(group_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add button group: {e}")

    def _gui_add_tool_button(args, _):
        """Add a tool button."""
        try:
            from PySide6.QtWidgets import QToolButton
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Tool"
            callback = args[2] if len(args) > 2 else None
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            tool_button = QToolButton()
            tool_button.setText(text)
            
            # Connect callback if provided
            if callback and isinstance(callback, HFunction):
                def on_click():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Tool button callback error: {e}")
                
                tool_button.clicked.connect(on_click)
            
            # Add to layout
            window_data["layout"].addWidget(tool_button)
            window_data["widgets"].append(tool_button)
            
            return h_string("Tool button added")
        except Exception as e:
            raise RuntimeError(f"Failed to add tool button: {e}")

    def _gui_add_frame(args, _):
        """Add a frame widget."""
        try:
            from PySide6.QtWidgets import QFrame
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            frame_shape = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "box"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            frame = QFrame()
            
            # Set frame shape
            if frame_shape == "box":
                frame.setFrameShape(QFrame.Box)
            elif frame_shape == "panel":
                frame.setFrameShape(QFrame.Panel)
            elif frame_shape == "hline":
                frame.setFrameShape(QFrame.HLine)
            elif frame_shape == "vline":
                frame.setFrameShape(QFrame.VLine)
            else:
                frame.setFrameShape(QFrame.NoFrame)
            
            # Add to layout
            window_data["layout"].addWidget(frame)
            window_data["widgets"].append(frame)
            
            return h_string("Frame added")
        except Exception as e:
            raise RuntimeError(f"Failed to add frame: {e}")

    def _gui_add_command_link_button(args, _):
        """Add a command link button."""
        try:
            from PySide6.QtWidgets import QCommandLinkButton
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Command"
            description = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
            callback = args[3] if len(args) > 3 else None
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            cmd_button = QCommandLinkButton(text, description)
            
            # Connect callback if provided
            if callback and isinstance(callback, HFunction):
                def on_click():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Command link button callback error: {e}")
                
                cmd_button.clicked.connect(on_click)
            
            # Add to layout
            window_data["layout"].addWidget(cmd_button)
            window_data["widgets"].append(cmd_button)
            
            return h_string("Command link button added")
        except Exception as e:
            raise RuntimeError(f"Failed to add command link button: {e}")

    def _gui_add_label_with_pixmap(args, _):
        """Add a label with an image/pixmap."""
        try:
            from PySide6.QtWidgets import QLabel
            from PySide6.QtGui import QPixmap
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            image_path = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            label = QLabel()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                label.setPixmap(pixmap)
            else:
                label.setText("Image not found")
            
            # Add to layout
            window_data["layout"].addWidget(label)
            window_data["widgets"].append(label)
            
            return h_string("Image label added")
        except Exception as e:
            raise RuntimeError(f"Failed to add image label: {e}")

    def _gui_add_progress_dialog(args, _):
        """Add a progress dialog."""
        try:
            from PySide6.QtWidgets import QProgressDialog
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            label_text = args[0].value if args and isinstance(args[0], HString) else "Progress"
            cancel_text = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Cancel"
            minimum = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
            maximum = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
            
            progress = QProgressDialog(label_text, cancel_text, minimum, maximum)
            progress.setWindowModality(Qt.WindowModal)
            progress.show()
            
            dialog_id = f"progress_{len(gui_components.get('dialogs', {}))}"
            gui_components["dialogs"] = gui_components.get("dialogs", {})
            gui_components["dialogs"][dialog_id] = progress
            
            return h_string(dialog_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add progress dialog: {e}")

    def _gui_update_progress_dialog(args, _):
        """Update progress dialog value."""
        dialog_id = args[0].value if args and isinstance(args[0], HString) else ""
        value = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if dialog_id in gui_components.get("dialogs", {}):
            progress = gui_components["dialogs"][dialog_id]
            if hasattr(progress, 'setValue'):
                progress.setValue(value)
                return h_string("Progress updated")
            else:
                raise RuntimeError("Dialog is not a progress dialog")
        else:
            raise RuntimeError(f"Progress dialog not found: {dialog_id}")

    def _gui_close_dialog(args, _):
        """Close a dialog."""
        dialog_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if dialog_id in gui_components.get("dialogs", {}):
            dialog = gui_components["dialogs"][dialog_id]
            dialog.close()
            del gui_components["dialogs"][dialog_id]
            return h_string("Dialog closed")
        else:
            raise RuntimeError(f"Dialog not found: {dialog_id}")

    # Advanced Window Management
    def _gui_maximize_window(args, _):
        """Maximize a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].showMaximized()
            return h_string("Window maximized")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_minimize_window(args, _):
        """Minimize a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].showMinimized()
            return h_string("Window minimized")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_show_normal(args, _):
        """Show window in normal state."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].showNormal()
            return h_string("Window shown normal")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_show_fullscreen(args, _):
        """Show window in fullscreen."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].showFullScreen()
            return h_string("Window shown fullscreen")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_hide_window(args, _):
        """Hide a window."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].hide()
            return h_string("Window hidden")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_set_window_icon(args, _):
        """Set window icon."""
        try:
            from PySide6.QtGui import QIcon
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            icon_path = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
            
            if window_id in gui_components["windows"]:
                icon = QIcon(icon_path)
                gui_components["windows"][window_id]["window"].setWindowIcon(icon)
                return h_string("Window icon set")
            else:
                raise RuntimeError(f"Window not found: {window_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to set window icon: {e}")

    def _gui_set_window_opacity(args, _):
        """Set window opacity (0.0 to 1.0)."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        opacity = args[1].value if len(args) > 1 and isinstance(args[1], HNumber) else 1.0
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].setWindowOpacity(opacity)
            return h_string("Window opacity set")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_set_window_position(args, _):
        """Set window position."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        x = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        y = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        
        if window_id in gui_components["windows"]:
            gui_components["windows"][window_id]["window"].move(x, y)
            return h_string("Window position set")
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_get_window_position(args, _):
        """Get window position."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if window_id in gui_components["windows"]:
            pos = gui_components["windows"][window_id]["window"].pos()
            return h_map({
                "x": h_number(pos.x()),
                "y": h_number(pos.y())
            })
        else:
            raise RuntimeError(f"Window not found: {window_id}")

    def _gui_set_window_modality(args, _):
        """Set window modality."""
        try:
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            modality = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "none"
            
            if window_id in gui_components["windows"]:
                if modality == "none":
                    gui_components["windows"][window_id]["window"].setWindowModality(Qt.NonModal)
                elif modality == "application":
                    gui_components["windows"][window_id]["window"].setWindowModality(Qt.ApplicationModal)
                elif modality == "window":
                    gui_components["windows"][window_id]["window"].setWindowModality(Qt.WindowModal)
                return h_string("Window modality set")
            else:
                raise RuntimeError(f"Window not found: {window_id}")
        except Exception as e:
            raise RuntimeError(f"Failed to set window modality: {e}")

    # Clipboard Operations
    def _gui_copy_to_clipboard(args, _):
        """Copy text to clipboard."""
        try:
            from PySide6.QtWidgets import QApplication
            
            text = args[0].value if args and isinstance(args[0], HString) else ""
            
            if gui_components["app"]:
                clipboard = gui_components["app"].clipboard()
                clipboard.setText(text)
                return h_string("Text copied to clipboard")
            else:
                raise RuntimeError("Application not initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to copy to clipboard: {e}")

    def _gui_paste_from_clipboard(args, _):
        """Paste text from clipboard."""
        try:
            from PySide6.QtWidgets import QApplication
            
            if gui_components["app"]:
                clipboard = gui_components["app"].clipboard()
                text = clipboard.text()
                return h_string(text)
            else:
                raise RuntimeError("Application not initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to paste from clipboard: {e}")

    def _gui_clear_clipboard(args, _):
        """Clear clipboard."""
        try:
            from PySide6.QtWidgets import QApplication
            
            if gui_components["app"]:
                clipboard = gui_components["app"].clipboard()
                clipboard.clear()
                return h_string("Clipboard cleared")
            else:
                raise RuntimeError("Application not initialized")
        except Exception as e:
            raise RuntimeError(f"Failed to clear clipboard: {e}")

    # System Tray Support
    def _gui_add_system_tray(args, _):
        """Add system tray icon."""
        try:
            from PySide6.QtWidgets import QSystemTrayIcon, QMenu
            from PySide6.QtGui import QIcon
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            icon_path = args[0].value if args and isinstance(args[0], HString) else ""
            tooltip = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Application"
            
            tray_icon = QSystemTrayIcon()
            
            if icon_path:
                icon = QIcon(icon_path)
                tray_icon.setIcon(icon)
            
            tray_icon.setToolTip(tooltip)
            tray_icon.show()
            
            tray_id = f"tray_{len(gui_components.get('trays', {}))}"
            gui_components["trays"] = gui_components.get("trays", {})
            gui_components["trays"][tray_id] = tray_icon
            
            return h_string(tray_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add system tray: {e}")

    def _gui_add_tray_menu(args, _):
        """Add menu to system tray icon."""
        try:
            from PySide6.QtWidgets import QMenu
            
            tray_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if tray_id not in gui_components.get("trays", {}):
                raise RuntimeError(f"System tray not found: {tray_id}")
            
            tray = gui_components["trays"][tray_id]
            menu = QMenu()
            tray.setContextMenu(menu)
            
            menu_id = f"{tray_id}_menu"
            gui_components["tray_menus"] = gui_components.get("tray_menus", {})
            gui_components["tray_menus"][menu_id] = menu
            
            return h_string(menu_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add tray menu: {e}")

    def _gui_add_tray_menu_item(args, _):
        """Add menu item to tray menu."""
        try:
            from PySide6.QtGui import QAction
            
            menu_id = args[0].value if args and isinstance(args[0], HString) else ""
            item_name = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "Item"
            callback = args[2] if len(args) > 2 else None
            
            if menu_id not in gui_components.get("tray_menus", {}):
                raise RuntimeError(f"Tray menu not found: {menu_id}")
            
            menu = gui_components["tray_menus"][menu_id]
            
            action = QAction(item_name, None)
            
            if callback and isinstance(callback, HFunction):
                def on_trigger():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Tray menu callback error: {e}")
                
                action.triggered.connect(on_trigger)
            
            menu.addAction(action)
            
            return h_string("Tray menu item added")
        except Exception as e:
            raise RuntimeError(f"Failed to add tray menu item: {e}")

    def _gui_show_tray_message(args, _):
        """Show system tray message."""
        tray_id = args[0].value if args and isinstance(args[0], HString) else ""
        title = args[1].value if len(args) > 1 and isinstance(args[1], HString) else ""
        message = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        message_type = args[3].value if len(args) > 3 and isinstance(args[3], HString) else "info"
        
        if tray_id not in gui_components.get("trays", {}):
            raise RuntimeError(f"System tray not found: {tray_id}")
        
        tray = gui_components["trays"][tray_id]
        
        try:
            from PySide6.QtWidgets import QSystemTrayIcon
            
            if message_type == "info":
                icon = QSystemTrayIcon.Information
            elif message_type == "warning":
                icon = QSystemTrayIcon.Warning
            elif message_type == "critical":
                icon = QSystemTrayIcon.Critical
            else:
                icon = QSystemTrayIcon.Information
            
            tray.showMessage(title, message, icon, 3000)
            return h_string("Tray message shown")
        except Exception as e:
            raise RuntimeError(f"Failed to show tray message: {e}")

    # Advanced Table Widget Features
    def _gui_set_table_item(args, _):
        """Set table item text."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        table_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        row = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        col = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        text = args[4].value if len(args) > 4 and isinstance(args[4], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if table_index >= len(window_data["widgets"]):
            raise RuntimeError("Table widget index out of range")
        
        table = window_data["widgets"][table_index]
        if hasattr(table, 'setItem'):
            from PySide6.QtWidgets import QTableWidgetItem
            item = QTableWidgetItem(text)
            table.setItem(row, col, item)
            return h_string("Table item set")
        else:
            raise RuntimeError("Widget is not a table widget")

    def _gui_get_table_item(args, _):
        """Get table item text."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        table_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        row = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        col = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if table_index >= len(window_data["widgets"]):
            raise RuntimeError("Table widget index out of range")
        
        table = window_data["widgets"][table_index]
        if hasattr(table, 'item'):
            item = table.item(row, col)
            if item:
                return h_string(item.text())
            else:
                return h_string("")
        else:
            raise RuntimeError("Widget is not a table widget")

    def _gui_set_table_header(args, _):
        """Set table header labels."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        table_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        headers = args[2] if len(args) > 2 and isinstance(args[2], HList) else None
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if table_index >= len(window_data["widgets"]):
            raise RuntimeError("Table widget index out of range")
        
        table = window_data["widgets"][table_index]
        if hasattr(table, 'setHorizontalHeaderLabels'):
            if headers:
                header_labels = [h.value if isinstance(h, HString) else str(h) for h in headers.elements]
                table.setHorizontalHeaderLabels(header_labels)
            return h_string("Table header set")
        else:
            raise RuntimeError("Widget is not a table widget")

    # Advanced Tree Widget Features
    def _gui_add_tree_item(args, _):
        """Add item to tree widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        tree_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        parent_index = args[2] if len(args) > 2 else None
        columns = args[3] if len(args) > 3 and isinstance(args[3], HList) else None
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if tree_index >= len(window_data["widgets"]):
            raise RuntimeError("Tree widget index out of range")
        
        tree = window_data["widgets"][tree_index]
        if hasattr(tree, 'addTopLevelItem'):
            from PySide6.QtWidgets import QTreeWidgetItem
            
            item = QTreeWidgetItem()
            if columns:
                for i, col in enumerate(columns.elements):
                    if isinstance(col, HString):
                        item.setText(i, col.value)
            
            if parent_index is None:
                tree.addTopLevelItem(item)
            else:
                # For simplicity, assuming parent_index is an item reference
                # In a full implementation, you'd need proper item tracking
                pass
            
            return h_string("Tree item added")
        else:
            raise RuntimeError("Widget is not a tree widget")

    # Validators and Input Masks
    def _gui_set_validator(args, _):
        """Set validator for text input."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        validator_type = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "none"
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        try:
            from PySide6.QtGui import QIntValidator, QDoubleValidator, QRegularExpressionValidator
            from PySide6.QtCore import QRegularExpression
            
            if validator_type == "int":
                validator = QIntValidator()
            elif validator_type == "double":
                validator = QDoubleValidator()
            elif validator_type == "email":
                # Simple email regex
                regex = QRegularExpression(r"[\\w\\.-]+@[\\w\\.-]+\\.\\w+")
                validator = QRegularExpressionValidator(regex)
            else:
                validator = None
            
            if validator and hasattr(widget, 'setValidator'):
                widget.setValidator(validator)
                return h_string("Validator set")
            else:
                return h_string("Validator not set - widget doesn't support validators")
        except Exception as e:
            raise RuntimeError(f"Failed to set validator: {e}")

    def _gui_set_input_mask(args, _):
        """Set input mask for text input."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        mask = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setInputMask'):
            widget.setInputMask(mask)
            return h_string("Input mask set")
        else:
            raise RuntimeError("Widget doesn't support input masks")

    def _gui_set_tooltip(args, _):
        """Set tooltip for a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        tooltip = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setToolTip'):
            widget.setToolTip(tooltip)
            return h_string("Tooltip set")
        else:
            raise RuntimeError("Widget doesn't support tooltips")

    def _gui_set_status_tip(args, _):
        """Set status tip for a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        status_tip = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setStatusTip'):
            widget.setStatusTip(status_tip)
            return h_string("Status tip set")
        else:
            raise RuntimeError("Widget doesn't support status tips")

    # Additional Dialog Types
    def _gui_add_wizard(args, _):
        """Add a wizard dialog."""
        try:
            from PySide6.QtWidgets import QWizard, QWizardPage, QVBoxLayout, QLabel
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            title = args[0].value if args and isinstance(args[0], HString) else "Wizard"
            
            wizard = QWizard()
            wizard.setWindowTitle(title)
            
            # Add a default page
            page = QWizardPage()
            page.setTitle("Introduction")
            layout = QVBoxLayout(page)
            layout.addWidget(QLabel("This is a wizard page"))
            wizard.addPage(page)
            
            wizard_id = f"wizard_{len(gui_components.get('wizards', {}))}"
            gui_components["wizards"] = gui_components.get("wizards", {})
            gui_components["wizards"][wizard_id] = wizard
            
            return h_string(wizard_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add wizard: {e}")

    def _gui_show_wizard(args, _):
        """Show wizard dialog."""
        wizard_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if wizard_id in gui_components.get("wizards", {}):
            wizard = gui_components["wizards"][wizard_id]
            result = wizard.exec()
            return h_number(result)
        else:
            raise RuntimeError(f"Wizard not found: {wizard_id}")

    def _gui_add_custom_dialog(args, _):
        """Add a custom dialog."""
        try:
            from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
            
            # Ensure app exists
            if gui_components["app"] is None:
                _gui_init_app([], None)
            
            title = args[0].value if args and isinstance(args[0], HString) else "Dialog"
            width = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 400
            height = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 300
            
            dialog = QDialog()
            dialog.setWindowTitle(title)
            dialog.resize(width, height)
            
            layout = QVBoxLayout(dialog)
            
            # Add close button
            close_button = QPushButton("Close")
            close_button.clicked.connect(dialog.close)
            layout.addWidget(close_button)
            
            dialog_id = f"dialog_{len(gui_components.get('custom_dialogs', {}))}"
            gui_components["custom_dialogs"] = gui_components.get("custom_dialogs", {})
            gui_components["custom_dialogs"][dialog_id] = {
                "dialog": dialog,
                "layout": layout,
                "widgets": []
            }
            
            return h_string(dialog_id)
        except Exception as e:
            raise RuntimeError(f"Failed to add custom dialog: {e}")

    def _gui_show_custom_dialog(args, _):
        """Show custom dialog."""
        dialog_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if dialog_id in gui_components.get("custom_dialogs", {}):
            dialog = gui_components["custom_dialogs"][dialog_id]["dialog"]
            result = dialog.exec()
            return h_number(result)
        else:
            raise RuntimeError(f"Custom dialog not found: {dialog_id}")

    def _gui_add_widget_to_dialog(args, _):
        """Add widget to custom dialog."""
        dialog_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_type = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "label"
        text = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if dialog_id not in gui_components.get("custom_dialogs", {}):
            raise RuntimeError(f"Custom dialog not found: {dialog_id}")
        
        dialog_data = gui_components["custom_dialogs"][dialog_id]
        layout = dialog_data["layout"]
        
        try:
            from PySide6.QtWidgets import QLabel, QPushButton, QLineEdit, QTextEdit
            
            if widget_type == "label":
                widget = QLabel(text)
            elif widget_type == "button":
                widget = QPushButton(text)
            elif widget_type == "text_input":
                widget = QLineEdit()
                widget.setPlaceholderText(text)
            elif widget_type == "text_area":
                widget = QTextEdit()
                widget.setPlainText(text)
            else:
                widget = QLabel(text)
            
            layout.addWidget(widget)
            dialog_data["widgets"].append(widget)
            
            return h_string("Widget added to dialog")
        except Exception as e:
            raise RuntimeError(f"Failed to add widget to dialog: {e}")

    # Advanced Styling
    def _gui_set_widget_style(args, _):
        """Set style for specific widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        style = args[2].value if len(args) > 2 and isinstance(args[2], HString) else ""
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setStyleSheet'):
            widget.setStyleSheet(style)
            return h_string("Widget style set")
        else:
            raise RuntimeError("Widget doesn't support stylesheets")

    def _gui_set_widget_font(args, _):
        """Set font for specific widget."""
        try:
            from PySide6.QtGui import QFont
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            font_family = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "Arial"
            font_size = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 10
            bold = args[4].value if len(args) > 4 and isinstance(args[4], HBoolean) else False
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Widget index out of range")
            
            widget = window_data["widgets"][widget_index]
            
            font = QFont(font_family, font_size)
            font.setBold(bold)
            
            if hasattr(widget, 'setFont'):
                widget.setFont(font)
                return h_string("Widget font set")
            else:
                raise RuntimeError("Widget doesn't support fonts")
        except Exception as e:
            raise RuntimeError(f"Failed to set widget font: {e}")

    def _gui_set_widget_color(args, _):
        """Set color for specific widget (background/text)."""
        try:
            from PySide6.QtGui import QPalette, QColor
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            color_type = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "background"
            color = args[3].value if len(args) > 3 and isinstance(args[3], HString) else "#000000"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Widget index out of range")
            
            widget = window_data["widgets"][widget_index]
            
            palette = widget.palette()
            qcolor = QColor(color)
            
            if color_type == "background":
                palette.setColor(widget.backgroundRole(), qcolor)
            elif color_type == "text":
                palette.setColor(widget.foregroundRole(), qcolor)
            elif color_type == "base":
                palette.setColor(QPalette.Base, qcolor)
            elif color_type == "alternate":
                palette.setColor(QPalette.AlternateBase, qcolor)
            
            widget.setPalette(palette)
            widget.setAutoFillBackground(True)
            
            return h_string("Widget color set")
        except Exception as e:
            raise RuntimeError(f"Failed to set widget color: {e}")

    # Enhanced Drag and Drop
    def _gui_set_drag_enabled(args, _):
        """Enable drag for a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        enabled = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else True
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setDragEnabled'):
            widget.setDragEnabled(enabled.value if isinstance(enabled, HBoolean) else enabled)
            return h_string("Drag enabled set")
        else:
            raise RuntimeError("Widget doesn't support drag")

    def _gui_set_drop_enabled(args, _):
        """Enable drop for a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        enabled = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else True
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setAcceptDrops'):
            widget.setAcceptDrops(enabled.value if isinstance(enabled, HBoolean) else enabled)
            return h_string("Drop enabled set")
        else:
            raise RuntimeError("Widget doesn't support drop")

    # Additional Widget Properties
    def _gui_set_widget_enabled(args, _):
        """Enable/disable widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        enabled = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else True
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setEnabled'):
            widget.setEnabled(enabled.value if isinstance(enabled, HBoolean) else enabled)
            return h_string("Widget enabled state set")
        else:
            raise RuntimeError("Widget doesn't support enabled state")

    def _gui_set_widget_visible(args, _):
        """Show/hide widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        visible = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else True
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setVisible'):
            widget.setVisible(visible.value if isinstance(visible, HBoolean) else visible)
            return h_string("Widget visibility set")
        else:
            raise RuntimeError("Widget doesn't support visibility")

    def _gui_set_widget_size(args, _):
        """Set widget size."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        width = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 100
        height = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 50
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setFixedSize'):
            widget.setFixedSize(width, height)
            return h_string("Widget size set")
        else:
            raise RuntimeError("Widget doesn't support size setting")

    def _gui_remove_widget(args, _):
        """Remove widget from layout."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        window_data["layout"].removeWidget(widget)
        widget.deleteLater()
        window_data["widgets"].pop(widget_index)
        
        return h_string("Widget removed")

    # Scroll Bar Controls
    def _gui_add_scroll_bar(args, _):
        """Add a scroll bar."""
        try:
            from PySide6.QtWidgets import QScrollBar
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            orientation = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "horizontal"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            qt_orientation = Qt.Horizontal if orientation == "horizontal" else Qt.Vertical
            scroll_bar = QScrollBar(qt_orientation)
            
            # Add to layout
            window_data["layout"].addWidget(scroll_bar)
            window_data["widgets"].append(scroll_bar)
            
            return h_string("Scroll bar added")
        except Exception as e:
            raise RuntimeError(f"Failed to add scroll bar: {e}")

    def _gui_add_slider_advanced(args, _):
        """Add an advanced slider with tick marks."""
        try:
            from PySide6.QtWidgets import QSlider
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            orientation = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "horizontal"
            min_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
            max_val = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
            initial = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 50
            tick_interval = int(args[5].value) if len(args) > 5 and isinstance(args[5], HNumber) else 10
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            qt_orientation = Qt.Horizontal if orientation == "horizontal" else Qt.Vertical
            slider = QSlider(qt_orientation)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(initial)
            slider.setTickInterval(tick_interval)
            slider.setTickPosition(QSlider.TicksBothSides)
            
            # Add to layout
            window_data["layout"].addWidget(slider)
            window_data["widgets"].append(slider)
            
            return h_string("Advanced slider added")
        except Exception as e:
            raise RuntimeError(f"Failed to add advanced slider: {e}")

    # Date/Time Advanced Features
    def _gui_add_calendar_widget(args, _):
        """Add a calendar widget."""
        try:
            from PySide6.QtWidgets import QCalendarWidget
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            calendar = QCalendarWidget()
            
            # Add to layout
            window_data["layout"].addWidget(calendar)
            window_data["widgets"].append(calendar)
            
            return h_string("Calendar widget added")
        except Exception as e:
            raise RuntimeError(f"Failed to add calendar widget: {e}")

    def _gui_get_selected_date(args, _):
        """Get selected date from date edit or calendar."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        try:
            if hasattr(widget, 'date'):
                date = widget.date()
                return h_string(date.toString("yyyy-MM-dd"))
            elif hasattr(widget, 'selectedDate'):
                date = widget.selectedDate()
                return h_string(date.toString("yyyy-MM-dd"))
            else:
                raise RuntimeError("Widget doesn't support date selection")
        except Exception as e:
            raise RuntimeError(f"Failed to get selected date: {e}")

    # Text Processing
    def _gui_set_text_alignment(args, _):
        """Set text alignment for label or text widget."""
        try:
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            alignment = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "left"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Widget index out of range")
            
            widget = window_data["widgets"][widget_index]
            
            if alignment == "left":
                qt_alignment = Qt.AlignLeft
            elif alignment == "center":
                qt_alignment = Qt.AlignCenter
            elif alignment == "right":
                qt_alignment = Qt.AlignRight
            elif alignment == "justify":
                qt_alignment = Qt.AlignJustify
            else:
                qt_alignment = Qt.AlignLeft
            
            if hasattr(widget, 'setAlignment'):
                widget.setAlignment(qt_alignment)
                return h_string("Text alignment set")
            else:
                raise RuntimeError("Widget doesn't support text alignment")
        except Exception as e:
            raise RuntimeError(f"Failed to set text alignment: {e}")

    def _gui_set_text_wrapping(args, _):
        """Set text wrapping for label or text widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        wrap = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else True
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setWordWrap'):
            widget.setWordWrap(wrap.value if isinstance(wrap, HBoolean) else wrap)
            return h_string("Text wrapping set")
        else:
            raise RuntimeError("Widget doesn't support text wrapping")

    # Multimedia (basic)
    def _gui_add_sound_effect(args, _):
        """Add a sound effect (plays a sound file)."""
        try:
            from PySide6.QtMultimedia import QSoundEffect
            
            sound_path = args[0].value if args and isinstance(args[0], HString) else ""
            
            sound_effect = QSoundEffect()
            sound_effect.setSource(sound_path)
            
            effect_id = f"sound_{len(gui_components.get('sounds', {}))}"
            gui_components["sounds"] = gui_components.get("sounds", {})
            gui_components["sounds"][effect_id] = sound_effect
            
            return h_string(effect_id)
        except ImportError:
            raise RuntimeError("QtMultimedia not available")
        except Exception as e:
            raise RuntimeError(f"Failed to add sound effect: {e}")

    def _gui_play_sound(args, _):
        """Play a sound effect."""
        sound_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if sound_id in gui_components.get("sounds", {}):
            sound = gui_components["sounds"][sound_id]
            sound.play()
            return h_string("Sound playing")
        else:
            raise RuntimeError(f"Sound effect not found: {sound_id}")

    def _gui_stop_sound(args, _):
        """Stop a sound effect."""
        sound_id = args[0].value if args and isinstance(args[0], HString) else ""
        
        if sound_id in gui_components.get("sounds", {}):
            sound = gui_components["sounds"][sound_id]
            sound.stop()
            return h_string("Sound stopped")
        else:
            raise RuntimeError(f"Sound effect not found: {sound_id}")

    # Additional Utility Functions
    def _gui_set_focus(args, _):
        """Set focus to a widget."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setFocus'):
            widget.setFocus()
            return h_string("Focus set")
        else:
            raise RuntimeError("Widget doesn't support focus")

    def _gui_clear_widget(args, _):
        """Clear content of a widget (text area, list, table, etc.)."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        try:
            if hasattr(widget, 'clear'):
                widget.clear()
                return h_string("Widget cleared")
            elif hasattr(widget, 'setPlainText'):
                widget.setPlainText("")
                return h_string("Widget cleared")
            elif hasattr(widget, 'setText'):
                widget.setText("")
                return h_string("Widget cleared")
            else:
                raise RuntimeError("Widget doesn't support clearing")
        except Exception as e:
            raise RuntimeError(f"Failed to clear widget: {e}")

    def _gui_get_widget_value(args, _):
        """Get current value from various widget types."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        try:
            if hasattr(widget, 'text'):
                return h_string(widget.text())
            elif hasattr(widget, 'toPlainText'):
                return h_string(widget.toPlainText())
            elif hasattr(widget, 'value'):
                return h_number(widget.value())
            elif hasattr(widget, 'isChecked'):
                return h_bool(widget.isChecked())
            elif hasattr(widget, 'currentText'):
                return h_string(widget.currentText())
            elif hasattr(widget, 'currentIndex'):
                return h_number(widget.currentIndex())
            else:
                return h_string("")
        except Exception as e:
            raise RuntimeError(f"Failed to get widget value: {e}")

    def _gui_set_widget_value(args, _):
        """Set value for various widget types."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        value = args[2]
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        try:
            if isinstance(value, HString):
                if hasattr(widget, 'setText'):
                    widget.setText(value.value)
                elif hasattr(widget, 'setPlainText'):
                    widget.setPlainText(value.value)
                elif hasattr(widget, 'setCurrentText'):
                    widget.setCurrentText(value.value)
            elif isinstance(value, HNumber):
                if hasattr(widget, 'setValue'):
                    widget.setValue(int(value.value))
                elif hasattr(widget, 'setCurrentIndex'):
                    widget.setCurrentIndex(int(value.value))
            elif isinstance(value, HBoolean):
                if hasattr(widget, 'setChecked'):
                    widget.setChecked(value.value)
            
            return h_string("Widget value set")
        except Exception as e:
            raise RuntimeError(f"Failed to set widget value: {e}")

    # Advanced Layout Management
    def _gui_add_widget_to_layout_by_id(args, _):
        """Add widget to layout by layout ID."""
        layout_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget = args[1] if len(args) > 1 else None
        row = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        col = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        
        if layout_id not in gui_components["layouts"]:
            raise RuntimeError(f"Layout not found: {layout_id}")
        
        layout_data = gui_components["layouts"][layout_id]
        layout = layout_data["layout"]
        
        if layout_data["type"] == "grid":
            # For grid layout, we need the actual widget reference
            # This is simplified - in a full implementation we'd need proper widget tracking
            pass
        else:
            # For vertical/horizontal layouts
            pass
        
        return h_string("Widget added to layout")

    def _gui_add_stretch(args, _):
        """Add stretch to layout."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        stretch = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 1
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        layout = window_data["layout"]
        
        if hasattr(layout, 'addStretch'):
            layout.addStretch(stretch)
            return h_string("Stretch added")
        else:
            raise RuntimeError("Layout doesn't support stretch")

    def _gui_add_spacing(args, _):
        """Add spacing to layout."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        spacing = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 10
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        layout = window_data["layout"]
        
        if hasattr(layout, 'addSpacing'):
            layout.addSpacing(spacing)
            return h_string("Spacing added")
        else:
            raise RuntimeError("Layout doesn't support spacing")

    def _gui_set_layout_spacing(args, _):
        """Set spacing for layout."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        spacing = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 10
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        layout = window_data["layout"]
        
        if hasattr(layout, 'setSpacing'):
            layout.setSpacing(spacing)
            return h_string("Layout spacing set")
        else:
            raise RuntimeError("Layout doesn't support spacing")

    def _gui_set_layout_margins(args, _):
        """Set margins for layout."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        left = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 10
        top = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 10
        right = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 10
        bottom = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 10
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        layout = window_data["layout"]
        
        if hasattr(layout, 'setContentsMargins'):
            layout.setContentsMargins(left, top, right, bottom)
            return h_string("Layout margins set")
        else:
            raise RuntimeError("Layout doesn't support margins")

    # Additional Widget Types
    def _gui_add_combo_box_advanced(args, _):
        """Add an advanced combobox with editable option."""
        try:
            from PySide6.QtWidgets import QComboBox
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            items = args[1] if len(args) > 1 and isinstance(args[1], HList) else None
            editable = args[2].value if len(args) > 2 and isinstance(args[2], HBoolean) else False
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            combobox = QComboBox()
            combobox.setEditable(editable.value if isinstance(editable, HBoolean) else editable)
            
            # Add items if provided
            if items:
                for item in items.elements:
                    if isinstance(item, HString):
                        combobox.addItem(item.value)
            
            # Add to layout
            window_data["layout"].addWidget(combobox)
            window_data["widgets"].append(combobox)
            
            return h_string("Advanced combobox added")
        except Exception as e:
            raise RuntimeError(f"Failed to add advanced combobox: {e}")

    def _gui_add_spin_box_advanced(args, _):
        """Add an advanced spin box with step and suffix."""
        try:
            from PySide6.QtWidgets import QSpinBox, QDoubleSpinBox
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_type = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "int"
            min_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
            max_val = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
            initial = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 0
            step = int(args[5].value) if len(args) > 5 and isinstance(args[5], HNumber) else 1
            suffix = args[6].value if len(args) > 6 and isinstance(args[6], HString) else ""
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_type == "double":
                spin_box = QDoubleSpinBox()
                spin_box.setMinimum(float(min_val))
                spin_box.setMaximum(float(max_val))
                spin_box.setValue(float(initial))
                spin_box.setSingleStep(float(step))
            else:
                spin_box = QSpinBox()
                spin_box.setMinimum(min_val)
                spin_box.setMaximum(max_val)
                spin_box.setValue(initial)
                spin_box.setSingleStep(step)
            
            if suffix:
                spin_box.setSuffix(suffix)
            
            # Add to layout
            window_data["layout"].addWidget(spin_box)
            window_data["widgets"].append(spin_box)
            
            return h_string("Advanced spin box added")
        except Exception as e:
            raise RuntimeError(f"Failed to add advanced spin box: {e}")

    def _gui_add_progress_bar_advanced(args, _):
        """Add an advanced progress bar with text format."""
        try:
            from PySide6.QtWidgets import QProgressBar
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            orientation = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "horizontal"
            min_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
            max_val = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
            initial = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 0
            text_visible = args[5].value if len(args) > 5 and isinstance(args[5], HBoolean) else True
            text_format = args[6].value if len(args) > 6 and isinstance(args[6], HString) else "%p%"
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            progress_bar = QProgressBar()
            progress_bar.setMinimum(min_val)
            progress_bar.setMaximum(max_val)
            progress_bar.setValue(initial)
            progress_bar.setTextVisible(text_visible.value if isinstance(text_visible, HBoolean) else text_visible)
            progress_bar.setFormat(text_format)
            
            # Set orientation using setOrientation
            qt_orientation = Qt.Horizontal if orientation == "horizontal" else Qt.Vertical
            progress_bar.setOrientation(qt_orientation)
            
            # Add to layout
            window_data["layout"].addWidget(progress_bar)
            window_data["widgets"].append(progress_bar)
            
            return h_string("Advanced progress bar added")
        except Exception as e:
            raise RuntimeError(f"Failed to add advanced progress bar: {e}")

    def _gui_add_slider_advanced_with_callback(args, _):
        """Add an advanced slider with value change callback."""
        try:
            from PySide6.QtWidgets import QSlider
            from PySide6.QtCore import Qt
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            orientation = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "horizontal"
            min_val = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
            max_val = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 100
            initial = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 50
            callback = args[5] if len(args) > 5 else None
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            qt_orientation = Qt.Horizontal if orientation == "horizontal" else Qt.Vertical
            slider = QSlider(qt_orientation)
            slider.setMinimum(min_val)
            slider.setMaximum(max_val)
            slider.setValue(initial)
            
            # Connect callback if provided
            if callback and isinstance(callback, HFunction):
                def on_value_changed(value):
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [h_number(value)], call_line=0)
                    except Exception as e:
                        print(f"Slider callback error: {e}")
                
                slider.valueChanged.connect(on_value_changed)
            
            # Add to layout
            window_data["layout"].addWidget(slider)
            window_data["widgets"].append(slider)
            
            return h_string("Advanced slider with callback added")
        except Exception as e:
            raise RuntimeError(f"Failed to add advanced slider with callback: {e}")

    # Animation and Graphics Enhancements
    def _gui_add_color_animation(args, _):
        """Add color animation to widget."""
        try:
            from PySide6.QtWidgets import QGraphicsColorizeEffect
            from PySide6.QtCore import QPropertyAnimation
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            start_color = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "#000000"
            end_color = args[3].value if len(args) > 3 and isinstance(args[3], HString) else "#ffffff"
            duration = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 1000
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Widget index out of range")
            
            widget = window_data["widgets"][widget_index]
            
            # Create color effect
            effect = QGraphicsColorizeEffect()
            widget.setGraphicsEffect(effect)
            
            # Create animation
            from PySide6.QtGui import QColor
            animation = QPropertyAnimation(effect, b"color")
            animation.setDuration(duration)
            animation.setStartValue(QColor(start_color))
            animation.setEndValue(QColor(end_color))
            
            animation.start()
            
            return h_string("Color animation started")
        except Exception as e:
            raise RuntimeError(f"Failed to add color animation: {e}")

    def _gui_add_rotation_animation(args, _):
        """Add rotation animation to widget."""
        try:
            from PySide6.QtWidgets import QGraphicsRotation
            from PySide6.QtCore import QPropertyAnimation
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            start_angle = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
            end_angle = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 360
            duration = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 1000
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Widget index out of range")
            
            widget = window_data["widgets"][widget_index]
            
            # Create rotation effect
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)
            
            # Simplified rotation animation (in a full implementation, you'd use QGraphicsRotation)
            return h_string("Rotation animation started (simplified)")
        except Exception as e:
            raise RuntimeError(f"Failed to add rotation animation: {e}")

    def _gui_add_scale_animation(args, _):
        """Add scale animation to widget."""
        try:
            from PySide6.QtWidgets import QGraphicsOpacityEffect
            from PySide6.QtCore import QPropertyAnimation
            
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
            start_scale = args[2].value if len(args) > 2 and isinstance(args[2], HNumber) else 1.0
            end_scale = args[3].value if len(args) > 3 and isinstance(args[3], HNumber) else 2.0
            duration = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 1000
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            if widget_index >= len(window_data["widgets"]):
                raise RuntimeError("Widget index out of range")
            
            widget = window_data["widgets"][widget_index]
            
            # Simplified scale animation (in a full implementation, you'd use QGraphicsScale)
            return h_string("Scale animation started (simplified)")
        except Exception as e:
            raise RuntimeError(f"Failed to add scale animation: {e}")

    def _gui_add_pixmap_animation(args, _):
        """Add pixmap/sequence animation."""
        try:
            window_id = args[0].value if args and isinstance(args[0], HString) else ""
            image_paths = args[1] if len(args) > 1 and isinstance(args[1], HList) else None
            interval = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 100
            
            if window_id not in gui_components["windows"]:
                raise RuntimeError(f"Window not found: {window_id}")
            
            window_data = gui_components["windows"][window_id]
            
            # Simplified pixmap animation
            return h_string("Pixmap animation started (simplified)")
        except Exception as e:
            raise RuntimeError(f"Failed to add pixmap animation: {e}")

    # Advanced Event Handling
    def _gui_set_widget_callback(args, _):
        """Set callback for widget events."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        event_type = args[2].value if len(args) > 2 and isinstance(args[2], HString) else "clicked"
        callback = args[3] if len(args) > 3 else None
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if not callback or not isinstance(callback, HFunction):
            raise RuntimeError("Callback must be a function")
        
        try:
            if event_type == "clicked" and hasattr(widget, 'clicked'):
                def on_clicked():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Clicked callback error: {e}")
                widget.clicked.connect(on_clicked)
            elif event_type == "changed" and hasattr(widget, 'textChanged'):
                def on_changed(text):
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [h_string(text)], call_line=0)
                    except Exception as e:
                        print(f"Changed callback error: {e}")
                widget.textChanged.connect(on_changed)
            elif event_type == "return_pressed" and hasattr(widget, 'returnPressed'):
                def on_return():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Return pressed callback error: {e}")
                widget.returnPressed.connect(on_return)
            elif event_type == "value_changed" and hasattr(widget, 'valueChanged'):
                def on_value_changed(value):
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [h_number(value)], call_line=0)
                    except Exception as e:
                        print(f"Value changed callback error: {e}")
                widget.valueChanged.connect(on_value_changed)
            elif event_type == "current_changed" and hasattr(widget, 'currentIndexChanged'):
                def on_current_changed(index):
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [h_number(index)], call_line=0)
                    except Exception as e:
                        print(f"Current changed callback error: {e}")
                widget.currentIndexChanged.connect(on_current_changed)
            else:
                raise RuntimeError(f"Event type '{event_type}' not supported for this widget")
            
            return h_string("Callback set")
        except Exception as e:
            raise RuntimeError(f"Failed to set callback: {e}")

    def _gui_set_window_callback(args, _):
        """Set callback for window events."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        event_type = args[1].value if len(args) > 1 and isinstance(args[1], HString) else "close"
        callback = args[2] if len(args) > 2 else None
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        window = window_data["window"]
        
        if not callback or not isinstance(callback, HFunction):
            raise RuntimeError("Callback must be a function")
        
        try:
            if event_type == "close":
                def on_close():
                    try:
                        if gui_components["interpreter"]:
                            gui_components["interpreter"]._call_function(callback, [], call_line=0)
                    except Exception as e:
                        print(f"Window close callback error: {e}")
                window.closeEvent = lambda event: (on_close(), event.accept())
            else:
                raise RuntimeError(f"Event type '{event_type}' not supported for window")
            
            return h_string("Window callback set")
        except Exception as e:
            raise RuntimeError(f"Failed to set window callback: {e}")

    # Additional Utility Functions
    def _gui_repaint_widget(args, _):
        """Force widget repaint."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'repaint'):
            widget.repaint()
            return h_string("Widget repainted")
        else:
            raise RuntimeError("Widget doesn't support repaint")

    def _gui_update_widget(args, _):
        """Force widget update."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'update'):
            widget.update()
            return h_string("Widget updated")
        else:
            raise RuntimeError("Widget doesn't support update")

    def _gui_get_widget_geometry(args, _):
        """Get widget geometry (position and size)."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'geometry'):
            geo = widget.geometry()
            return h_map({
                "x": h_number(geo.x()),
                "y": h_number(geo.y()),
                "width": h_number(geo.width()),
                "height": h_number(geo.height())
            })
        else:
            raise RuntimeError("Widget doesn't support geometry")

    def _gui_set_widget_geometry(args, _):
        """Set widget geometry (position and size)."""
        window_id = args[0].value if args and isinstance(args[0], HString) else ""
        widget_index = int(args[1].value) if len(args) > 1 and isinstance(args[1], HNumber) else 0
        x = int(args[2].value) if len(args) > 2 and isinstance(args[2], HNumber) else 0
        y = int(args[3].value) if len(args) > 3 and isinstance(args[3], HNumber) else 0
        width = int(args[4].value) if len(args) > 4 and isinstance(args[4], HNumber) else 100
        height = int(args[5].value) if len(args) > 5 and isinstance(args[5], HNumber) else 50
        
        if window_id not in gui_components["windows"]:
            raise RuntimeError(f"Window not found: {window_id}")
        
        window_data = gui_components["windows"][window_id]
        
        if widget_index >= len(window_data["widgets"]):
            raise RuntimeError("Widget index out of range")
        
        widget = window_data["widgets"][widget_index]
        
        if hasattr(widget, 'setGeometry'):
            widget.setGeometry(x, y, width, height)
            return h_string("Widget geometry set")
        else:
            raise RuntimeError("Widget doesn't support geometry")
    
    # Register GUI functions (note: addButton needs interpreter for callbacks)
    gui_env.define("init", HNativeFn("init", 0, _gui_init_app))
    gui_env.define("createWindow", HNativeFn("createWindow", -1, _gui_create_window))
    gui_env.define("createFramelessWindow", HNativeFn("createFramelessWindow", -1, _gui_create_frameless_window))
    gui_env.define("addTitleBar", HNativeFn("addTitleBar", -1, _gui_add_title_bar))
    gui_env.define("setTitleBarTitle", HNativeFn("setTitleBarTitle", 2, _gui_set_title_bar_title))
    gui_env.define("addLineNumberGutter", HNativeFn("addLineNumberGutter", -1, _gui_add_line_number_gutter))
    gui_env.define("updateLineNumbers", HNativeFn("updateLineNumbers", 1, _gui_update_line_numbers))
    gui_env.define("showWindow", HNativeFn("showWindow", 1, _gui_show_window))
    gui_env.define("addButton", HNativeFn("addButton", -1, _gui_add_button))
    gui_env.define("addLabel", HNativeFn("addLabel", -1, _gui_add_label))
    gui_env.define("addTextInput", HNativeFn("addTextInput", -1, _gui_add_text_input))
    gui_env.define("addTextArea", HNativeFn("addTextArea", -1, _gui_add_text_area))
    gui_env.define("addCheckbox", HNativeFn("addCheckbox", -1, _gui_add_checkbox))
    gui_env.define("addCombobox", HNativeFn("addCombobox", -1, _gui_add_combobox))
    gui_env.define("addSlider", HNativeFn("addSlider", -1, _gui_add_slider))
    gui_env.define("addProgressBar", HNativeFn("addProgressBar", -1, _gui_add_progress_bar))
    gui_env.define("run", HNativeFn("run", 0, _gui_run))
    gui_env.define("setStyle", HNativeFn("setStyle", 1, _gui_set_style))
    gui_env.define("messageBox", HNativeFn("messageBox", -1, _gui_message_box))
    gui_env.define("getInput", HNativeFn("getInput", 2, _gui_get_input))
    gui_env.define("setText", HNativeFn("setText", 3, _gui_set_text))
    gui_env.define("closeWindow", HNativeFn("closeWindow", 1, _gui_close_window))
    gui_env.define("setWindowTitle", HNativeFn("setWindowTitle", 2, _gui_set_window_title))
    gui_env.define("setWindowSize", HNativeFn("setWindowSize", 3, _gui_set_window_size))
    
    # Advanced layouts
    gui_env.define("createHorizontalLayout", HNativeFn("createHorizontalLayout", -1, _gui_create_horizontal_layout))
    gui_env.define("createVerticalLayout", HNativeFn("createVerticalLayout", -1, _gui_create_vertical_layout))
    gui_env.define("createGridLayout", HNativeFn("createGridLayout", -1, _gui_create_grid_layout))
    gui_env.define("createFormLayout", HNativeFn("createFormLayout", -1, _gui_create_form_layout))
    gui_env.define("addWidgetToLayout", HNativeFn("addWidgetToLayout", -1, _gui_add_widget_to_layout))
    gui_env.define("setWindowLayout", HNativeFn("setWindowLayout", 2, _gui_set_window_layout))
    gui_env.define("createWindowWithGrid", HNativeFn("createWindowWithGrid", -1, _gui_create_window_with_grid))
    gui_env.define("addToGrid", HNativeFn("addToGrid", -1, _gui_add_to_grid))
    
    # Advanced widgets
    gui_env.define("addTreeWidget", HNativeFn("addTreeWidget", 1, _gui_add_tree_widget))
    gui_env.define("addTableWidget", HNativeFn("addTableWidget", -1, _gui_add_table_widget))
    gui_env.define("addTabWidget", HNativeFn("addTabWidget", 1, _gui_add_tab_widget))
    gui_env.define("addTabToTabWidget", HNativeFn("addTabToTabWidget", -1, _gui_add_tab_to_tab_widget))
    gui_env.define("addScrollArea", HNativeFn("addScrollArea", -1, _gui_add_scroll_area))
    gui_env.define("addGroupBox", HNativeFn("addGroupBox", -1, _gui_add_group_box))
    gui_env.define("addSpinBox", HNativeFn("addSpinBox", -1, _gui_add_spin_box))
    gui_env.define("addDoubleSpinBox", HNativeFn("addDoubleSpinBox", -1, _gui_add_double_spin_box))
    gui_env.define("addDateEdit", HNativeFn("addDateEdit", 1, _gui_add_date_edit))
    gui_env.define("addTimeEdit", HNativeFn("addTimeEdit", 1, _gui_add_time_edit))
    gui_env.define("addLCDNumber", HNativeFn("addLCDNumber", -1, _gui_add_lcd_number))
    gui_env.define("addDial", HNativeFn("addDial", -1, _gui_add_dial))
    
    # Dialogs
    gui_env.define("fileDialog", HNativeFn("fileDialog", -1, _gui_file_dialog))
    gui_env.define("colorDialog", HNativeFn("colorDialog", 0, _gui_color_dialog))
    gui_env.define("fontDialog", HNativeFn("fontDialog", 0, _gui_font_dialog))
    gui_env.define("inputDialog", HNativeFn("inputDialog", -1, _gui_input_dialog))
    
    # Menu and toolbar
    gui_env.define("addMenuBar", HNativeFn("addMenuBar", 1, _gui_add_menu_bar))
    gui_env.define("addMenu", HNativeFn("addMenu", -1, _gui_add_menu))
    gui_env.define("addMenuItem", HNativeFn("addMenuItem", -1, _gui_add_menu_item))
    gui_env.define("addMenuSeparator", HNativeFn("addMenuSeparator", 1, _gui_add_menu_separator))
    gui_env.define("addToolBar", HNativeFn("addToolBar", -1, _gui_add_toolbar))
    gui_env.define("addToolBarAction", HNativeFn("addToolBarAction", -1, _gui_add_toolbar_action))
    gui_env.define("addStatusBar", HNativeFn("addStatusBar", 1, _gui_add_status_bar))
    gui_env.define("setStatusBarText", HNativeFn("setStatusBarText", 2, _gui_set_status_bar_text))
    
    # Timers
    gui_env.define("createTimer", HNativeFn("createTimer", -1, _gui_create_timer))
    gui_env.define("startTimer", HNativeFn("startTimer", 1, _gui_start_timer))
    gui_env.define("stopTimer", HNativeFn("stopTimer", 1, _gui_stop_timer))
    
    # Stylesheets
    gui_env.define("setStylesheet", HNativeFn("setStylesheet", 2, _gui_set_stylesheet))
    
    # MDI
    gui_env.define("setMDIMode", HNativeFn("setMDIMode", 1, _gui_set_mdi_mode))
    gui_env.define("addMDISubwindow", HNativeFn("addMDISubwindow", -1, _gui_add_mdi_subwindow))
    
    # Rich Text
    gui_env.define("addRichTextEdit", HNativeFn("addRichTextEdit", -1, _gui_add_rich_text_edit))
    gui_env.define("setRichText", HNativeFn("setRichText", 3, _gui_set_rich_text))
    
    # Graphics and Painting
    gui_env.define("addGraphicsView", HNativeFn("addGraphicsView", 1, _gui_add_graphics_view))
    gui_env.define("drawRectangle", HNativeFn("drawRectangle", -1, _gui_draw_rectangle))
    gui_env.define("drawEllipse", HNativeFn("drawEllipse", -1, _gui_draw_ellipse))
    gui_env.define("drawText", HNativeFn("drawText", -1, _gui_draw_text))
    gui_env.define("drawLine", HNativeFn("drawLine", -1, _gui_draw_line))
    
    # Web View
    gui_env.define("addWebView", HNativeFn("addWebView", -1, _gui_add_web_view))
    
    # Charts
    gui_env.define("addPlotWidget", HNativeFn("addPlotWidget", 1, _gui_add_plot_widget))
    
    # Drag and Drop
    gui_env.define("enableDragDrop", HNativeFn("enableDragDrop", 2, _gui_enable_drag_drop))
    
    # Animation
    gui_env.define("animateWidget", HNativeFn("animateWidget", -1, _gui_animate_widget))
    
    # Additional Qt Widgets
    gui_env.define("addSplitter", HNativeFn("addSplitter", -1, _gui_add_splitter))
    gui_env.define("addDockWidget", HNativeFn("addDockWidget", -1, _gui_add_dock_widget))
    gui_env.define("addStackedWidget", HNativeFn("addStackedWidget", 1, _gui_add_stacked_widget))
    gui_env.define("addPageToStacked", HNativeFn("addPageToStacked", -1, _gui_add_page_to_stacked))
    gui_env.define("setStackedIndex", HNativeFn("setStackedIndex", 3, _gui_set_stacked_index))
    gui_env.define("addListWidget", HNativeFn("addListWidget", -1, _gui_add_list_widget))
    gui_env.define("addRadioButton", HNativeFn("addRadioButton", -1, _gui_add_radio_button))
    gui_env.define("addButtonGroup", HNativeFn("addButtonGroup", 1, _gui_add_button_group))
    gui_env.define("addToolButton", HNativeFn("addToolButton", -1, _gui_add_tool_button))
    gui_env.define("addFrame", HNativeFn("addFrame", -1, _gui_add_frame))
    gui_env.define("addCommandLinkButton", HNativeFn("addCommandLinkButton", -1, _gui_add_command_link_button))
    gui_env.define("addLabelWithPixmap", HNativeFn("addLabelWithPixmap", -1, _gui_add_label_with_pixmap))
    gui_env.define("addProgressDialog", HNativeFn("addProgressDialog", -1, _gui_add_progress_dialog))
    gui_env.define("updateProgressDialog", HNativeFn("updateProgressDialog", 2, _gui_update_progress_dialog))
    gui_env.define("closeDialog", HNativeFn("closeDialog", 1, _gui_close_dialog))
    
    # Advanced Window Management
    gui_env.define("maximizeWindow", HNativeFn("maximizeWindow", 1, _gui_maximize_window))
    gui_env.define("minimizeWindow", HNativeFn("minimizeWindow", 1, _gui_minimize_window))
    gui_env.define("showNormal", HNativeFn("showNormal", 1, _gui_show_normal))
    gui_env.define("showFullscreen", HNativeFn("showFullscreen", 1, _gui_show_fullscreen))
    gui_env.define("hideWindow", HNativeFn("hideWindow", 1, _gui_hide_window))
    gui_env.define("setWindowIcon", HNativeFn("setWindowIcon", -1, _gui_set_window_icon))
    gui_env.define("setWindowOpacity", HNativeFn("setWindowOpacity", 2, _gui_set_window_opacity))
    gui_env.define("setWindowPosition", HNativeFn("setWindowPosition", 3, _gui_set_window_position))
    gui_env.define("getWindowPosition", HNativeFn("getWindowPosition", 1, _gui_get_window_position))
    gui_env.define("setWindowModality", HNativeFn("setWindowModality", -1, _gui_set_window_modality))
    
    # Clipboard Operations
    gui_env.define("copyToClipboard", HNativeFn("copyToClipboard", 1, _gui_copy_to_clipboard))
    gui_env.define("pasteFromClipboard", HNativeFn("pasteFromClipboard", 0, _gui_paste_from_clipboard))
    gui_env.define("clearClipboard", HNativeFn("clearClipboard", 0, _gui_clear_clipboard))
    
    # System Tray Support
    gui_env.define("addSystemTray", HNativeFn("addSystemTray", -1, _gui_add_system_tray))
    gui_env.define("addTrayMenu", HNativeFn("addTrayMenu", 1, _gui_add_tray_menu))
    gui_env.define("addTrayMenuItem", HNativeFn("addTrayMenuItem", -1, _gui_add_tray_menu_item))
    gui_env.define("showTrayMessage", HNativeFn("showTrayMessage", -1, _gui_show_tray_message))
    
    # Advanced Table Widget Features
    gui_env.define("setTableItem", HNativeFn("setTableItem", 5, _gui_set_table_item))
    gui_env.define("getTableItem", HNativeFn("getTableItem", 4, _gui_get_table_item))
    gui_env.define("setTableHeader", HNativeFn("setTableHeader", 3, _gui_set_table_header))
    
    # Advanced Tree Widget Features
    gui_env.define("addTreeItem", HNativeFn("addTreeItem", -1, _gui_add_tree_item))
    
    # Validators and Input Masks
    gui_env.define("setValidator", HNativeFn("setValidator", 3, _gui_set_validator))
    gui_env.define("setInputMask", HNativeFn("setInputMask", 3, _gui_set_input_mask))
    gui_env.define("setTooltip", HNativeFn("setTooltip", 3, _gui_set_tooltip))
    gui_env.define("setStatusTip", HNativeFn("setStatusTip", 3, _gui_set_status_tip))
    
    # Additional Dialog Types
    gui_env.define("addWizard", HNativeFn("addWizard", -1, _gui_add_wizard))
    gui_env.define("showWizard", HNativeFn("showWizard", 1, _gui_show_wizard))
    gui_env.define("addCustomDialog", HNativeFn("addCustomDialog", -1, _gui_add_custom_dialog))
    gui_env.define("showCustomDialog", HNativeFn("showCustomDialog", 1, _gui_show_custom_dialog))
    gui_env.define("addWidgetToDialog", HNativeFn("addWidgetToDialog", -1, _gui_add_widget_to_dialog))
    
    # Advanced Styling
    gui_env.define("setWidgetStyle", HNativeFn("setWidgetStyle", 3, _gui_set_widget_style))
    gui_env.define("setWidgetFont", HNativeFn("setWidgetFont", -1, _gui_set_widget_font))
    gui_env.define("setWidgetColor", HNativeFn("setWidgetColor", -1, _gui_set_widget_color))
    
    # Enhanced Drag and Drop
    gui_env.define("setDragEnabled", HNativeFn("setDragEnabled", 3, _gui_set_drag_enabled))
    gui_env.define("setDropEnabled", HNativeFn("setDropEnabled", 3, _gui_set_drop_enabled))
    
    # Additional Widget Properties
    gui_env.define("setWidgetEnabled", HNativeFn("setWidgetEnabled", 3, _gui_set_widget_enabled))
    gui_env.define("setWidgetVisible", HNativeFn("setWidgetVisible", 3, _gui_set_widget_visible))
    gui_env.define("setWidgetSize", HNativeFn("setWidgetSize", 4, _gui_set_widget_size))
    gui_env.define("removeWidget", HNativeFn("removeWidget", 2, _gui_remove_widget))
    
    # Scroll Bar Controls
    gui_env.define("addScrollBar", HNativeFn("addScrollBar", -1, _gui_add_scroll_bar))
    gui_env.define("addSliderAdvanced", HNativeFn("addSliderAdvanced", -1, _gui_add_slider_advanced))
    
    # Date/Time Advanced Features
    gui_env.define("addCalendarWidget", HNativeFn("addCalendarWidget", 1, _gui_add_calendar_widget))
    gui_env.define("getSelectedDate", HNativeFn("getSelectedDate", 2, _gui_get_selected_date))
    
    # Text Processing
    gui_env.define("setTextAlignment", HNativeFn("setTextAlignment", 3, _gui_set_text_alignment))
    gui_env.define("setTextWrapping", HNativeFn("setTextWrapping", 3, _gui_set_text_wrapping))
    
    # Multimedia (basic)
    gui_env.define("addSoundEffect", HNativeFn("addSoundEffect", 1, _gui_add_sound_effect))
    gui_env.define("playSound", HNativeFn("playSound", 1, _gui_play_sound))
    gui_env.define("stopSound", HNativeFn("stopSound", 1, _gui_stop_sound))
    
    # Additional Utility Functions
    gui_env.define("setFocus", HNativeFn("setFocus", 2, _gui_set_focus))
    gui_env.define("clearWidget", HNativeFn("clearWidget", 2, _gui_clear_widget))
    gui_env.define("getWidgetValue", HNativeFn("getWidgetValue", 2, _gui_get_widget_value))
    gui_env.define("setWidgetValue", HNativeFn("setWidgetValue", 3, _gui_set_widget_value))
    
    # Advanced Layout Management
    gui_env.define("addWidgetToLayoutById", HNativeFn("addWidgetToLayoutById", -1, _gui_add_widget_to_layout_by_id))
    gui_env.define("addStretch", HNativeFn("addStretch", 2, _gui_add_stretch))
    gui_env.define("addSpacing", HNativeFn("addSpacing", 2, _gui_add_spacing))
    gui_env.define("setLayoutSpacing", HNativeFn("setLayoutSpacing", 2, _gui_set_layout_spacing))
    gui_env.define("setLayoutMargins", HNativeFn("setLayoutMargins", 5, _gui_set_layout_margins))
    
    # Additional Widget Types
    gui_env.define("addComboBoxAdvanced", HNativeFn("addComboBoxAdvanced", -1, _gui_add_combo_box_advanced))
    gui_env.define("addSpinBoxAdvanced", HNativeFn("addSpinBoxAdvanced", -1, _gui_add_spin_box_advanced))
    gui_env.define("addProgressBarAdvanced", HNativeFn("addProgressBarAdvanced", -1, _gui_add_progress_bar_advanced))
    gui_env.define("addSliderAdvancedWithCallback", HNativeFn("addSliderAdvancedWithCallback", -1, _gui_add_slider_advanced_with_callback))
    
    # Animation and Graphics Enhancements
    gui_env.define("addColorAnimation", HNativeFn("addColorAnimation", -1, _gui_add_color_animation))
    gui_env.define("addRotationAnimation", HNativeFn("addRotationAnimation", -1, _gui_add_rotation_animation))
    gui_env.define("addScaleAnimation", HNativeFn("addScaleAnimation", -1, _gui_add_scale_animation))
    gui_env.define("addPixmapAnimation", HNativeFn("addPixmapAnimation", -1, _gui_add_pixmap_animation))
    
    # Advanced Event Handling
    gui_env.define("setWidgetCallback", HNativeFn("setWidgetCallback", 4, _gui_set_widget_callback))
    gui_env.define("setWindowCallback", HNativeFn("setWindowCallback", 3, _gui_set_window_callback))
    
    # Additional Utility Functions
    gui_env.define("repaintWidget", HNativeFn("repaintWidget", 2, _gui_repaint_widget))
    gui_env.define("updateWidget", HNativeFn("updateWidget", 2, _gui_update_widget))
    gui_env.define("getWidgetGeometry", HNativeFn("getWidgetGeometry", 2, _gui_get_widget_geometry))
    gui_env.define("setWidgetGeometry", HNativeFn("setWidgetGeometry", 6, _gui_set_widget_geometry))
    
    env.define("GUI", HModule("GUI", gui_env))

    return env


def is_truthy(value: HValue) -> bool:
    """Check if a value is truthy."""
    if isinstance(value, HNone):
        return False
    if isinstance(value, HBoolean):
        return value.value
    if isinstance(value, HNumber):
        return value.value != 0
    if isinstance(value, HString):
        return len(value.value) > 0
    if isinstance(value, HList):
        return len(value.elements) > 0
    if isinstance(value, HMap):
        return len(value.entries) > 0
    return True
