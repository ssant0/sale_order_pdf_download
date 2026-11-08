# 📄 PDF en Órdenes de Venta

[English](README.md) · **Español**

Descarga el PDF de una orden de venta desde el menú del engranaje, sin pasar por la impresión directa.

[![Odoo 19](https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white)](https://www.odoo.com/)
[![GitHub](https://img.shields.io/badge/GitHub-ssant0%2Fsale__order__pdf__download-181717?logo=github)](https://github.com/ssant0/sale_order_pdf_download)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Versión](https://img.shields.io/badge/versi%C3%B3n-19.0.1.0.5-blue)](__manifest__.py)
[![Licencia LGPL-3](https://img.shields.io/badge/licencia-LGPL--3-blue)](LICENSE)
[![CI: manual](https://img.shields.io/badge/CI-manual-lightgrey)](#comandos-disponibles)

## Descripción

`PDF en Órdenes de Venta` es un addon de Odoo 19 que agrega la acción **Descargar PDF** al menú de acciones (engranaje) del pedido de venta. Resuelve el caso en que `wk_odoo_direct_print` (PrintDirect) envía el documento a la impresora y no siempre permite obtener el archivo: esta acción descarga el PDF estándar `sale.report_saleorder` directamente. Está pensado para equipos de ventas y administración que necesitan el documento digital sin alterar la configuración de impresión.

## Tabla de contenidos

- [Descripción](#descripción)
- [Stack técnico](#stack-técnico)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Variables de entorno](#variables-de-entorno)
- [Uso](#uso)
- [Cómo funciona](#cómo-funciona)
- [Comandos disponibles](#comandos-disponibles)
- [Solución de problemas](#solución-de-problemas)
- [Limitaciones](#limitaciones)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Historial de versiones](#historial-de-versiones)

## Stack técnico

- **Odoo 19.0** — framework, ORM y motor de reportes.
- **Python 3.10+** — modelo `sale.order` y controlador HTTP.
- **XML** — definición de la server action (`ir.actions.server`).
- **QWeb** — plantilla estándar `sale.report_saleorder`.
- **PostgreSQL** — base de datos de Odoo (el módulo no crea tablas ni campos).
- **HTTP / Werkzeug** — ruta de descarga `/sale/order/download_pdf/<id>`.

## Requisitos previos

- **Odoo 19.0** (probado en Community; no usa APIs exclusivas de Enterprise).
- **Python 3.10 o superior**, según lo requiera tu instalación de Odoo 19.
- **PostgreSQL** en la versión soportada por tu instalación de Odoo 19.
- Módulo **`sale_management`** instalado.
- Opcional: **`sale_credit_approval_gate`** para respetar el bloqueo por crédito.
- Compatible con **`wk_odoo_direct_print`**; no es necesario para funcionar.

## Instalación

1. Clona o copia el módulo en tu máquina:

   ```bash
   git clone https://github.com/ssant0/sale_order_pdf_download.git sale_order_pdf_download
   ```

2. Deja el directorio dentro de una ruta incluida en `addons_path`. Puedes enlazarlo:

   ```bash
   ln -s /ruta/a/sale_order_pdf_download /ruta/a/odoo/addons/sale_order_pdf_download
   ```

3. Confirma que el directorio padre esté en `addons_path` de tu `odoo.conf`:

   ```ini
   [options]
   addons_path = /ruta/a/odoo/addons,/ruta/a/addons
   ```

4. Instala el módulo:

   ```bash
   odoo -d <base_de_datos> -i sale_order_pdf_download --stop-after-init
   ```

   Si tu instalación usa el binario con otro nombre, el equivalente es `odoo-bin`.

5. Alternativa desde la interfaz: activa el **modo desarrollador**, ve a **Ajustes → Apps**, pulsa **Actualizar lista de aplicaciones** y busca **PDF en Órdenes de Venta**.

> [!WARNING]
> En producción, respalda la base de datos y avisa al equipo antes de instalar o actualizar: el comando reinicia Odoo al terminar.

## Variables de entorno

El módulo no define variables de entorno ni lee `os.environ`. Toda la configuración proviene de Odoo:

| Variable / clave | Descripción | Entorno | Requerida |
|---|---|---|---|
| `addons_path` (`odoo.conf`) | Debe incluir el directorio padre del módulo | Todos | Sí |
| `db_name` (`odoo.conf` o `-d`) | Base de datos donde se instala el addon | Todos | Sí |

No hay archivo `.env.example` porque no se necesitan secretos ni configuración propia.

## Uso

1. Abre **Ventas → Pedidos** y entra a una cotización **guardada**.
2. Pulsa el menú del engranaje (**Acción**) y elige **Descargar PDF**.
3. El navegador descarga el archivo:
   - `Cotizacion_<folio>.pdf` si la orden está en estado `draft` o `sent`.
   - `Pedido_<folio>.pdf` si ya está confirmada o en un estado posterior.
4. El botón **Imprimir** sigue funcionando como siempre a través de PrintDirect; esta acción solo descarga.

> [!IMPORTANT]
> La descarga trabaja sobre **una sola orden guardada**. Una orden nueva sin `id`, o varias órdenes seleccionadas desde la vista de lista, muestran un error y no generan el archivo.

Si `sale_credit_approval_gate` está instalado y la orden es a crédito sin aprobar, **Descargar PDF** muestra el error del gate y no descarga. Si el módulo no está instalado, el addon funciona de forma independiente.

## Cómo funciona

```text
data/ir_actions_server.xml
  → sale.order.action_download_pdf
  → act_url /sale/order/download_pdf/<id>
  → controllers/main.py
  → _render_qweb_pdf("sale.report_saleorder")
  → respuesta con Content-Disposition: attachment
```

- La **server action** se engancha con `binding_model_id` + `binding_type = action`, por eso aparece en el engranaje.
- El modelo valida que haya exactamente una orden, comprueba `check_access("read")` y aplica el gate de crédito si existe.
- El **controlador** es accesible por URL directa, así que repite `check_access("read")` y `_check_pdf_download_allowed()`; no usa `sudo()`.
- `_render_qweb_pdf()` devuelve la tupla `(pdf, report_type)`; el controlador desempaqueta ambos valores.
- El nombre del archivo se sanea con una regex porque los folios de Odoo contienen `/`.
- `sale_credit_approval_gate` es una dependencia blanda: se detecta con `"credit_gate_required" in self._fields` y el import de `raise_credit_blocked` es perezoso.

> [!WARNING]
> En un server action de Odoo 19 la variable `model` llega como un recordset vacío. Los ids deben resolverse desde `active_ids` / `active_id` del contexto; usar `model` provoca `Expected singleton: sale.order()`.

## Comandos disponibles

El módulo no incluye `Makefile`, `package.json`, `justfile`, tests automatizados ni linter. La verificación es manual desde el formulario.

| Comando | Para qué |
|---|---|
| `odoo -d <db> -i sale_order_pdf_download --stop-after-init` | Instalar el módulo. |
| `odoo -d <db> -u sale_order_pdf_download --stop-after-init` | Actualizar tras cambiar el código o los datos XML. |
| `odoo -d <db>` | Arrancar el servidor para probar en la interfaz. |
| `odoo -d <db> --dev=all` | Desarrollo con recarga y trazas detalladas. |

Checklist manual después de un cambio:

1. La acción aparece en el engranaje del pedido.
2. Descarga `Cotizacion_<folio>.pdf` sin enviar nada a la impresora.
3. **Imprimir** sigue usando PrintDirect.
4. Con el gate de crédito instalado: una orden a crédito sin aprobar no descarga; tras aprobarla, sí.
5. Una orden inexistente devuelve 404 y un error de permisos devuelve 403.

## Solución de problemas

| Síntoma | Causa / solución |
|---|---|
| No aparece “Descargar PDF” | El módulo no está instalado, no se actualizó la lista de apps o el usuario no tiene acceso a Ventas. |
| “Selecciona una sola orden…” | La orden es nueva sin guardar o hay varias seleccionadas en la lista. |
| Descarga vacía o error 403 | Sin permisos sobre la orden, o a crédito sin aprobar. |
| El archivo se llama `Pedido_...` | La orden ya está confirmada; es el nombre esperado. |
| No descarga y abre una pestaña | El navegador bloqueó la descarga; revisa los permisos del sitio. |
| Error `Expected singleton: sale.order()` | La server action está usando `model`; debe leer `active_ids` / `active_id`. |

## Limitaciones

- Solo descarga **una orden a la vez**, desde el formulario, y debe estar guardada.
- Usa el reporte estándar `sale.report_saleorder`; si se cambia la plantilla en el controlador, hay que actualizar también el nombre del reporte.
- No modifica `wk_odoo_direct_print` ni `sale_credit_approval_gate`.
- No define ACL propias: reutiliza las de `sale` y valida con `check_access("read")`.

## Contribuir

- Crea una rama con prefijo `feat/`, `fix/` o `docs/` y mantén el cambio acotado a un solo propósito.
- Usa mensajes de commit en formato **Conventional Commits** (`feat: ...`, `fix: ...`, `docs: ...`).
- Al cambiar comportamiento, sube la versión del manifiesto en formato `19.0.x.y.z` y agrega la entrada correspondiente en [Historial de versiones](#historial-de-versiones).
- Mantén los textos de UI, los comentarios y la descripción del manifiesto en **español**. La documentación es bilingüe: `README.md` en inglés y `README.es.md` en español; actualiza ambos al cambiar el comportamiento.
- Conserva las dos capas de validación (modelo y controlador) y el patrón de dependencia opcional con import perezoso.
- Antes de abrir el PR, ejecuta el checklist manual y describe en la descripción qué probaste.

## Licencia

Este proyecto es **código abierto y gratuito** para todos. Se distribuye bajo la **GNU Lesser General Public License v3.0 (LGPL-3.0)**.

El texto completo de la licencia está en [`LICENSE`](LICENSE); también puedes consultar el campo `license` de [`__manifest__.py`](__manifest__.py).

## Historial de versiones

- `19.0.1.0.0` — versión inicial.
- `19.0.1.0.1` — error claro cuando no hay exactamente una orden.
- `19.0.1.0.2` — obtiene los ids desde `active_ids` / `active_id`; `model` siempre viene vacío en Odoo 19.
- `19.0.1.0.3` — dependencia opcional de `sale_credit_approval_gate` y check de acceso en el controlador.
- `19.0.1.0.4` — nombre visible en Apps: **PDF en Órdenes de Venta**.
- `19.0.1.0.5` — documentación bilingüe: `README.md` en inglés y `README.es.md` en español.
