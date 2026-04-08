import sys
print(python:, sys.executable)
print(cwd:, __import__(os).getcwd())
print(sys.path before:, sys.path[:3])
sys.path.insert(0, src)
print(sys.path after:, sys.path[:3])
try:
    import rmer_ai_coffee
    print(import rmer_ai_coffee OK, file=, getattr(rmer_ai_coffee, "__file__", None))
except Exception as e:
    print(import rmer_ai_coffee FAILED:, e)
import pytest
print(pytest version, pytest.__version__)
ret = pytest.main([-q, tests])
print(pytest.main returned, ret)
sys.exit(ret)
