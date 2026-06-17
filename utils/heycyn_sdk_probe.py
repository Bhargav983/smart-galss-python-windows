import importlib
import inspect
import pkgutil
import sys
from importlib import metadata


CANDIDATE_MODULES = [
    "heycyan_glasses_sdk",
    "heycyan",
    "heycyan_sdk",
    "glasses_sdk",
]

METHOD_KEYWORDS = [
    "notify",
    "notification",
    "command",
    "battery",
    "photo",
    "capture",
    "transfer",
    "wifi",
    "media",
]

NOTIFICATION_KEYWORDS = [
    "notify",
    "notification",
]


def get_python_executable():
    return sys.executable


def get_distribution_info(package_name="heycyan-glasses-sdk"):
    try:
        dist = metadata.distribution(package_name)
        return {
            "name": dist.metadata.get("Name", package_name),
            "version": dist.version,
            "location": str(dist.locate_file("")),
            "files": [str(file) for file in (dist.files or [])],
        }
    except metadata.PackageNotFoundError:
        return None


def find_matching_module_names():
    matches = []

    for module in pkgutil.iter_modules():
        name = module.name
        lower_name = name.lower()

        if any(keyword in lower_name for keyword in ["hey", "cyan", "glass"]):
            matches.append(name)

    return sorted(set(matches))


def import_candidate_modules():
    imported = []
    failed = []

    for module_name in CANDIDATE_MODULES:
        try:
            module = importlib.import_module(module_name)
            imported.append(module)
        except Exception as exc:
            failed.append((module_name, exc))

    return imported, failed


def list_public_callables(obj):
    callables = []

    for name, member in inspect.getmembers(obj):
        if name.startswith("_"):
            continue

        if inspect.isclass(member) or inspect.isfunction(member) or inspect.ismethod(member):
            callables.append((name, member))

    return callables


def find_keyword_methods(obj, keywords=None):
    if keywords is None:
        keywords = METHOD_KEYWORDS

    matches = []

    for name, member in list_public_callables(obj):
        lower_name = name.lower()

        if any(keyword in lower_name for keyword in keywords):
            matches.append((name, member))

    return matches


def describe_callable(name, member):
    try:
        signature = str(inspect.signature(member))
    except Exception:
        signature = "(signature unavailable)"

    if inspect.isclass(member):
        kind = "class"
    elif inspect.isfunction(member):
        kind = "function"
    elif inspect.ismethod(member):
        kind = "method"
    else:
        kind = type(member).__name__

    return {
        "name": name,
        "kind": kind,
        "signature": signature,
    }


def required_positional_count(callable_obj):
    try:
        signature = inspect.signature(callable_obj)
    except Exception:
        return None

    count = 0

    for param in signature.parameters.values():
        if param.name == "self":
            continue

        if (
            param.default is inspect.Signature.empty
            and param.kind
            in (
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            )
        ):
            count += 1

    return count


def describe_class_keyword_methods(class_obj):
    methods = []

    for name, member in inspect.getmembers(class_obj):
        if name.startswith("_"):
            continue

        if not (inspect.isfunction(member) or inspect.ismethod(member)):
            continue

        lower_name = name.lower()

        if any(keyword in lower_name for keyword in METHOD_KEYWORDS):
            methods.append(describe_callable(name, member))

    return methods


def discover_sdk_surface():
    imported, failed = import_candidate_modules()
    modules = []

    for module in imported:
        public_callables = [
            describe_callable(name, member)
            for name, member in list_public_callables(module)
        ]
        keyword_methods = [
            describe_callable(name, member)
            for name, member in find_keyword_methods(module)
        ]
        class_keyword_methods = []

        for name, member in list_public_callables(module):
            if inspect.isclass(member):
                class_keyword_methods.append(
                    {
                        "class": name,
                        "methods": describe_class_keyword_methods(member),
                    }
                )

        modules.append(
            {
                "name": module.__name__,
                "file": getattr(module, "__file__", None),
                "public_callables": public_callables,
                "keyword_methods": keyword_methods,
                "class_keyword_methods": class_keyword_methods,
            }
        )

    return {
        "python_executable": get_python_executable(),
        "distribution": get_distribution_info(),
        "imported_modules": modules,
        "failed_imports": [
            {"name": name, "error": repr(error)}
            for name, error in failed
        ],
        "matching_module_names": find_matching_module_names(),
    }


def find_notification_function():
    imported, _failed = import_candidate_modules()

    for module in imported:
        for name, member in find_keyword_methods(module, NOTIFICATION_KEYWORDS):
            if inspect.isfunction(member) or inspect.ismethod(member):
                return module, name, member

        for class_name, class_obj in list_public_callables(module):
            if not inspect.isclass(class_obj):
                continue

            init_required_count = required_positional_count(class_obj)

            if init_required_count not in (0, None):
                continue

            try:
                instance = class_obj()
            except Exception:
                continue

            for method_name, method in find_keyword_methods(instance, NOTIFICATION_KEYWORDS):
                if inspect.ismethod(method) or inspect.isfunction(method):
                    return module, f"{class_name}.{method_name}", method

    return None, None, None
