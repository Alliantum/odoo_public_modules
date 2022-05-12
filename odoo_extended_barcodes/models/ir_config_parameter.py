from odoo import api, models



class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def set_concat_param(self, key, value):
        """Sets or concatenate the value of a parameter.

        :param string key: The key of the parameter value to set.
        :param string value: The value to set.
        :return: the previous value of the parameter or False if it did
                 not exist.
        """
        param = self.search([('key', '=', key)])
        if param:
            old = param.value
            if value is not False and value is not None:
                new_value = set(old.split(',')) | set(value.split(','))
                param.write({'value': ','.join(new_value).strip(',')})
            else:
                param.unlink()
            return old
        else:
            if value is not False and value is not None:
                self.create({'key': key, 'value': value})
            return False

