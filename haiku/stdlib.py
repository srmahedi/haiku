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
