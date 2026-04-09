# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fastexcel-rw is a fork of [ToucanToco/fastexcel](https://github.com/ToucanToco/fastexcel) that adds Excel writing functionality. It's a high-performance Python library for reading and writing Excel files, powered by Rust (PyO3 bindings).

- **Reading**: Uses `calamine` crate for parsing xlsx/xls/ods files
- **Writing**: Uses `rust_xlsxwriter` crate (optional feature) for creating Excel files
- **Output formats**: PyArrow RecordBatch (convertible to pandas/polars)

## Build Commands

```bash
# Development install (with writer feature)
make dev-install              # maturin develop --uv -E pandas,polars -F writer

# Production install
make prod-install             # Uses prod_install.sh

# Build wheel
maturin build --features writer

# Run tests
make test                     # Both Rust and Python tests
make test-rust                # cargo test --no-default-features --features tests
make test-python              # pytest -v

# Run single Python test
pytest -v python/tests/test_writer.py::TestExcelWriter::test_write_simple_data

# Lint
make lint                     # Both Rust (clippy) and Python (ruff + mypy)
make lint-rust
make lint-python

# Format
make format                   # Both Rust and Python
```

## Architecture

### Rust Layer (`src/`)
- `lib.rs` - PyO3 module definition, exports `read_excel` and `ExcelWriter` (conditional)
- `writer.rs` - Excel writing implementation (feature-gated with `#[cfg(feature = "writer")]`)
- `data.rs` - Data conversion from calamine to Arrow arrays
- `error.rs` - Error types and context handling
- `types/` - Type definitions for ExcelReader, ExcelSheet, ExcelTable, ColumnInfo
  - `python/excelreader.rs` - Reader that opens Excel files
  - `python/excelsheet/mod.rs` - Sheet representation with Arrow conversion
  - `python/excelsheet/column_info.rs` - Column metadata
  - `python/table.rs` - Excel table structure

### Python Layer (`python/fastexcel_rw/`)
- `__init__.py` - Public API wrappers: `read_excel()`, `ExcelReader`, `ExcelSheet`, `create_writer()`, `ExcelWriter`
- `_fastexcel.pyi` - Type stubs for the Rust extension module

### Key Patterns
- **Reader pattern**: `read_excel(path)` → `ExcelReader` → `load_sheet()` → `ExcelSheet` → `.to_arrow()/.to_pandas()/.to_polars()`
- **Writer pattern**: `create_writer(path)` → `ExcelWriter` → `.write_sheet_data()/.write_dataframe()` → `.save()`

## Important Notes

1. **Writer feature is optional**: Must compile with `-F writer` or `--features writer` flag. Python imports gracefully handle absence with `_WRITER_AVAILABLE` flag.

2. **abi3 wheels**: Built once per platform, works across Python 3.9-3.13.

3. **Rust edition 2024**: Requires Rust 1.85.0+.

4. **Tests require special feature**: Rust tests use `--features tests` which enables `pyo3/auto-initialize` (see Cargo.toml comment about PyO3 testing limitations).

5. **Type coercion**: Reading supports `dtype_coercion="coerce"` (default) or `"strict"` mode for column type inference.