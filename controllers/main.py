import re

from odoo import http
from odoo.exceptions import AccessError, UserError
from odoo.http import request


class SaleOrderPdfDownload(http.Controller):
    @http.route(
        "/sale/order/download_pdf/<int:order_id>",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def download_pdf(self, order_id, **kwargs):
        order = request.env["sale.order"].browse(order_id).exists()
        if not order:
            return request.not_found()

        try:
            # El controlador es accesible por URL directa: sin este check,
            # cualquier usuario interno podría bajar el PDF de otra orden.
            order.check_access("read")
            order._check_pdf_download_allowed()
            pdf, _report_type = request.env["ir.actions.report"]._render_qweb_pdf(
                "sale.report_saleorder", [order.id]
            )
        except (UserError, AccessError) as exc:
            return request.make_response(
                str(exc),
                status=403,
                headers={"Content-Type": "text/plain; charset=utf-8"},
            )

        label = "Cotizacion" if order.state in ("draft", "sent") else "Pedido"
        safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", order.name or "orden")
        filename = f"{label}_{safe_name}.pdf"
        return request.make_response(
            pdf,
            headers=[
                ("Content-Type", "application/pdf"),
                ("Content-Disposition", f'attachment; filename="{filename}"'),
            ],
        )
