# -*- coding: utf-8 -*-

from . import models


def version_check(cr):
    from odoo.exceptions import UserError  # pylint: disable=redefined-builtin,import-outside-toplevel
    from reportlab import __version__  # pylint: disable=import-outside-toplevel
    if __version__ < '3.5.49':
        raise UserError(
            f'An earlier version of reportlab is installed: {__version__} \nVersion 3.5.49 is needed.' +  # noqa
            ' See the readme (installation) of the module for more information'
        )
    return True
