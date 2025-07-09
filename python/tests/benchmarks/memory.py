import argparse
from enum import Enum

import fastexcel_rw


class Engine(str, Enum):
    FASTEXCEL = "fastexcel"
    XLRD = "xlrd"
    OPENPYXL = "pyxl"


def fastexcel_read(file_path: str):
    """Read Excel file using fastexcel_rw"""
    return fastexcel_rw.read_excel(file_path).load_sheet(0).to_polars()


def xlrd_read(file_path: str):
    """Read Excel file using xlrd (placeholder)"""
    # This is a placeholder - actual implementation would go here
    raise NotImplementedError("xlrd reading not implemented")


def pyxl_read(file_path: str):
    """Read Excel file using pyxl (placeholder)"""
    # This is a placeholder - actual implementation would go here
    raise NotImplementedError("pyxl reading not implemented")


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--engine", default=Engine.FASTEXCEL)
    parser.add_argument("file")
    return parser.parse_args()


def main():
    args = get_args()
    engine = args.engine

    if engine == Engine.FASTEXCEL:
        fastexcel_read(args.file)
    elif engine == Engine.XLRD:
        xlrd_read(args.file)
    elif engine == Engine.OPENPYXL:
        pyxl_read(args.file)


if __name__ == "__main__":
    main()
