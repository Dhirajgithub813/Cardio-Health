# test_imports.py
try:
    import flask
    import flask_cors
    import sklearn
    import pandas
    import numpy
    import scipy
    import dotenv
    import requests
    
    print("✅ All packages imported successfully!")
    print(f"Flask version: {flask.__version__}")
    print(f"Scikit-learn version: {sklearn.__version__}")
    print(f"Pandas version: {pandas.__version__}")
    print(f"NumPy version: {numpy.__version__}")
    print(f"SciPy version: {scipy.__version__}")
    
except ImportError as e:
    print(f"❌ Import error: {e}")