import werkzeug
import pyzint
import base64
from odoo import api, models



class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    @api.model
    def pyzint_svg_barcode(self, type='', value='', height=30, scale=1.0, **kwargs):
        if hasattr(pyzint.Barcode, type):
            try:
                symbol = getattr(pyzint.Barcode, type)(value, height=int(height), scale=float(scale)) # width is not a valid argument for pyzint, but generally you can use css styles for this
                e = base64.b64encode(symbol.render_svg()[137:])
                return 'data:image/svg+xml;base64,' + e.decode('utf-8')
            except (ValueError, AttributeError):
                raise werkzeug.exceptions.HTTPException(description='Cannot convert into barcode.')
