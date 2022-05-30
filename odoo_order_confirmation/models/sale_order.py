# -*- encoding: utf-8 -*-

from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    was_stock_approved = fields.Boolean('Stock Approved', readonly=True, default=False)

    @api.model
    def _setup_fields(self):
        """Add the `stock_to_approve` status"""
        super(SaleOrder, self)._setup_fields()
        selection = self._fields['state'].selection
        exists = False
        for idx, (state, __) in enumerate(selection):
            if state == 'stock_to_approve':
                exists = True
        if not exists:
            selection.insert(0, ('stock_to_approve', _('Stock Confirmation')))

    @api.multi
    def needs_confirmation(self):
        """Check if the sale order needs to be approved"""
        if any(self.order_line.mapped('blocking')):
            return True
        return False

    def _block_sale_order(self):
        """Block the Sale Order and send a message to the Stock Managers"""
        self.state = 'stock_to_approve'
        odoobot_id = self.env['ir.model.data'].xmlid_to_res_id("base.partner_root")
        stock_managers = self.env.user.company_id.stock_warning_notify
        if stock_managers:
            for stock_manager in stock_managers:
                note = '<p>One or more of the products in this Sale Order ({}) has exceeded the limit on big sales.</p>' \
                       '<p>Lines are the following:</p>' \
                       '<ul>'.format(self.name)
                for line in self.order_line.filtered(lambda r: r.blocking is True):
                    note += '<li>{} {} {}</li>'.format(line.name, line.product_uom_qty, line.product_uom.name)
                note += '</ul>'
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_warning').id,
                    'summary': 'Sale Order {} needs confirmation'.format(self.name),
                    'note': note,
                    'user_id': stock_manager.id,
                    'res_id': self.id,
                    'res_model_id': self.env.ref('sale.model_sale_order').id,
                    'automated': True,
                    'create_user_id': odoobot_id,
                    'is_stock_confirmation': True,
                })
        else:
            for user in self.env.ref('stock.group_stock_manager').users:
                if user.partner_id:
                    channel_id = self.sudo(user.id).env['mail.channel'].search([('name', '=', 'OdooBot')], limit=1)
                    message = "<p>One or more of the products in this Sale Order ({}) has exceeded the limit on big sales.<br/>" \
                              "However, at this moment there's no reposible assigned to manage this kind of situation, so the sale order will stay locked.</p>" \
                              "<p>Please, be ware that it's very important to set some responsible in Sales/Configuration/Settings/Warning/Create activity for solve this problem.</p>".format(self.name)
                    if not channel_id:
                        channel_id = self.env['mail.channel'].with_context({"mail_create_nosubscribe": True}).create({
                            'channel_partner_ids': [(4, odoobot_id, False), (4, user.partner_id.id, False)],
                            'public': 'private',
                            'channel_type': 'chat',
                            'email_send': False,
                            'name': 'OdooBot'
                        })
                    channel_id.sudo().message_post(body=message,
                                                   author_id=odoobot_id,
                                                   message_type="comment",
                                                   subtype="mail.mt_comment")

    @api.multi
    def warning_action_confirm(self):
        """Check if the sale order can be confirmed"""
        if self.needs_confirmation():
            self._block_sale_order()
            return False
        return self.action_confirm()

    @api.model
    def create(self, vals):
        """Check if the sale order needs confirmation before creating it"""
        sale = super(SaleOrder, self).create(vals)
        if sale.needs_confirmation():
            sale._block_sale_order()
        return sale

    @api.multi
    def action_stock_approve(self):
        """Approve the sale order and set it's state to draft"""
        self.sudo().order_line.write({
            'blocking': False,
        })  # Sudo used here because maybe user doing this task doesn't have any permission on sale order or lines.
        stock_activity_ids = self.env['mail.activity'].search([('res_id', '=', self.id), ('res_model_id', '=', self.env.ref('sale.model_sale_order').id)])
        if stock_activity_ids:
            stock_activity_ids.action_done()
        self.sudo().write({'state': 'draft', 'was_stock_approved': True})


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    blocking = fields.Boolean('Blocking')

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        """Check the quantity as well as the product's uom in order to apply the limits"""
        res = super(SaleOrderLine, self)._onchange_product_id_check_availability()
        if self.product_id and self.product_id.type == 'product':
            need_check_warning = self.env['ir.config_parameter'].sudo().get_param('odoo_order_confirmation.percentage_warning')
            if need_check_warning:
                if self.product_id.uom_id.category_id.id in [1, 2]:  # Units and Weight
                    qty = self.product_uom_qty
                    if self.product_id.uom_id.category_id.id == 1:
                        ref_unit = self.env['uom.uom'].browse(1)
                        if self.product_uom.id != 1:  # Not Units, maybe Dozens or whatever
                            qty = self.product_uom._compute_quantity(qty, ref_unit)
                        limit = self.env['ir.config_parameter'].sudo().get_param('odoo_order_confirmation.units_onsale_warning')
                    else:
                        ref_unit = self.env['uom.uom'].browse(3)
                        if self.product_uom.id != 3:  # Not Kg, maybe g or whatever
                            qty = self.product_uom._compute_quantity(qty, ref_unit)
                        limit = self.env['ir.config_parameter'].sudo().get_param('odoo_order_confirmation.kg_onsale_warning')
                    if limit:
                        limit = float(limit)
                    if qty > limit:
                        message = _("Selling {} {} of {} exceeds the limit for this product, which is set to {} {}.\n\n"
                                    "If you save or confirm this sale order with the present amounts, it will remain blocked until one of the stock managers"
                                    " will confirm it.").format(self.product_uom_qty, self.product_uom.name, self.product_id.name, limit, ref_unit.name)
                        if res.get('warning', False) and res['warning'].get('message', False):
                            message += '\n\n' + res['warning'].get('message')
                        warning_mess = {
                            'title': _('Limit on SO quantities surpassed!'),
                            'message': message
                        }
                        self.blocking = True
                        return {'warning': warning_mess}

        self.blocking = False
        return res
