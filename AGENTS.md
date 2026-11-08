# AGENTS.md — sale_order_pdf_download

Módulo Odoo 19 que agrega **Descargar PDF** al menú de acciones (engranaje) del
pedido de venta. Guía de usuario: `README.md`.

## Contexto del repo

- Addon Odoo 19 Community autocontenido. No hay Makefile, tests, CI ni linter:
  no busques `pytest`, `ruff`, `pre-commit` ni `make`.
- Nombre técnico: `sale_order_pdf_download` (es la carpeta y el identificador
  de instalación; no cambiarlo). Nombre visible en Apps: **PDF en Órdenes de
  Venta**, definido en `name` de `__manifest__.py`.
- La verificación es manual: coloca el directorio padre en `addons_path`,
  instala/actualiza y prueba desde el formulario.

  ```bash
  odoo -d <base_de_datos> -i sale_order_pdf_download --stop-after-init
  odoo -d <base_de_datos> -u sale_order_pdf_download --stop-after-init
  ```

  También se puede instalar desde Apps con el modo desarrollador activo.
- Usa el checklist del `README.md`: descarga desde el engranaje, nombre del
  archivo y bloqueo de crédito.

## Flujo (no romper la cadena)

`data/ir_actions_server.xml` (server action) → `sale.order.action_download_pdf`
→ `act_url` `/sale/order/download_pdf/<id>` → `controllers/main.py` →
`_render_qweb_pdf()` de `sale.report_saleorder` → respuesta adjunta.

- El controlador es alcanzable por URL directa. Cada ruta de descarga debe
  repetir `order.check_access("read")` y `order._check_pdf_download_allowed()`;
  no lo simplifiques a una sola capa ni uses `sudo()`.
- `_render_qweb_pdf()` devuelve una tupla `(pdf, report_type)`; hay que
  desempaquetarla.
- El reporte está hardcodeado como `sale.report_saleorder`. Si se cambia la
  plantilla estándar, actualiza también el controlador.
- Orden inexistente → `request.not_found()`. `UserError`/`AccessError` →
  respuesta 403 en texto plano.
- Nombre del archivo: `Cotizacion_*` para `draft`/`sent`, `Pedido_*` para el
  resto; se sanea con regex. No uses `order.name` crudo (los folios llevan
  `/`).

## Trampas de Odoo 19

- En un server action, la variable `model` llega como recordset vacío. Resuelve
  los ids con `active_ids` / `active_id` del contexto (como hace el XML); usar
  `model` provoca `Expected singleton: sale.order()`.
- El Python dentro de `<field name="code">` debe quedar a columna 0, como está.
  La primera línea indentada funciona solo porque Odoo hace `str.strip()`;
  indentar las demás produce `IndentationError`.
- La acción se engancha con `binding_model_id` + `binding_type=action`. Si no
  aparece en el engranaje, revisa esos campos y que el módulo esté instalado.

## Dependencia opcional de crédito

- **No** agregues `sale_credit_approval_gate` a `depends`: el módulo debe
  instalar sin él.
- Detección en runtime: `"credit_gate_required" in self._fields`; el import de
  `raise_credit_blocked` es perezoso dentro del método. Sigue ese patrón para
  cualquier dependencia blanda.
- Campos del gate que se consultan: `credit_gate_required` (calculado) y
  `credit_gate_state` (`approved`).
- `wk_odoo_direct_print` no se modifica: la convivencia con PrintDirect es el
  motivo del módulo.

## Convenciones

- Odoo 19 Community, licencia LGPL-3. `version` del manifiesto en formato
  `19.0.x.y.z`.
- Al cambiar comportamiento, sube la versión y agrega una entrada al historial
  de `README.md` (se viene haciendo desde `19.0.1.0.0`).
- Textos de UI, comentarios y descripción del manifiesto en español.
- Documentación bilingüe: `README.md` en inglés (principal) y `README.es.md` en
  español. Ambos se enlazan entre sí y deben actualizarse juntos.
- No hay ACL propias: se reutilizan las de `sale` y el acceso se valida con
  `check_access("read")`.
