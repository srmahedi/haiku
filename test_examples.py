import os
import subprocess
import sys

def main():
    examples_dir = "examples"
    main_py = "main.py"
    
    if not os.path.exists(examples_dir):
        print(f"Examples directory not found: {examples_dir}")
        sys.exit(1)
        
    files = [f for f in os.listdir(examples_dir) if f.endswith(".hku")]
    files.sort()
    
    passed = []
    failed = []
    
    print(f"Found {len(files)} example files.")
    print("=" * 60)
    
    for filename in files:
        filepath = os.path.join(examples_dir, filename)
        print(f"Running {filename}...", end=" ", flush=True)
        
        # Some examples might be interactive or block, but let's run them first
        # We can set stdin to devnull to avoid hanging on input if any
        try:
            res = subprocess.run(
                [sys.executable, main_py, filepath],
                capture_output=True,
                text=True,
                timeout=5,
                stdin=subprocess.DEVNULL
            )
            if res.returncode == 0:
                print("PASS")
                passed.append(filename)
            else:
                print("FAIL")
                failed.append((filename, res.returncode, res.stdout, res.stderr))
        except subprocess.TimeoutExpired:
            print("TIMEOUT")
            failed.append((filename, "Timeout", "", "Process timed out after 5 seconds"))
        except Exception as e:
            print("ERROR")
            failed.append((filename, "Error", "", str(e)))
            
    print("=" * 60)
    print(f"Results: {len(passed)} passed, {len(failed)} failed.")
    print("=" * 60)
    
    if failed:
        print("\nFailed Details:")
        for name, code, stdout, stderr in failed:
            print(f"\n--- {name} (Exit code/Status: {code}) ---")
            if stdout:
                print(f"Stdout:\n{stdout}")
            if stderr:
                print(f"Stderr:\n{stderr}")
        sys.exit(1)
    else:
        print("All examples passed successfully!")

if __name__ == "__main__":
    main()
