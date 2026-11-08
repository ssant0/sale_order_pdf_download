{
    "name": "PDF en Órdenes de Venta",
    "version": "19.0.1.0.4",
    "summary": "Descarga el PDF de la orden sin pasar por la impresión directa.",
    "description": """
PDF en Órdenes de Venta
=======================

Agrega la acción **Descargar PDF** al menú del engranaje (Acción) de la orden
de venta. Descarga el PDF estándar `sale.report_saleorder` como archivo, sin
pasar por la impresión directa de `wk_odoo_direct_print`.

Está pensado para convivir con PrintDirect: el botón **Imprimir** manda el
documento a la impresora y no siempre permite obtener el archivo; esta acción
solo descarga el PDF para cuando necesitas el formato digital.

- Una sola orden, desde el formulario.
- No modifica `wk_odoo_direct_print`.
- Si `sale_credit_approval_gate` está instalado, respeta el bloqueo de crédito.
  Si no está instalado, funciona de forma independiente.
""",
    "author": "ssant0",
    "website": "https://github.com/ssant0/sale_order_pdf_download",
    "license": "LGPL-3",
    "category": "Sales",
    "depends": ["sale_management"],
    "data": [
        "data/ir_actions_server.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
