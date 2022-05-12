# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import float_compare


class AccountInvoiceInherited(models.Model):
    _inherit = "account.move"

    # Adding our two new fields, representing the Invoicing Address and the Delivery Address respectively
    partner_invoice_id = fields.Many2one('res.partner', string="Invoice Address", change_default=True,
                                 track_visibility='always', ondelete='restrict',
                                 help="You can find a contact by its Name, TIN, Email or Internal Reference.",
                                 domain="[('id', 'child_of', partner_id)]")
    #partner_shipping_id is an existing field but we are going to let the user choose only the childs of the partner selected
    partner_shipping_id = fields.Many2one(domain="[('id', 'child_of', partner_id)]")

    @api.onchange('partner_id', 'company_id')
    def _onchange_delivery_address(self):
        """ Here we are just automating the two addresses input (delivery and invoice) to the default
        whenever the company or the partner is changed.
        This method is overwritten so we call super first and then our changes."""
        super(AccountInvoiceInherited, self)._onchange_delivery_address()
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        self.partner_invoice_id = addr and addr.get('invoice')
        self.partner_shipping_id = addr and addr.get('delivery')
        inv_type = self.type or self.env.context.get('type', 'out_invoice')
        if inv_type == 'out_invoice':
            company = self.company_id or self.env.user.company_id
            current_lang = self.partner_invoice_id.lang or self.partner_id.lang
            self.comment = company.with_context(lang=current_lang).sale_note or (
                    self._origin.company_id == company and self.comment)

    @api.onchange('partner_invoice_id', 'company_id')
    def _onchange_invoice_address(self):
        """ This method is created to make sure that the language of the Terms and
        Conditions is set according to the partner_invoice_id or company_id """
        inv_type = self.type or self.env.context.get('type', 'out_invoice')
        if inv_type == 'out_invoice':
            company = self.company_id or self.env.user.company_id
            current_lang = self.partner_invoice_id.lang or self.partner_id.lang
            self.comment = company.with_context(lang=current_lang).sale_note or (
                    self._origin.company_id == company and self.comment)

    @api.onchange('partner_id')
    def _onchange_partner_id_check(self):
        """ This is a warning feature that prevents you from setting an address instead of a customer in the customer field """
        if self.partner_id.parent_id:
            res = {}
            res['warning'] = {
                'title': _("Setting Address as a Customer"),
                'message': _(
                    "Warning. It seems like you're trying to use an Address as the main Customer of this Invoice.\n"
                    "If you didn't do it intentionally, please consider change the value of the Customer field.")
            }
            return res

    @api.model
    def _prepare_refund(self, invoice, date_invoice=None, date=None, description=None, journal_id=None):
        """ When something is added to credit note this method is called in order
        to prepare the refund data, so now we just include partner_invoice_id"""
        values = super(AccountInvoiceInherited, self)._prepare_refund(invoice, date_invoice=date_invoice, date=date, description=description, journal_id=journal_id)
        if invoice.partner_invoice_id:
            values['partner_invoice_id'] = invoice.partner_invoice_id.id
        return values


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    @api.onchange('product_id')
    def _onchange_product_id(self):
        """ This method is completely overwritten and we'll copy the
        original and just change only one line of code"""
        domain = {}
        if not self.invoice_id:
            return

        part = self.invoice_id.partner_invoice_id or self.invoice_id.partner_id  #Right here we first use our new
        # variable (partner_invoice_id) and if not the partner_id
        fpos = self.invoice_id.fiscal_position_id
        company = self.invoice_id.company_id
        currency = self.invoice_id.currency_id
        type = self.invoice_id.type

        if not part:
            warning = {
                'title': _('Warning!'),
                'message': _('You must first select a partner.'),
            }
            return {'warning': warning}

        if not self.product_id:
            if type not in ('in_invoice', 'in_refund'):
                self.price_unit = 0.0
            domain['uom_id'] = []
            # if fpos:
            #     self.account_id = fpos.map_account(self.account_id)
        else:
            self_lang = self
            if part.lang:
                self_lang = self.with_context(lang=part.lang)

            product = self_lang.product_id
            account = self.get_invoice_line_account(type, product, fpos, company)
            if account:
                self.account_id = account.id
            self._set_taxes()

            product_name = self_lang._get_invoice_line_name_from_product()
            if product_name != None:
                self.name = product_name

            if not self.uom_id or product.uom_id.category_id.id != self.uom_id.category_id.id:
                self.uom_id = product.uom_id.id
            domain['uom_id'] = [('category_id', '=', product.uom_id.category_id.id)]

            if company and currency:

                if self.uom_id and self.uom_id.id != product.uom_id.id:
                    self.price_unit = product.uom_id._compute_price(self.price_unit, self.uom_id)
        return {'domain': domain}

    def _set_taxes(self):
        """ And here we do the same as the above method"""
        self.ensure_one()

        # Keep only taxes of the company
        company_id = self.company_id or self.env.user.company_id

        if self.invoice_id.type in ('out_invoice', 'out_refund'):
            taxes = self.product_id.taxes_id.filtered(lambda r: r.company_id == company_id) or self.account_id.tax_ids or self.invoice_id.company_id.account_sale_tax_id
        else:
            taxes = self.product_id.supplier_taxes_id.filtered(lambda r: r.company_id == company_id) or self.account_id.tax_ids or self.invoice_id.company_id.account_purchase_tax_id
        # In this line at the end we change the last parameter for our variable and if not the partner_id
        self.invoice_line_tax_ids = fp_taxes = self.invoice_id.fiscal_position_id.map_tax(taxes, self.product_id, self.invoice_id.partner_invoice_id or self.invoice_id.partner_id)

        fix_price = self.env['account.tax']._fix_tax_included_price
        if self.invoice_id.type in ('in_invoice', 'in_refund'):
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if not self.price_unit or float_compare(self.price_unit, self.product_id.standard_price, precision_digits=prec) == 0:
                self.price_unit = fix_price(self.product_id.standard_price, taxes, fp_taxes)
                self._set_currency()
        else:
            self.price_unit = fix_price(self.product_id.lst_price, taxes, fp_taxes)
            self._set_currency()
