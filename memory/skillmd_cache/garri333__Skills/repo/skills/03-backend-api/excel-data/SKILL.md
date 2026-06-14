---
name: excel-data
version: 1.0.0
description: Leer, escribir y manipular archivos Excel (XLSX) con Python usando openpyxl y pandas. Usa cuando necesites procesar hojas de cálculo, automatizar reportes Excel, o extraer datos de archivos .xlsx.
tags: [excel, xlsx, pandas, openpyxl, spreadsheet, data, automation, reporting]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# Excel Data Skill

## Cuándo usar esta skill
- Leer datos de un archivo Excel (.xlsx, .xls)
- Generar reportes en formato Excel con formato
- Automatizar la creación de hojas de cálculo
- Transformar datos entre Excel y otros formatos (CSV, JSON, DB)

## Setup

```bash
pip install openpyxl pandas xlsxwriter
```

## Leer Excel con pandas

```python
import pandas as pd

# Leer hoja por defecto
df = pd.read_excel("datos.xlsx")

# Leer hoja específica
df = pd.read_excel("datos.xlsx", sheet_name="Ventas")

# Leer múltiples hojas
sheets = pd.read_excel("datos.xlsx", sheet_name=None)  # Devuelve dict {nombre: df}
for sheet_name, df in sheets.items():
    print(f"Hoja: {sheet_name}, Filas: {len(df)}")

# Opciones útiles
df = pd.read_excel(
    "datos.xlsx",
    sheet_name="Sheet1",
    header=0,           # Fila 0 es el header (default)
    skiprows=2,         # Saltar las primeras 2 filas
    usecols="A:E",      # Solo columnas A a E
    nrows=100,          # Solo las primeras 100 filas
    dtype={"ID": str},  # Forzar tipo de columna
    na_values=["N/A", "-", ""],  # Valores nulos
)

# Información básica
print(df.head())
print(df.dtypes)
print(df.describe())
print(f"Shape: {df.shape}")
```

## Escribir Excel con pandas

```python
# Exportar single sheet
df.to_excel("output.xlsx", index=False, sheet_name="Datos")

# Múltiples hojas en el mismo archivo
with pd.ExcelWriter("report.xlsx", engine="openpyxl") as writer:
    df_ventas.to_excel(writer, sheet_name="Ventas", index=False)
    df_clientes.to_excel(writer, sheet_name="Clientes", index=False)
    df_resumen.to_excel(writer, sheet_name="Resumen", index=False)

# Con formato usando xlsxwriter
with pd.ExcelWriter("formatted.xlsx", engine="xlsxwriter") as writer:
    df.to_excel(writer, sheet_name="Datos", index=False)
    
    workbook = writer.book
    worksheet = writer.sheets["Datos"]
    
    # Formato para headers
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2B5CE6',
        'font_color': 'white',
        'border': 1,
    })
    
    # Aplicar formato a headers
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_format)
    
    # Auto-ajustar ancho de columnas
    for i, col in enumerate(df.columns):
        max_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
        worksheet.set_column(i, i, min(max_len, 50))
```

## openpyxl — Control granular

