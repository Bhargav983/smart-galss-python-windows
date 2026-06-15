import importlib
import pkgutil

print("Searching HeyCyan SDK modules...\n")

matches = [
    m.name for m in pkgutil.iter_modules()
    if "hey" in m.name.lower()
    or "cyan" in m.name.lower()
    or "glass" in m.name.lower()
]

print("Matched modules:")
print(matches)

print("\nTrying to import matched modules...\n")

for module_name in matches:
    try:
        module = importlib.import_module(module_name)
        print(f"\nSUCCESS: {module_name}")
        print("Module file:", getattr(module, "__file__", "No file found"))

        print("\nAvailable SDK functions/classes:")
        for item in dir(module):
            if not item.startswith("_"):
                print(" -", item)

    except Exception as e:
        print(f"FAILED: {module_name} -> {e}")