# -*- encoding: utf-8 -*-

from odoo import models, api, exceptions


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        """If there's a block on the parent, it'll take precedence"""
        if self.partner_id and self.partner_id.picking_warn:
            if self.partner_id.picking_warn == 'no-message' and self.partner_id.parent_id:
                partner = self.partner_id.parent_id
            elif self.partner_id.picking_warn not in ('no-message', 'block') and self.partner_id.parent_id.picking_warn == 'block':
                partner = self.partner_id.parent_id
            else:
                partner = self.partner_id
            if partner.picking_warn != 'no-message':
                if partner.picking_warn == 'block':
                    raise exceptions.ValidationError(partner.picking_warn_msg)
        return super(StockPicking, self).button_validate()

    def check_amounts(self):
        """Checks the amount of product sold and the amount of product being picked from the stock,
        and sets the sale status to `Warning` if is not enough"""
        self.ensure_one()

        order_product_amounts = {}
        deliveries_products_amounts = {}
        for line in self.sale_id.order_line:
            if line.product_id.type != 'service' and line.product_uom_qty > 0:
                if not order_product_amounts.get(line.product_id.id):
                    order_product_amounts[line.product_id.id] = [line.product_uom_qty, line.product_uom.name]
                else:
                    order_product_amounts[line.product_id.id][0] += line.product_uom_qty

        sale_deliveries = self.env['stock.picking'].search([('sale_id', '=', self.sale_id.id), ('state', '!=', 'cancel')])
        if sale_deliveries:
            for delivery in sale_deliveries:
                for line in delivery.move_ids_without_package:
                    if line.product_id.type != 'service':
                        if not deliveries_products_amounts.get(line.product_id.id):
                            deliveries_products_amounts[line.product_id.id] = line.product_uom_qty
                        else:
                            deliveries_products_amounts[line.product_id.id] += line.product_uom_qty

        missing_quants = False
        missing_quants_list = []
        for product_id, amount in order_product_amounts.items():
            if deliveries_products_amounts.get(product_id):
                if order_product_amounts.get(product_id) and order_product_amounts.get(product_id)[0] > deliveries_products_amounts.get(product_id):
                    diff = order_product_amounts[product_id][0] - deliveries_products_amounts.get(product_id)
                    self.sale_id.state = 'warning'
                    missing_quants = True
                    product_info = self.env['product.product'].browse(product_id)
                    if product_info:
                        missing_quants_list.append((product_info.name or '') + " " + (product_info.default_code or '') + ": " + str(diff) + ' ' + amount[1])
            else:
                self.sale_id.state = 'warning'
                missing_quants = True
                product_info = self.env['product.product'].browse(product_id)
                if product_info:
                    missing_quants_list.append((product_info.name or '') + " " + (product_info.default_code or '') + ": " + str(amount[0]) + ' ' + amount[1])

        message_text = ""
        if missing_quants_list:
            for line in missing_quants_list:
                message_text += line + '\n'

        return (missing_quants, message_text)

    def action_cancel(self):
        """Update the sale status when cancelling"""
        for picking in self:
            result = super(StockPicking, picking).action_cancel()
            if picking.sale_id:
                picking.check_amounts()
            return result

    @api.model
    def create(self, vals):
        """Set or update the sale status when creating"""
        res = super(StockPicking, self).create(vals)
        if res.sale_id:
            res.check_amounts()
        return res

    def unlink(self):
        """Update the sale status when deleting"""
        sale_ids = []
        for picking in self:
            if picking.sale_id and picking.state != 'cancel':
                sale_ids.append(picking.sale_id)
        res = super(StockPicking, self).unlink()
        for sale in sale_ids:
            picking_id = self.search([('sale_id', '=', sale.id)], limit=1)
            if picking_id:
                picking_id.check_amounts()
        return res
