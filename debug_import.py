
import importlib.machinery
import importlib.util
import os
import sys

path = "/Users/cryptojoker710/Desktop/Aether Live Agent/aether-cortex/target/release/aether_cortex.so"
print(f"Attempting to load: {path}")
print(f"File exists: {os.path.exists(path)}")

try:
    loader = importlib.machinery.ExtensionFileLoader("aether_cortex", path)
    spec = importlib.util.spec_from_loader("aether_cortex", loader)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print("SUCCESS")
    print(f"Module members: {dir(module)}")
except Exception as e:
    print(f"FAILURE: {e}")
    import traceback
    traceback.print_exc()
