# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    display_assign_serial = fields.Boolean(compute='_compute_display_assign_serial')
    next_serial = fields.Char('First SN')
    next_serial_count = fields.Integer('Number of SN')

    # This show the wizard when clicking the Lines button
    def action_show_details(self):
        """Returns an action that will open a form view (in a popup) allowing to work on all the
        move lines of a particular move. This form view is used when "show operations" is not
        checked on the picking type.
        """
        self.ensure_one()

        # If "show suggestions" is not checked on the picking type, we have to filter out the
        # reserved move lines. We do this by displaying `move_line_nosuggest_ids`. We use
        # different views to display one field or another so that the webclient doesn't have to
        # fetch both.
        if self.picking_id.picking_type_id.show_reserved:
            view = self.env.ref('odoo_serial_generator.view_stock_move_operations_serials')
        else:
            view = self.env.ref('stock.view_stock_move_nosuggest_operations')

        picking_type_id = self.picking_type_id or self.picking_id.picking_type_id
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'stock.move',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
                self.env.context,
                show_owner=self.picking_type_id.code != 'incoming',
                show_lots_m2o=self.has_tracking != 'none' and (picking_type_id.use_existing_lots or
                                                               self.state == 'done' or
                                                               self.origin_returned_move_id.id),
                # able to create lots, whatever the value of ` use_create_lots`.
                show_lots_text=self.has_tracking != 'none' and picking_type_id.use_create_lots and not picking_type_id.use_existing_lots and self.state != 'done' and not self.origin_returned_move_id.id,
                show_source_location=self.picking_type_id.code != 'incoming',
                show_destination_location=self.picking_type_id.code != 'outgoing',
                show_package=not self.location_id.usage == 'supplier',
                show_reserved_quantity=self.state != 'done' and not self.picking_id.immediate_transfer and self.picking_type_id.code != 'incoming'
            ),
        }

    @api.depends('has_tracking', 'picking_type_id.use_create_lots', 'picking_type_id.use_existing_lots',
                 'picking_type_id.show_reserved', 'picking_type_id.show_operations')
    def _compute_display_assign_serial(self):
        """Set `display_assing_serial` according to the move and picking type settings"""
        for move in self:
            move.display_assign_serial = (
                move.has_tracking == 'serial' and
                move.state in ('partially_available', 'assigned', 'confirmed') and
                move.picking_type_id.use_create_lots and
                not move.picking_type_id.use_existing_lots and
                not move.picking_type_id.show_reserved
            )

    def action_assign_serial_show_details(self):
        """On `self.move_line_ids`, assign `lot_name` according to
        `self.next_serial` before returning `self.action_show_details`.
        """
        self.ensure_one()
        if not self.next_serial:
            raise UserError(_("You need to set a Serial Number before generating more."))
        self._generate_serial_numbers()
        return self.action_show_details()

    def _generate_serial_numbers(self, next_serial_count=False):
        """This method will generate `lot_name` from a string (field
        `next_serial`) and create a move line for each generated `lot_name`.
        """
        self.ensure_one()

        if not next_serial_count:
            next_serial_count = self.next_serial_count
        # We look if the serial number contains at least one digit.
        caught_initial_number = re.findall(r"\d+", self.next_serial)
        if not caught_initial_number:
            raise UserError(_('The serial number must contain at least one digit.'))
        # We base the serie on the last number find in the base serial number.
        initial_number = caught_initial_number[-1]
        padding = len(initial_number)
        # We split the serial number to get the prefix and suffix.
        splitted = re.split(initial_number, self.next_serial)
        prefix = splitted[0]
        suffix = splitted[1]
        initial_number = int(initial_number)

        move_lines_commands = []
        location_dest = self.location_dest_id.get_putaway_strategy(self.product_id) or self.location_dest_id
        for i in range(0, next_serial_count):
            lot_name = '%s%s%s' % (
                prefix,
                str(initial_number + i).zfill(padding),
                suffix
            )
            move_lines_commands.append((0, 0, {
                'lot_name': lot_name,
                'qty_done': 1,
                'product_id': self.product_id.id,
                'product_uom_id': self.product_id.uom_id.id,
                'location_id': self.location_id.id,
                'location_dest_id': location_dest.id,
                'picking_id': self.picking_id.id,
            }))
        self.write({'move_line_ids': move_lines_commands})
        return True

    def action_assign_serial(self):
        """Opens a wizard to assign SN's name on each move lines."""
        self.ensure_one()
        action = self.env.ref('odoo_serial_generator.act_assign_serial_numbers').read()[0]
        action['context'] = {
            'default_product_id': self.product_id.id,
            'default_move_id': self.id,
        }
        return action

    def _action_assign(self):
        """On automatic assignation of reserved quants, it will
        update the next_serial_count for the just remaining quantities
        """
        super(StockMove, self)._action_assign()
        for move in self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available']):
            if move.product_id.tracking == 'serial':
                move.next_serial_count = move.product_uom_qty
