# Project Repository

This repository is a collection of university coursework and personal projects, primarily developed in C++ and Python. The projects cover a range of topics from networking and data structures to various programming paradigms.

## Directory Structure

The repository is organized into the following main directories:

### `cpp`

This directory contains C++ projects.

- **`DCCN-Project-CPP`**: A miniature, multi-threaded, FTP-like server. This is a significant networking project that showcases client-server architecture and multi-threading in C++.

### `GNDEC-Labs`

This directory holds a collection of lab assignments for various university courses at GNDEC.

- **`GNDEC- DBMS`**: Lab work for Database Management Systems.
- **`GNDEC- DS`**: Lab work for Data Structures, with implementations of various algorithms and data structures in C++.
- **`GNDEC- OOPS`**: Lab work for Object-Oriented Programming, demonstrating concepts like classes, inheritance, and polymorphism in C++.
- **`GNDEC- PAS`**: Lab work for Probability and Statistics, with implementations in Python.

### `Practicals`

This directory contains reports and documentation corresponding to the lab work in the other directories. The documents are in `.docx` and `.tex` formats.

### `python`

This directory contains Python projects.

- **`DCCN-Project-Python`**: A Python implementation of the networking server, similar to the one in the `cpp` directory.
- **`DS-Project`**: A project related to data structures in Python.

## Environment Management

The projects in this repository use [Nix Flakes](https://nixos.wiki/wiki/Flakes) for creating reproducible development environments. The `flake.nix` files in the respective project directories define the dependencies and build instructions.
