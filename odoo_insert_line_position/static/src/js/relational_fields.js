odoo.define('odoo_insert_line_position.relational_fields', function (require) {
"use strict";


    const FieldOne2Many = require('web.relational_fields').FieldOne2Many;

    FieldOne2Many.include({
        /**
         * @override
         */
        init: function () {
            this._super.apply(this, arguments);
            const arch = this.view && this.view.arch;
            if (arch) {
                this.activeActions.insert = arch.attrs.insert ? JSON.parse(arch.attrs.insert) : false;
            }
        },

        _getInsertedRowIndex: function (line) {
            return this.value.data.findIndex(item => item.id === line.value.id)
        }

    });

});
