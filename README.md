# 📄 PDF on Sales Orders

**English** · [Español](README.es.md)

Download a sales order PDF from the cog menu, without going through direct printing.

[![Odoo 19](https://img.shields.io/badge/Odoo-19.0-714B67?logo=odoo&logoColor=white)](https://www.odoo.com/)
[![GitHub](https://img.shields.io/badge/GitHub-ssant0%2Fsale__order__pdf__download-181717?logo=github)](https://github.com/ssant0/sale_order_pdf_download)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-19.0.1.0.5-blue)](__manifest__.py)
[![LGPL-3 License](https://img.shields.io/badge/license-LGPL--3-blue)](LICENSE)
[![CI: manual](https://img.shields.io/badge/CI-manual-lightgrey)](#available-commands)

## Description

`PDF en Órdenes de Venta` is an Odoo 19 addon that adds a **Download PDF** action to the sales order action menu (cog). It solves the case where `wk_odoo_direct_print` (PrintDirect) sends the document to the printer and does not always let you obtain the file: this action downloads the standard `sale.report_saleorder` PDF directly. It is aimed at sales and administration teams that need the digital document without changing their printing setup.

## Table of contents

- [Description](#description)
- [Tech stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Environment variables](#environment-variables)
- [Usage](#usage)
- [How it works](#how-it-works)
- [Available commands](#available-commands)
- [Troubleshooting](#troubleshooting)
- [Limitations](#limitations)
- [Contributing](#contributing)
- [License](#license)
- [Version history](#version-history)

## Tech stack

- **Odoo 19.0** — framework, ORM and report engine.
- **Python 3.10+** — `sale.order` model and HTTP controller.
- **XML** — server action definition (`ir.actions.server`).
- **QWeb** — standard `sale.report_saleorder` template.
- **PostgreSQL** — Odoo database (the module creates no tables or fields).
- **HTTP / Werkzeug** — download route `/sale/order/download_pdf/<id>`.

## Prerequisites

- **Odoo 19.0** (tested on Community; no Enterprise-only APIs).
- **Python 3.10 or higher**, as required by your Odoo 19 installation.
- **PostgreSQL** in the version supported by your Odoo 19 installation.
- **`sale_management`** module installed.
- Optional: **`sale_credit_approval_gate`** to honor the credit block.
- Compatible with **`wk_odoo_direct_print`**; it is not required to work.

## Installation

1. Clone or copy the module to your machine:

   ```bash
   git clone https://github.com/ssant0/sale_order_pdf_download.git sale_order_pdf_download
   ```

2. Keep the directory inside a path included in `addons_path`. You can link it:

   ```bash
   ln -s /path/to/sale_order_pdf_download /path/to/odoo/addons/sale_order_pdf_download
   ```

3. Confirm the parent directory is in your `odoo.conf` `addons_path`:

   ```ini
   [options]
   addons_path = /path/to/odoo/addons,/path/to/addons
   ```

4. Install the module:

   ```bash
   odoo -d <database> -i sale_order_pdf_download --stop-after-init
   ```

   If your installation uses a different binary name, the equivalent is `odoo-bin`.

5. UI alternative: enable **developer mode**, go to **Settings → Apps**, click **Update Apps List** and search for **PDF en Órdenes de Venta**.

> [!WARNING]
> In production, back up the database and notify your team before installing or upgrading: the command restarts Odoo when it finishes.

## Environment variables

The module defines no environment variables and does not read `os.environ`. All configuration comes from Odoo:

| Variable / key | Description | Environment | Required |
|---|---|---|---|
| `addons_path` (`odoo.conf`) | Must include the module's parent directory | All | Yes |
| `db_name` (`odoo.conf` or `-d`) | Database where the addon is installed | All | Yes |

There is no `.env.example` file because no secrets or custom configuration are needed.

## Usage

1. Open **Sales → Orders** and open a **saved** quotation.
2. Click the cog menu (**Action**) and choose **Download PDF**.
3. The browser downloads the file:
   - `Cotizacion_<reference>.pdf` if the order is in `draft` or `sent` state.
   - `Pedido_<reference>.pdf` if it is confirmed or in a later state.
4. The **Print** button keeps working as usual through PrintDirect; this action only downloads.

> [!IMPORTANT]
> The download works on **a single saved order**. A new order without an `id`, or several orders selected from the list view, show an error and generate no file.

If `sale_credit_approval_gate` is installed and the order is a credit order that is not approved, **Download PDF** shows the gate error and does not download. If the module is not installed, the addon works independently.

## How it works

```text
data/ir_actions_server.xml
  → sale.order.action_download_pdf
  → act_url /sale/order/download_pdf/<id>
  → controllers/main.py
  → _render_qweb_pdf("sale.report_saleorder")
  → response with Content-Disposition: attachment
```

- The **server action** is bound with `binding_model_id` + `binding_type = action`, which is why it appears in the cog menu.
- The model checks that there is exactly one order, verifies `check_access("read")` and applies the credit gate when available.
- The **controller** is reachable by direct URL, so it repeats `check_access("read")` and `_check_pdf_download_allowed()`; it does not use `sudo()`.
- `_render_qweb_pdf()` returns the `(pdf, report_type)` tuple; the controller unpacks both values.
- The file name is sanitized with a regex because Odoo references contain `/`.
- `sale_credit_approval_gate` is a soft dependency: it is detected with `"credit_gate_required" in self._fields` and the `raise_credit_blocked` import is lazy.

> [!WARNING]
> In an Odoo 19 server action the `model` variable arrives as an empty recordset. Ids must be resolved from the context's `active_ids` / `active_id`; using `model` raises `Expected singleton: sale.order()`.

## Available commands

The module ships no `Makefile`, `package.json`, `justfile`, automated tests or linter. Verification is manual from the form.

| Command | Purpose |
|---|---|
| `odoo -d <db> -i sale_order_pdf_download --stop-after-init` | Install the module. |
| `odoo -d <db> -u sale_order_pdf_download --stop-after-init` | Upgrade after changing code or XML data. |
| `odoo -d <db>` | Start the server to test in the UI. |
| `odoo -d <db> --dev=all` | Development with reload and detailed traces. |

Manual checklist after a change:

1. The action appears in the order's cog menu.
2. It downloads `Cotizacion_<reference>.pdf` without sending anything to the printer.
3. **Print** still uses PrintDirect.
4. With the credit gate installed: an unapproved credit order does not download; after approval it does.
5. A nonexistent order returns 404 and a permission error returns 403.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| "Download PDF" does not appear | The module is not installed, the apps list was not refreshed, or the user has no access to Sales. |
| "Select a single order…" | The order is new and unsaved, or several are selected in the list. |
| Empty download or 403 error | No permission on the order, or an unapproved credit order. |
| The file is named `Pedido_...` | The order is already confirmed; this is the expected name. |
| Nothing downloads and a tab opens | The browser blocked the download; check the site permissions. |
| `Expected singleton: sale.order()` error | The server action is using `model`; it must read `active_ids` / `active_id`. |

## Limitations

- It only downloads **one order at a time**, from the form, and the order must be saved.
- It uses the standard `sale.report_saleorder` report; if the template is changed in the controller, the report name must be updated too.
- It does not modify `wk_odoo_direct_print` or `sale_credit_approval_gate`.
- It defines no ACLs of its own: it reuses those of `sale` and validates with `check_access("read")`.

## Contributing

- Create a branch prefixed with `feat/`, `fix/` or `docs/` and keep the change scoped to a single purpose.
- Use **Conventional Commits** messages (`feat: ...`, `fix: ...`, `docs: ...`).
- When changing behavior, bump the manifest version in `19.0.x.y.z` format and add the matching entry to [Version history](#version-history).
- Keep **UI texts, code comments and the manifest description in Spanish**. Documentation is bilingual: `README.md` in English and `README.es.md` in Spanish; update both when behavior changes.
- Preserve the two validation layers (model and controller) and the soft-dependency pattern with a lazy import.
- Before opening the PR, run the manual checklist and describe what you tested in the description.

## License

This project is **open source and free** for everyone. It is distributed under the **GNU Lesser General Public License v3.0 (LGPL-3.0)**.

The full license text is in [`LICENSE`](LICENSE); you can also check the `license` field of [`__manifest__.py`](__manifest__.py).

## Version history

- `19.0.1.0.0` — initial version.
- `19.0.1.0.1` — clear error when there is not exactly one order.
- `19.0.1.0.2` — gets ids from `active_ids` / `active_id`; `model` is always empty in Odoo 19.
- `19.0.1.0.3` — optional `sale_credit_approval_gate` dependency and access check in the controller.
- `19.0.1.0.4` — visible name in Apps: **PDF en Órdenes de Venta**.
- `19.0.1.0.5` — bilingual documentation: `README.md` in English and `README.es.md` in Spanish.
