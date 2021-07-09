# External-Linking-in-Python
This repository demonstrates how to run Rust and C++ libraries in Python.

# Installation
Download package and compile C++ and Rust files into .so libraries.
To compile the C++ files into a .so library, install CMake and run

```cmake ./; make```

To compile the Rust file into a .so library, install rustc and run

`rustc -o lib_rust_xorcipher.so xorcipher.rs --crate-type cdylib`

# Run
Run with `python cipher.py`
