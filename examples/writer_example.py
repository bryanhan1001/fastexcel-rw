#!/usr/bin/env python3
"""
fastexcel_rw Writer Example

This example demonstrates how to use fastexcel_rw's writer functionality to create Excel files.
Requires writer feature: pip install fastexcel_rw[writer]
"""

import sys
from pathlib import Path

try:
    from fastexcel_rw import create_writer, read_excel
except ImportError:
    print("Please install fastexcel_rw: pip install fastexcel_rw[writer]")
    sys.exit(1)


def create_sample_excel():
    """Create a sample Excel file"""

    # Create writer
    output_path = "sample_output.xlsx"
    writer = create_writer(output_path)

    print(f"Creating Excel file: {output_path}")

    # Example 1: Employee data
    print("Writing employee data...")
    employee_data = [
        ["Alice", 28, "Software Engineer", 8500.50, True],
        ["Bob", 32, "Product Manager", 12000.00, True],
        ["Charlie", 26, "UI Designer", 7000.75, False],
        ["David", 35, "Project Manager", 15000.25, True],
    ]
    employee_headers = ["Name", "Age", "Position", "Salary", "Active"]

    writer.write_sheet_data(employee_data, "Employees", employee_headers)

    # Example 2: Sales data
    print("Writing sales data...")
    sales_data = [
        ["2024-01", "Product A", 1200, 25.99],
        ["2024-01", "Product B", 800, 35.50],
        ["2024-02", "Product A", 1500, 25.99],
        ["2024-02", "Product B", 950, 35.50],
        ["2024-03", "Product A", 1800, 26.99],
        ["2024-03", "Product B", 1100, 36.50],
    ]
    sales_headers = ["Month", "Product", "Sales", "Price"]

    writer.write_sheet_data(sales_data, "Sales", sales_headers)

    # Example 3: Mixed data types
    print("Writing mixed data types...")
    mixed_data = [
        ["String", 42, 3.14159, True, None],
        ["Another string", -10, 0.0, False, "Non-empty"],
        ["Test", 100, 99.99, True, "Complete"],
    ]
    mixed_headers = ["Text", "Integer", "Float", "Boolean", "Nullable"]

    writer.write_sheet_data(mixed_data, "Mixed Types", mixed_headers)

    # Save file
    print("Saving file...")
    writer.save()

    print(f"Excel file created: {Path(output_path).absolute()}")
    return output_path


def read_and_verify(file_path):
    """Read and verify the created Excel file"""
    print(f"\nVerifying created file: {file_path}")

    # Read Excel file
    reader = read_excel(file_path)

    print(f"Sheet list: {reader.sheet_names}")

    # Read each worksheet
    for sheet_name in reader.sheet_names:
        print(f"\n=== {sheet_name} ===")
        sheet = reader.load_sheet_by_name(sheet_name)

        print(f"Dimensions: {sheet.height} rows x {sheet.width} columns")

        # Convert to pandas DataFrame and display first few rows
        try:
            df = sheet.to_pandas()
            print("First few rows:")
            print(df.head())
        except ImportError:
            print("Need pandas to display data")
            # Use pyarrow instead
            batch = sheet.to_arrow()
            print(f"Data structure: {batch.schema}")


def main():
    """Main function"""
    print("fastexcel_rw Writer Example")
    print("=" * 40)

    try:
        # Create sample file
        output_file = create_sample_excel()

        # Read and verify
        read_and_verify(output_file)

        print(f"\nExample completed! Please check file: {output_file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
