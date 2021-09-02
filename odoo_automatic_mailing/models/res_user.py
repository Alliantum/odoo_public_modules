from odoo import models, api


class ResPartner(models.Model):
    _inherit = "res.users"

    # os_enable_email_receivable field is declared in res.parter, but included here in the special fields, so can be modified by all internal users,
    # without being Administrator. This works like this because res.users has _inherits = {'res.partner': 'partner_id'} and odoo manage this cases in a spacial way
    @api.model
    def _register_hook(self):
        super()._register_hook()
        self.SELF_WRITEABLE_FIELDS.extend([
            'os_enable_email_receivable'
        ])
        self.SELF_READABLE_FIELDS.extend([
            'os_enable_email_receivable'
        ])
