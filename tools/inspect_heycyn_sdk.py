from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from utils.heycyn_sdk_probe import discover_sdk_surface


def print_section(title):
    print("\n" + title)
    print("-" * len(title))


def main():
    surface = discover_sdk_surface()

    print_section("Python")
    print("Executable:", surface["python_executable"])

    print_section("Installed Package")
    distribution = surface["distribution"]

    if not distribution:
        print("heycyan-glasses-sdk: not installed")
    else:
        print("Name:", distribution["name"])
        print("Version:", distribution["version"])
        print("Location:", distribution["location"])
        print("Files:")

        for file_name in distribution["files"]:
            print(" ", file_name)

    print_section("Candidate Imports")

    for module in surface["imported_modules"]:
        print("IMPORT OK:", module["name"])
        print("File:", module["file"])

        print("Available classes/functions:")
        if module["public_callables"]:
            for item in module["public_callables"]:
                print(f"  {item['kind']} {item['name']}{item['signature']}")
        else:
            print("  None")

        print("Keyword methods:")
        if module["keyword_methods"]:
            for item in module["keyword_methods"]:
                print(f"  {item['kind']} {item['name']}{item['signature']}")
        else:
            print("  None")

        print("Class keyword methods:")
        printed_class_method = False

        for class_item in module["class_keyword_methods"]:
            methods = class_item["methods"]

            if not methods:
                continue

            printed_class_method = True
            print(f"  {class_item['class']}:")

            for item in methods:
                print(f"    {item['kind']} {item['name']}{item['signature']}")

        if not printed_class_method:
            print("  None")

    for failed in surface["failed_imports"]:
        print("IMPORT FAIL:", failed["name"], failed["error"])

    print_section("Installed Modules Matching hey/cyan/glass")
    if surface["matching_module_names"]:
        for module_name in surface["matching_module_names"]:
            print(module_name)
    else:
        print("None")


if __name__ == "__main__":
    main()
