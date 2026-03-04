# Aether Cortex

The Neural Signal Layer for Aether Voice OS. This crate contains biologically inspired audio DSP algorithms implemented in Rust and exposed as a Python module.

## Build Instructions

This project is built as a Python extension module using `maturin`.

### Prerequisites

*   **Rust:** Ensure you have the Rust toolchain installed. You can install it from [rust-lang.org](https://www.rust-lang.org/tools/install).
*   **Python:** Python 3.10 or newer is required.
*   **Virtual Environment:** It is highly recommended to work within a Python virtual environment.

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

### Development Build

For development, you can build and install the package in editable mode. This allows you to test your changes without reinstalling the package every time.

From within the `aether-cortex` directory, run:

```bash
pip install -e .
```

Alternatively, you can use `maturin` directly:

```bash
maturin develop
```

### Release Build

To build a release wheel for distribution, run:

```bash
maturin build --release
```

This will create a `.whl` file in the `target/wheels/` directory, which can then be installed using `pip`.