```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

# Crear nuevo workbook
wb = Workbook()
ws = wb.active
ws.title = "Reporte"

# Escribir datos
ws["A1"] = "Producto"
ws["B1"] = "Unidades"
ws["C1"] = "Precio"
ws["D1"] = "Total"

datos = [
    ("Producto A", 100, 29.99),
    ("Producto B", 250, 14.99),
    ("Producto C", 75, 49.99),
]

for row, (producto, unidades, precio) in enumerate(datos, start=2):
    ws[f"A{row}"] = producto
    ws[f"B{row}"] = unidades
    ws[f"C{row}"] = precio
    ws[f"D{row}"] = f"=B{row}*C{row}"  # Fórmula

# Estilos
header_fill = PatternFill(start_color="2B5CE6", end_color="2B5CE6", fill_type="solid")
header_font = Font(bold=True, color="FFFFFF", size=12)

for cell in ws[1]:  # Primera fila
    cell.fill = header_fill
    cell.font = header_font
    cell.alignment = Alignment(horizontal="center")

# Formato de número para columna precio
from openpyxl.styles.numbers import FORMAT_CURRENCY_EUR_SIMPLE
for row in ws.iter_rows(min_row=2, min_col=3, max_col=4):
    for cell in row:
        cell.number_format = '#,##0.00 "€"'

# Auto-ajustar columnas
for column in ws.columns:
    max_length = max(len(str(cell.value or "")) for cell in column) + 2
    ws.column_dimensions[get_column_letter(column[0].column)].width = min(max_length, 50)

# Añadir fila de totales
last_row = ws.max_row + 1
ws[f"A{last_row}"] = "TOTAL"
ws[f"B{last_row}"] = f"=SUM(B2:B{last_row-1})"
ws[f"D{last_row}"] = f"=SUM(D2:D{last_row-1})"
ws[f"A{last_row}"].font = Font(bold=True)
ws[f"D{last_row}"].font = Font(bold=True)

# Añadir gráfico de barras
chart = BarChart()
chart.type = "col"
chart.style = 10
chart.title = "Ventas por Producto"
chart.y_axis.title = "Total €"
chart.x_axis.title = "Producto"

data = Reference(ws, min_col=4, min_row=1, max_row=ws.max_row - 1)
chart.add_data(data, titles_from_data=True)
categories = Reference(ws, min_col=1, min_row=2, max_row=ws.max_row - 1)
chart.set_categories(categories)
chart.shape = 4
ws.add_chart(chart, "F1")

# Guardar
wb.save("reporte_ventas.xlsx")
```

## Leer Excel existente y modificar

```python
def update_excel_report(filepath: str, new_data: pd.DataFrame, sheet_name: str = "Datos"):
    """Actualizar una hoja existente sin perder otras hojas"""
    wb = load_workbook(filepath)
    
    # Eliminar hoja si existe
    if sheet_name in wb.sheetnames:
        del wb[sheet_name]
    
    # Crear nueva hoja
    ws = wb.create_sheet(sheet_name)
    
    # Escribir headers
    for col, header in enumerate(new_data.columns, start=1):
        ws.cell(row=1, column=col, value=header)
    
    # Escribir datos
    for row_idx, row in enumerate(new_data.itertuples(index=False), start=2):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)
    
    wb.save(filepath)
    print(f"✅ Hoja '{sheet_name}' actualizada en {filepath}")
```

## Patrones comunes

### Consolidar múltiples archivos Excel
```python
def consolidate_excel_files(folder_path: str, output_file: str) -> pd.DataFrame:
    """Unir todos los xlsx de una carpeta en un solo DataFrame"""
    import glob
    
    files = glob.glob(f"{folder_path}/*.xlsx")
    
    dfs = []
    for file in files:
        df = pd.read_excel(file)
        df['source_file'] = Path(file).name  # Añadir columna de origen
        dfs.append(df)
    
    result = pd.concat(dfs, ignore_index=True)
    result.to_excel(output_file, index=False)
    
    print(f"Consolidados {len(files)} archivos: {len(result)} filas totales")
    return result
```

### Excel a JSON/dict
```python
def excel_to_records(filepath: str, sheet_name: str = 0) -> list[dict]:
    """Convertir Excel a lista de registros (dicts)"""
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    return df.to_dict(orient='records')

# Uso:
records = excel_to_records("clientes.xlsx")
# [{"nombre": "Ana", "email": "ana@email.com", ...}, ...]
```

## Referencias
- [openpyxl documentation](https://openpyxl.readthedocs.io/)
- [pandas Excel I/O](https://pandas.pydata.org/docs/user_guide/io.html#excel-files)
- [xlsxwriter documentation](https://xlsxwriter.readthedocs.io/)
