use pyo3::prelude::*;
use pyo3::types::PyList;
use rust_xlsxwriter::*;

use crate::error::FastExcelResult;

/// Excel writer that supports writing multiple worksheets
#[pyclass(name = "ExcelWriter")]
pub struct ExcelWriter {
    workbook: Option<Workbook>,
    file_path: String,
    sheet_names: Vec<String>,
}

impl ExcelWriter {
    /// Create a new Excel writer
    pub fn new(file_path: String) -> FastExcelResult<Self> {
        let workbook = Workbook::new();
        Ok(Self {
            workbook: Some(workbook),
            file_path,
            sheet_names: Vec::new(),
        })
    }

    fn get_worksheet_index(&self, sheet_name: &str) -> Option<usize> {
        self.sheet_names.iter().position(|name| name == sheet_name)
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
        // Input validation
        if data.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Data cannot be empty",
            ));
        }

        if sheet_name.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Sheet name cannot be empty",
            ));
        }

        if self.get_worksheet_index(sheet_name).is_some() {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Sheet '{}' already exists",
                sheet_name
            )));
        }

        let workbook = self.workbook.as_mut().ok_or_else(|| {
            pyo3::exceptions::PyRuntimeError::new_err("Workbook has been closed")
        })?;

        let worksheet = workbook.add_worksheet().set_name(sheet_name).map_err(|e| {
            pyo3::exceptions::PyRuntimeError::new_err(format!("Failed to create worksheet: {}", e))
        })?;

        self.sheet_names.push(sheet_name.to_string());

        let mut row_num = 0;

        // Write headers
        if let Some(headers) = headers {
            if headers.is_empty() {
                return Err(pyo3::exceptions::PyValueError::new_err(
                    "Headers list cannot be empty if provided",
                ));
            }
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
                    // Skip null values (leave cell empty)
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
        index: Option<bool>,
    ) -> PyResult<()> {
        // Input validation
        if sheet_name.is_empty() {
            return Err(pyo3::exceptions::PyValueError::new_err(
                "Sheet name cannot be empty",
            ));
        }

        if self.get_worksheet_index(sheet_name).is_some() {
            return Err(pyo3::exceptions::PyValueError::new_err(format!(
                "Sheet '{}' already exists",
                sheet_name
            )));
        }

        let include_index = index.unwrap_or(false);

        // Get column names
        let columns = df.getattr("columns")?;
        let column_names: Vec<String> = columns.call_method0("tolist")?.extract()?;

        // Get index as list if we need to include it
        let index_values: Option<Vec<String>> = if include_index {
            let index_obj = df.getattr("index")?;
            Some(index_obj.call_method0("tolist")?.extract()?)
        } else {
            None
        };

        // Get data values
        let values = df.call_method0("values")?;
        let data_list: Vec<Vec<PyObject>> = values.call_method0("tolist")?.extract()?;

        // Convert to Python list format with index if needed
        let py = df.py();
        let py_data = PyList::empty(py);

        for row in data_list {
            let py_row = PyList::new(py, row)?;
            py_data.append(py_row)?;
        }

        // Build headers with index column if needed
        let final_headers = if include_index {
            let index_obj = df.getattr("index")?;
            let index_name = index_obj.getattr("name")?;
            let index_col_name: String = index_name.extract()?;
            let mut headers = vec![if index_col_name.is_empty() { "index" } else { &index_col_name }.to_string()];
            headers.extend(column_names);
            Some(headers)
        } else {
            Some(column_names)
        };

        // If including index, we need to prepend index values to each row
        if include_index {
            let py_data_with_index = PyList::empty(py);
            let index_vals = index_values.unwrap();
            for (i, py_row) in py_data.iter().enumerate() {
                let row_list = py_row.downcast::<PyList>()?;
                let new_row = PyList::new(py, vec![pyo3::IntoPyObject::into_pyobject(&index_vals[i], py)?.into_any()])?;
                for item in row_list.iter() {
                    new_row.append(item)?;
                }
                py_data_with_index.append(new_row)?;
            }
            self.write_sheet_data(&py_data_with_index, sheet_name, final_headers)
        } else {
            self.write_sheet_data(&py_data, sheet_name, final_headers)
        }
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

    /// Check if workbook is still open
    pub fn is_open(&self) -> bool {
        self.workbook.is_some()
    }

    /// Get list of sheet names that have been added
    #[getter]
    pub fn sheet_names(&self) -> Vec<String> {
        self.sheet_names.clone()
    }

    /// Get output file path
    #[getter]
    pub fn file_path(&self) -> &str {
        &self.file_path
    }
}

/// Convenient function to create Excel writer
#[pyfunction]
pub fn create_excel_writer(file_path: String) -> PyResult<ExcelWriter> {
    ExcelWriter::py_new(file_path)
} 