import importlib.util
import os
import re
import shutil
import sys

# labelImg की जगह ढूँढो (import किए बिना)
spec = importlib.util.find_spec("labelImg")
if spec is None or spec.origin is None:
    # कुछ versions में सिर्फ़ libs फ़ोल्डर मिलता है
    spec_libs = importlib.util.find_spec("libs")
    if spec_libs is None:
        sys.exit("labelImg नहीं मिला। पहले pip install labelImg चलाओ।")
    base = os.path.dirname(os.path.dirname(spec_libs.origin or spec_libs.submodule_search_locations[0]))
else:
    base = os.path.dirname(spec.origin)

candidates = []
for root, _, files in os.walk(base):
    for f in files:
        if f in ("canvas.py", "labelImg.py"):
            candidates.append(os.path.join(root, f))

# सिर्फ़ labelImg वाली फ़ाइलें (libs/canvas.py और labelImg.py)
candidates = [p for p in candidates
              if p.endswith("canvas.py") or p.endswith("labelImg.py")]

def wrap_int(arg):
    a = arg.strip()
    return a if a.startswith("int(") else f"int({a})"

def patch_line(line):
    # drawLine(...) और drawRect(...) के सारे arguments को int बनाओ
    m = re.match(r"^(\s*.*?\.(?:drawLine|drawRect)\()(.*)(\)\s*)$", line.rstrip("\n"))
    if m:
        args = [wrap_int(a) for a in m.group(2).split(",")]
        return m.group(1) + ", ".join(args) + m.group(3) + "\n"
    # scrollbar के setValue(...) को int बनाओ
    m = re.match(r"^(\s*\w*bar\w*\.setValue\()(.*)(\)\s*)$", line.rstrip("\n"))
    if m:
        return m.group(1) + wrap_int(m.group(2)) + m.group(3) + "\n"
    return line

changed_files = 0
for path in candidates:
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    new_lines = [patch_line(l) for l in lines]
    if new_lines != lines:
        shutil.copy(path, path + ".bak")  # backup
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print("ठीक किया:", path)
        changed_files += 1

if changed_files == 0:
    print("कोई बदलाव ज़रूरी नहीं मिला (या फ़ाइलें पहले से ठीक हैं)।")
else:
    print("हो गया। अब labelImg चलाओ।")