import datetime
import time
import dateutil
from odoo import fields, models
from odoo.tools.safe_eval import safe_eval


class AutomaticMailingRule(models.Model):
    _name = 'automatic.mailing.rule'
    _description = 'Automatic Mailing Rule'
    _order = 'sequence,model_id'

    sequence = fields.Integer()
    company_id = fields.Many2one('res.company', required=True, ondelete="cascade")
    model_id = fields.Many2one('ir.model', string='Apply On', required=True, ondelete="cascade", domain="[('model', 'in', ['sale.order', 'account.move'])]")
    model_name = fields.Char(related="model_id.model")
    filter_model_id = fields.Char(string="Apply On", help="Extended filtering option to trigger the line for this model.")
    template_id = fields.Many2one('mail.template', string="Mail Template", required=True)

    def _get_eval_context(self):
        """ Prepare the context used when evaluating python code
            :returns: dict -- evaluation context given to safe_eval
        """
        return {
            'datetime': datetime,
            'dateutil': dateutil,
            'time': time,
            'uid': self.env.uid,
            'user': self.env.user,
        }

    def _pass_filter(self, records):
        """ Filter the records that satisfy the precondition of action ``self``. """
        if self.filter_model_id and records:
            domain = [('id', 'in', records.ids)] + safe_eval(self.filter_model_id, self._get_eval_context())
            return records.search(domain)
        else:
            return records
