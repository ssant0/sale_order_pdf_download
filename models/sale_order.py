from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _pdf_download_credit_blocked(self):
        """True solo si el gate de crédito está instalado y bloquea la orden."""
        if "credit_gate_required" not in self._fields:
            return False
        return bool(
            self.credit_gate_required and self.credit_gate_state != "approved"
        )

    def _check_pdf_download_allowed(self):
        """Aplica el gate de crédito si está instalado; si no, no hace nada."""
        if not self._pdf_download_credit_blocked():
            return
        # Import perezoso: el módulo de crédito es opcional.
        from odoo.addons.sale_credit_approval_gate.models.credit_gate import (
            raise_credit_blocked,
        )

        raise_credit_blocked(self.env, self, _("descargar"))

    def action_download_pdf(self):
        """Devuelve una URL de descarga; el PDF se genera en el controlador."""
        if len(self) != 1:
            raise UserError(_(
                "Selecciona una sola orden de venta y guárdala antes de "
                "descargar el PDF."
            ))
        self.check_access("read")
        self._check_pdf_download_allowed()
        return {
            "type": "ir.actions.act_url",
            "url": f"/sale/order/download_pdf/{self.id}",
            "target": "self",
        }
