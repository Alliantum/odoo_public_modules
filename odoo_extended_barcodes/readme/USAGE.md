To use this module, it's recommended to follow the approach below:

 - First, make a list of all the current barcodes you plan to replace by new kinds of barcodes included in this module. Then note, inside which existing Odoo modules they are currently.

 - Then, create a new Odoo module. In the `__manifest__.py` set it as `'auto_install': True`

 - Also in the `__manifest__.py`, edit the `'depends': []` key and add `odoo_extended_barcodes` followed by all your installed modules where you previously has noticed there are barcodes you want to modify.

- Finally, all you need to do, is inherit the templates where your target barcodes are used, by using the odoo's xpath mechanism, and modify what's needed. Normally all you may need to change is the `t-att-src` of the `<img>` tags that frequently are used to locate the barcode that's going to be rendered inside a given template.

    For example, if you have something like this in a `your_template` `<template>` record:

        <t t-if="o.product_id.whatever">
            <div class="position-absolute" style="bottom: 0px;">
                <img class="h-100" t-att-src="'/report/barcode/?type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % ('Code128', o.product_id.default_code, 9000, 1100)" alt="Barcode"/>
            </div>
        </t>

    all you need to do is:

        <template id="your_template" inherit_id="module.your_template">
            <xpath expr="//img" position="attributes">
                <attribute name="t-att-src">'/report/barcode/?type=%s&amp;value=%s&amp;scale=%s&amp;height=%s' % ('DATAMATRIX', o.product_id.default_code, 5, 1100)</attribute>
            </xpath>
        </template>

Then, instead a traditional **Code128** barcode, you will end up with something as beautiful as this:

<div align="center" style="margin: 2rem;">
    <img src="./static/description/little_label_example.png" width="40%" style="border-radius: 5px;">
</div>
