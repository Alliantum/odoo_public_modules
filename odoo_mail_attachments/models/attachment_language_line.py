from odoo import fields, models


class AttachmentLanguageLine(models.Model):
    _name = 'attachment.language.line'
    _description = 'Attachment Language Line'
    _order = 'sequence'

    sequence = fields.Integer()
    attachment_line_id = fields.Many2one('mail.attachment.line')
    attachment_id = fields.Many2one('ir.attachment', required=True, domain="[('mimetype', 'not in', ['application/javascript', 'text/css', 'text/calendar'])]")
    ref_field = fields.Char('Reference Field', default="res_partner", required=True)
    lang_id = fields.Many2one('res.lang', required=True)
