from urllib.parse import urlparse, parse_qs
from odoo import api, models
from reportlab.graphics.barcode import createBarcodeImageInMemory
import base64



class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    # All this code is based on the original method to produce barcodes
    @api.model
    def reportlab_svg_barcode(self, type='', value='', width=300, height=30, humanreadable=0, **kwargs):
        """ Create a SVG barcode image.
            This method named is though to follow the patter 'barcode.library_svg_barcode'
        Returns a base64 svg image ready to put it on a `src` attribute of an `<img>` tag
        """
        if type == 'UPCA' and len(value) in (11, 12, 13):
            type = 'EAN13'
            if len(value) in (11, 12):
                value = '0%s' % value
        try:
            width, height, humanreadable = int(width), int(height), bool(int(humanreadable))
            rst = createBarcodeImageInMemory(type, value=value, format='svg', width=width, height=height,
                humanreadable=humanreadable)
            e = base64.b64encode(bytes(rst, 'ascii'))
            return 'data:image/svg+xml;base64,' + e.decode('utf-8')
        except (ValueError, AttributeError):
            if type == 'Code128':
                raise ValueError("Cannot convert into svg barcode.")
            else:
                return self.svg_barcode('Code128', value, width=width, height=height, humanreadable=humanreadable)

    @api.model
    def get_svg_barcode(self, **kwargs):
        # looking for modules extending the default type of barcodes, they should concatenate values into this system parameter, that later will be used to call dynamically the method required to manage this kind of barcode
        barcodes_extended_libraries = self.env['ir.config_parameter'].sudo().get_param('barcodes.extended_libraries')
        if barcodes_extended_libraries:
            for barcode_library in barcodes_extended_libraries.split(','):
                # trying with every library before fall back to reportlab
                if hasattr(self, f'{barcode_library}_svg_barcode'):
                    barcode_value = getattr(self, f'{barcode_library}_svg_barcode')(**kwargs)
                    if barcode_value:
                        return barcode_value
        # if our barcode is not yet generated, we always fallback to reportlab, which is the library used by default in Odoo
        return self.reportlab_svg_barcode(**kwargs)



class IrQWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    # with this method we automate the rendering proccess to change all the regular barcodes to the customs svg
    def _compile_node(self, el, options):
        # this is just working for urls of the shape '/report/barcode?params' but not those like '/report/barcode/<type>/<path:value>'. Also the param values must be interpolated using the % symbol. For the rest os cases, we leave Odoo does as usual
        if el.tag == "img" and any(att == 't-att-src' and el.attrib[att].startswith("'/report/barcode/?") and (' % ' in el.attrib[att]) for att in el.attrib):
            barcode_before = el.attrib.pop('t-att-src')
            [url, args] = barcode_before.split(' % ')

            keys = parse_qs(urlparse(url).query)
            vals = [val.strip() for val in args.strip('(').strip(')').split(',')]
            kwargs_string = ''
            for key, val in zip(keys, vals):
                kwargs_string += f'{key}={val}, '
            # remove trailing ', ' after concatenating
            kwargs_string = kwargs_string.strip(', ')

            if 'type' in keys and 'value' in keys and "humanreadable=1" not in barcode_before:
                el.set('t-att-src', f"request.env['ir.actions.report'].get_svg_barcode({kwargs_string})")
            else:
                el.set('t-att-src', barcode_before)
        return super(IrQWeb, self)._compile_node(el, options)
