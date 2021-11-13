from setuptools import setup, find_packages

setup(
  name="rarian",
  version='0.1.0',
  author="Gilad Hecht",
  description='workspace manager to help you manage your work',
  extras_require={
    "dev": [
      "pytest>=6.2.5",
      "pytest-mock>=3.6.1"
    ]
  },
  py_modules=["rarian"],
  package_dir={'': 'src'},
  packages=find_packages(where="src"),
  python_requires=">=3.8",
)