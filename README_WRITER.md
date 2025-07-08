# fastexcel Writer Feature

fastexcel now supports Excel file writing! 🎉

## Installation

To use the writer feature, install fastexcel with the `writer` feature:

```bash
pip install fastexcel[writer]
```

## Features

- ✅ **High Performance Writing**: Built on `rust_xlsxwriter` library
- ✅ **Multiple Data Types**: Support for strings, numbers, booleans, dates, etc.
- ✅ **Multiple Worksheets**: Create multiple worksheets
- ✅ **pandas Integration**: Write directly from DataFrames
- ✅ **Type Safety**: Memory safety guaranteed by Rust
- ✅ **Simple API**: Easy-to-use Python interface

## Basic Usage

### Create Simple Excel File

```python
from fastexcel import create_writer

# Create writer
writer = create_writer("output.xlsx")

# Prepare data
data = [
    ["Alice", 25, True],
    ["Bob", 30, False],
    ["Charlie", 35, True]
]
headers = ["Name", "Age", "Active"]

# Write data
writer.write_sheet_data(data, "Sheet1", headers)

# Save file
writer.save()
```

### Write Multiple Worksheets

```python
from fastexcel import create_writer

writer = create_writer("multi_sheet.xlsx")

# First worksheet
employee_data = [
    ["Alice", "Engineer", 8500],
    ["Bob", "Designer", 7500]
]
writer.write_sheet_data(employee_data, "Employees", ["Name", "Position", "Salary"])

# Second worksheet
sales_data = [
    ["2024-01", 1200, 25.99],
    ["2024-02", 1500, 26.50]
]
writer.write_sheet_data(sales_data, "Sales", ["Month", "Volume", "Price"])

writer.save()
```

### Write from pandas DataFrame

```python
import pandas as pd
from fastexcel import create_writer

# Create DataFrame
df = pd.DataFrame({
    'Product': ['A', 'B', 'C'],
    'Price': [10.5, 20.0, 15.75],
    'In_Stock': [True, False, True]
})

# Write to Excel
writer = create_writer("from_dataframe.xlsx")
writer.write_dataframe(df, "Products")
writer.save()
```

## API Reference

### `create_writer(file_path)`

Create a new Excel writer.

**Parameters:**
- `file_path`: Output file path (string or Path object)

**Returns:** `ExcelWriter` instance

### `ExcelWriter` Class

#### `write_sheet_data(data, sheet_name, headers=None)`

Write 2D list data to specified worksheet.

**Parameters:**
- `data`: 2D list, each sublist represents a row of data
- `sheet_name`: Worksheet name
- `headers`: Optional column headers list

#### `write_dataframe(df, sheet_name, index=None)`

Write data from pandas DataFrame.

**Parameters:**
- `df`: pandas DataFrame
- `sheet_name`: Worksheet name
- `index`: Whether to include index (not implemented yet)

#### `save()`

Save the Excel file.

#### `close()`

Close the writer (equivalent to `save()`).

## Supported Data Types

| Python Type | Excel Type | Description |
|-------------|-----------|-------------|
| `str` | Text | String data |
| `int` | Number | Integer |
| `float` | Number | Float |
| `bool` | Boolean | True/False |
| `None` | Empty | Empty cell |
| Others | Text | Convert to string |

## Performance Comparison

Writing performance based on `rust_xlsxwriter` is excellent:

- **3.8x faster than Python xlsxwriter**
- **9.4x faster than openpyxl**
- **More memory efficient**

## Combining with Reading Functionality

fastexcel's reading and writing features work perfectly together:

```python
from fastexcel import read_excel, create_writer

# Read existing file
reader = read_excel("input.xlsx")
sheet = reader.load_sheet_by_name("Data")
df = sheet.to_pandas()

# Process data
df['New_Column'] = df['Value'] * 2

# Write new file
writer = create_writer("processed.xlsx")
writer.write_dataframe(df, "Processed_Data")
writer.save()
```

## Complete Example

See `examples/writer_example.py` for complete usage examples.

## Notes

1. **Optional Feature**: Writing functionality is optional and requires explicit installation of the `writer` feature
2. **Create New Files Only**: Currently doesn't support modifying existing Excel files
3. **Basic Formatting**: Currently supports basic data writing, more formatting options will be added in future versions

## Future Plans

- [ ] Cell formatting (font, color, borders, etc.)
- [ ] Formula support
- [ ] Chart support
- [ ] Data validation
- [ ] Conditional formatting
- [ ] More data type support (dates, times, etc.)

## Contributing

Welcome to submit Issues and Pull Requests to improve the writing functionality! 