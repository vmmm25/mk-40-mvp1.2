---
name: pdf-builder
version: 1.0.0
description: Generar PDFs profesionales a partir de Markdown, HTML o plantillas con Pandoc, WeasyPrint o Puppeteer. Usa cuando necesites crear reportes, facturas, documentación o cualquier documento en PDF.
tags: [pdf, pandoc, weasyprint, puppeteer, documents, reporting, markdown, html]
author: garri333
license: MIT
source: https://clawdbotskills.org/
---

# PDF Builder Skill

## Cuándo usar esta skill
- Generar un reporte, factura, o documento en PDF
- Convertir Markdown a PDF con formato profesional
- Crear PDFs desde plantillas HTML
- Generar PDFs desde páginas web existentes

## Opciones disponibles

| Herramienta | Input | Ideal para | Requiere |
|-------------|-------|-----------|---------|
| Pandoc + LaTeX | Markdown | Documentación técnica, papers | pandoc + LaTeX |
| WeasyPrint | HTML/CSS | Facturas, reportes con CSS | Python |
| Puppeteer/Playwright | HTML/URL | Screenshots, documentos web | Node.js |
| reportlab | Python | PDFs programáticos | Python |
| fpdf2 | Python | PDFs simples | Python |

## Opción 1: Pandoc (Markdown → PDF)

```bash
# Instalar pandoc
# https://pandoc.org/installing.html
# + LaTeX: tlmgr install collection-latex

# Conversión básica
pandoc documento.md -o documento.pdf

# Con tema y opciones
pandoc documento.md \
  --pdf-engine=xelatex \
  -V geometry:margin=2cm \
  -V fontsize=12pt \
  -V lang=es \
  -o documento.pdf

# Con template personalizado
pandoc documento.md \
  --template=mi-template.tex \
  --variables-file=variables.yaml \
  -o documento.pdf

# Con tabla de contenidos
pandoc documento.md --toc --toc-depth=3 -o documento.pdf
```

## Opción 2: WeasyPrint (HTML/CSS → PDF)

```bash
pip install weasyprint
```

```python
from weasyprint import HTML, CSS
from pathlib import Path

def markdown_to_pdf(markdown_text: str, output_path: str, title: str = "Documento"):
    """Convertir Markdown a PDF via HTML con WeasyPrint"""
    import markdown
    
    # Convertir Markdown a HTML
    md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
    html_body = md.convert(markdown_text)
    
    # Template HTML completo con estilos
    html_content = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
  
  @page {{
    margin: 2.5cm;
    @bottom-center {{
      content: counter(page) " / " counter(pages);
      font-size: 10pt;
      color: #666;
    }}
  }}
  
  body {{
    font-family: 'Inter', sans-serif;
    font-size: 11pt;
    line-height: 1.6;
    color: #333;
  }}
  
  h1 {{ font-size: 24pt; color: #1a1a1a; border-bottom: 2px solid #2B5CE6; padding-bottom: 8px; }}
  h2 {{ font-size: 16pt; color: #1a1a1a; margin-top: 24px; }}
  h3 {{ font-size: 13pt; color: #333; margin-top: 16px; }}
  
  code {{
    background: #f5f5f5;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 10pt;
  }}
  
  pre {{
    background: #f5f5f5;
    padding: 16px;
    border-radius: 8px;
    overflow: hidden;
    border-left: 4px solid #2B5CE6;
  }}
  
  pre code {{
    background: none;
    padding: 0;
  }}
  
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 16px 0;
  }}
  
  th {{
    background: #2B5CE6;
    color: white;
    padding: 8px 12px;
    text-align: left;
  }}
  
  td {{
    padding: 8px 12px;
    border-bottom: 1px solid #e0e0e0;
  }}
  
  tr:nth-child(even) {{ background: #f9f9f9; }}
  
  blockquote {{
    border-left: 4px solid #2B5CE6;
    margin: 0;
    padding: 8px 16px;
    background: #f0f4ff;
    color: #555;
  }}
  
  img {{ max-width: 100%; height: auto; }}
  
  a {{ color: #2B5CE6; }}
  
  .page-break {{ page-break-after: always; }}
</style>
</head>
<body>
{html_body}
</body>
</html>"""
    
    # Generar PDF
    HTML(string=html_content).write_pdf(output_path)
    print(f"✅ PDF generado: {output_path}")


def html_to_pdf(html_file: str, output_path: str, css_file: str = None):
    """Convertir archivo HTML a PDF"""
    stylesheets = []
    if css_file:
        stylesheets.append(CSS(filename=css_file))
    
    HTML(filename=html_file).write_pdf(output_path, stylesheets=stylesheets)
    print(f"✅ PDF generado: {output_path}")
```

## Opción 3: Playwright (HTML completo → PDF)

