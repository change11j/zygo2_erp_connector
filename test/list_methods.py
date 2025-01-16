import zygo.mx as mx
import zygo.ui as ui
import inspect

def list_available_methods(module):
    print("Available methods in {0}:".format(module.__name__))
    methods = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            methods.append(name)
    
    # Sort methods alphabetically for better readability
    methods.sort()
    for name in methods:
        print("- {0}".format(name))

try:
    print("\nChecking mx module:")
    list_available_methods(mx)
    
    print("\nChecking ui module:")
    list_available_methods(ui)
    
except Exception as e:
    print('Error: {0}'.format(str(e)))