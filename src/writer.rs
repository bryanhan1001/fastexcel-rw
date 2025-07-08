use pyo3::prelude::*;
use pyo3::types::PyList;
use rust_xlsxwriter::*;

use crate::error::FastExcelResult;

/// Excel writer that supports writing multiple worksheets
#[pyclass(name = "ExcelWriter")]
pub struct ExcelWriter {
    workbook: Option<Workbook>,
    file_path: String,
}

impl ExcelWriter {
    /// Create a new Excel writer
    pub fn new(file_path: String) -> FastExcelResult<Self> {
        let workbook = Workbook::new();
        Ok(Self {
            workbook: Some(workbook),
            file_path,
        })
    }
}

#[pymethods]
impl ExcelWriter {
    /// Create a new Excel writer
    #[new]
    pub fn py_new(file_path: String) -> PyResult<Self> {
        Self::new(file_path).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create ExcelWriter: {}", e))
        })
    }

    /// Write 2D data to specified worksheet
    pub fn write_sheet_data(
        &mut self,
        data: &Bound<'_, PyList>,
        sheet_name: &str,
        headers: Option<Vec<String>>,
    ) -> PyResult<()> {
        let workbook = self.workbook.as_mut().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Workbook has been closed")
        })?;

        let worksheet = workbook.add_worksheet().set_name(sheet_name).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create worksheet: {}", e))
        })?;

        let mut row_num = 0;

        // Write headers
        if let Some(headers) = headers {
            for (col_num, header) in headers.iter().enumerate() {
                worksheet.write_string(row_num, col_num as u16, header).map_err(|e| {
                    pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to write header: {}", e))
                })?;
            }
            row_num += 1;
        }

        // Write data rows
        for py_row in data.iter() {
            let row_list = py_row.downcast::<PyList>().map_err(|_| {
                pyo3::exceptions::PyTypeError::new_err("Each row must be a list")
            })?;

            for (col_num, py_cell) in row_list.iter().enumerate() {
                // Try different data types
                if let Ok(value) = py_cell.extract::<String>() {
                    worksheet.write_string(row_num, col_num as u16, &value).map_err(|e| {
                        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to write string: {}", e))
                    })?;
                } else if let Ok(value) = py_cell.extract::<i64>() {
                    worksheet.write_number(row_num, col_num as u16, value as f64).map_err(|e| {
                        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to write number: {}", e))
                    })?;
                } else if let Ok(value) = py_cell.extract::<f64>() {
                    worksheet.write_number(row_num, col_num as u16, value).map_err(|e| {
                        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to write number: {}", e))
                    })?;
                } else if let Ok(value) = py_cell.extract::<bool>() {
                    worksheet.write_boolean(row_num, col_num as u16, value).map_err(|e| {
                        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to write boolean: {}", e))
                    })?;
                } else if py_cell.is_none() {
                    // Skip null values
                    continue;
                } else {
                    // Convert other types to string
                    let value = py_cell.str()?.to_string();
                    worksheet.write_string(row_num, col_num as u16, &value).map_err(|e| {
                        pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to write string: {}", e))
                    })?;
                }
            }
            row_num += 1;
        }

        Ok(())
    }

    /// Write data from pandas DataFrame
    pub fn write_dataframe(
        &mut self,
        df: &Bound<'_, PyAny>,
        sheet_name: &str,
        _index: Option<bool>,
    ) -> PyResult<()> {
        // Get column names
        let columns = df.getattr("columns")?;
        let column_names: Vec<String> = columns.call_method0("tolist")?.extract()?;

        // Get data
        let values = df.call_method0("values")?;
        let data_list: Vec<Vec<PyObject>> = values.call_method0("tolist")?.extract()?;

        // Convert to Python list format
        let py = df.py();
        let py_data = PyList::empty(py);
        
        for row in data_list {
            let py_row = PyList::new(py, row)?;
            py_data.append(py_row)?;
        }

        // Write data
        self.write_sheet_data(&py_data, sheet_name, Some(column_names))
    }

    /// Save file
    pub fn save(&mut self) -> PyResult<()> {
        let mut workbook = self.workbook.take().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Workbook has already been saved")
        })?;

        workbook.save(&self.file_path).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to save workbook: {}", e))
        })?;

        Ok(())
    }

    /// Close writer (save file)
    pub fn close(&mut self) -> PyResult<()> {
        self.save()
    }

    /// Add worksheet
    pub fn add_worksheet(&mut self, name: &str) -> PyResult<()> {
        let workbook = self.workbook.as_mut().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Workbook has been closed")
        })?;

        workbook.add_worksheet().set_name(name).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to add worksheet: {}", e))
        })?;

        Ok(())
    }

    /// Set column width
    pub fn set_column_width(&mut self, _sheet_name: &str, _column: u16, _width: f64) -> PyResult<()> {
        // This requires more complex implementation to get specific worksheet
        // For simplicity, we provide basic functionality first
        Ok(())
    }
}

/// Convenient function to create Excel writer
#[pyfunction]
pub fn create_excel_writer(file_path: String) -> PyResult<ExcelWriter> {
    ExcelWriter::py_new(file_path)
} 