```python
from playwright.sync_api import sync_playwright

def html_or_url_to_pdf(
    source: str,      # URL o ruta de archivo HTML
    output_path: str,
    format: str = "A4",
    margin: dict = None
) -> str:
    """
    Genera un PDF renderizando con Chromium (fiel recreación de como se ve en el browser)
    """
    margin = margin or {
        "top": "1.5cm",
        "bottom": "1.5cm", 
        "left": "1.5cm",
        "right": "1.5cm"
    }
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        
        if source.startswith('http'):
            page.goto(source, wait_until='networkidle')
        else:
            page.goto(f'file://{source}', wait_until='networkidle')
        
        page.pdf(
            path=output_path,
            format=format,
            margin=margin,
            print_background=True  # Incluye colores de fondo
        )
        
        browser.close()
    
    return output_path


def generate_report_pdf(data: dict, template_html: str, output_path: str) -> str:
    """
    Generar PDF desde una plantilla HTML con datos variables
    """
    from jinja2 import Template
    
    # Renderizar plantilla con Jinja2
    template = Template(template_html)
    rendered_html = template.render(**data)
    
    # Guardar HTML temporal
    import tempfile
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.html', delete=False, encoding='utf-8'
    ) as f:
        f.write(rendered_html)
        tmp_html = f.name
    
    # Generar PDF
    try:
        html_or_url_to_pdf(tmp_html, output_path)
    finally:
        import os
        os.unlink(tmp_html)
    
    return output_path
```

## Plantilla de factura (ejemplo práctico)

```python
INVOICE_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
<style>
  body { font-family: 'Helvetica', sans-serif; margin: 0; padding: 40px; color: #333; }
  .header { display: flex; justify-content: space-between; margin-bottom: 40px; }
  .company-name { font-size: 24px; font-weight: bold; color: #2B5CE6; }
  .invoice-title { font-size: 36px; color: #2B5CE6; text-align: right; }
  .invoice-details { text-align: right; color: #666; }
  .bill-to { margin: 30px 0; }
  table { width: 100%; border-collapse: collapse; margin: 20px 0; }
  th { background: #2B5CE6; color: white; padding: 12px; text-align: left; }
  td { padding: 10px 12px; border-bottom: 1px solid #eee; }
  .total-row { font-weight: bold; font-size: 16px; background: #f0f4ff; }
  .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #666; font-size: 12px; }
</style>
</head>
<body>
  <div class="header">
    <div>
      <div class="company-name">{{ company_name }}</div>
      <div>{{ company_address }}</div>
      <div>NIF: {{ company_nif }}</div>
    </div>
    <div>
      <div class="invoice-title">FACTURA</div>
      <div class="invoice-details">
        <div>Nº {{ invoice_number }}</div>
        <div>Fecha: {{ invoice_date }}</div>
        <div>Vencimiento: {{ due_date }}</div>
      </div>
    </div>
  </div>
  
  <div class="bill-to">
    <strong>Facturar a:</strong><br>
    {{ client_name }}<br>
    {{ client_address }}<br>
    NIF: {{ client_nif }}
  </div>
  
  <table>
    <thead>
      <tr>
        <th>Descripción</th>
        <th style="text-align:right">Cantidad</th>
        <th style="text-align:right">Precio unitario</th>
        <th style="text-align:right">Total</th>
      </tr>
    </thead>
    <tbody>
      {% for item in items %}
      <tr>
        <td>{{ item.description }}</td>
        <td style="text-align:right">{{ item.quantity }}</td>
        <td style="text-align:right">{{ "%.2f"|format(item.unit_price) }} €</td>
        <td style="text-align:right">{{ "%.2f"|format(item.total) }} €</td>
      </tr>
      {% endfor %}
    </tbody>
    <tfoot>
      <tr><td colspan="3">Subtotal</td><td style="text-align:right">{{ "%.2f"|format(subtotal) }} €</td></tr>
      <tr><td colspan="3">IVA ({{ iva_pct }}%)</td><td style="text-align:right">{{ "%.2f"|format(iva_amount) }} €</td></tr>
      <tr class="total-row"><td colspan="3">TOTAL</td><td style="text-align:right">{{ "%.2f"|format(total) }} €</td></tr>
    </tfoot>
  </table>
  
  <div class="footer">
    <p>Forma de pago: {{ payment_method }}</p>
    <p>{{ notes }}</p>
  </div>
</body>
</html>"""


def generate_invoice(invoice_data: dict) -> str:
    """Generar factura en PDF"""
    # Calcular totales
    for item in invoice_data['items']:
        item['total'] = item['quantity'] * item['unit_price']
    
    invoice_data['subtotal'] = sum(i['total'] for i in invoice_data['items'])
    invoice_data['iva_amount'] = invoice_data['subtotal'] * (invoice_data.get('iva_pct', 21) / 100)
    invoice_data['total'] = invoice_data['subtotal'] + invoice_data['iva_amount']
    
    output_path = f"factura-{invoice_data['invoice_number']}.pdf"
    return generate_report_pdf(invoice_data, INVOICE_TEMPLATE, output_path)
```

## Referencias
- [Pandoc documentation](https://pandoc.org/MANUAL.html)
- [WeasyPrint docs](https://weasyprint.readthedocs.io/)
- [Playwright PDF API](https://playwright.dev/python/docs/api/class-page#page-pdf)
- [fpdf2 docs](https://py-pdf.github.io/fpdf2/)
