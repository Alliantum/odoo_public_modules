from odoo import models, api
from odoo.tools.safe_eval import safe_eval


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        value = super(MailComposer, self).onchange_template_id(template_id, composition_mode, model, res_id)
        # This method will return the same 'value' variable, but updated with the pdf reports that were dynamically generated
        return self.env['mail.attachment.line'].add_dynamic_reports(self, value)

    def get_dynamic_attachments(self, report, base64_pdf, report_record_ids):
        attachment_ids = self.env['ir.attachment']
        for report_record_id in report_record_ids:
            if report.print_report_name:
                report_name = safe_eval(report.print_report_name, {'object': report_record_id})
            elif report.attachment:
                report_name = safe_eval(report.attachment, {'object': report_record_id})
            else:
                report_name = 'Document'
            filename = "%s.%s" % (report_name, "pdf")
            attachment_ids += self.env['ir.attachment'].create({
                'name': filename,
                'type': 'binary',
                'datas': base64_pdf,
                'store_fname': report.report_file,
                'res_model': self.model,
                'res_id': self.res_id,
                'mimetype': 'application/pdf'
            })
        return attachment_ids
