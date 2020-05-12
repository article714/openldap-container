import importlib
import logging
import pkgutil
import sys
import unittest

# ---------------------------------
# test cases

# ---------------------------------
# Go main
if __name__ == "__main__":
    # init logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    # discover tests
    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    suite = unittest.TestSuite()
    for module in pkgutil.iter_modules([__package__]):
        if module.name.startswith("test"):
            mod = importlib.import_module(".{}".format(module.name), __package__)
            if "_addTestsToSuite" in dir(mod):
                mod._addTestsToSuite(suite)
            else:
                suite.addTest(loader.loadTestsFromModule(mod))
    # run tests
    results = runner.run(suite)
    if results.failures or results.errors:
        sys.exit(1)
    else:
        sys.exit(0)
