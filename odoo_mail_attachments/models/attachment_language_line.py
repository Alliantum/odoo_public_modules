from odoo import fields, models, api

@api.model
def _lang_get(self):
    return self.env['res.lang'].get_installed()



class AttachmentLanguageLine(models.Model):
    _name = 'attachment.language.line'
    _description = 'Attachment Language Line'
    _order = 'sequence'

    sequence = fields.Integer()
    attachment_line_id = fields.Many2one('mail.attachment.line')
    attachment_id = fields.Many2one('ir.attachment', required=True, domain="[('mimetype', 'not in', ['application/javascript', 'text/css', 'text/calendar'])]")
    ref_field = fields.Char('Reference Field', default="res_partner", required=True)
    lang = fields.Selection(_lang_get, string='Language', default=lambda self: self.env.lang, required=True)
