odoo.define('odoo_insert_line_position.BasicModel', function (require) {
"use strict";

    var BasicModel = require('web.BasicModel');

    BasicModel.include({
        _getNewLineIndex: function (list, position, params) {
            if (params.context && params.context.index !== undefined) {
                return params.context.index;
            }
            return list.offset + (position !== 'top' ? list.limit : 0);
        },

        _makeDefaultRecord: function (modelName, params) {
            if (params.context.avoid_override_position) {
                params.position = 'insert';
            }
            return this._super.apply(this, arguments);
        },

        _computeOverrideDefaultFields: function (listID, position) {
            if (position == 'insert') {
                return false;
            }
            return this._super.apply(this, arguments);
        },

        _addX2ManyDefaultRecord: function (list, options) {
            var self = this;
            var position = options && options.position || 'top';
            var params = {
                fields: list.fields,
                fieldsInfo: list.fieldsInfo,
                parentID: list.id,
                position: position,
                viewType: list.viewType,
                allowWarning: options && options.allowWarning
            };

            var additionalContexts = options && options.context;
            var makeDefaultRecords = [];
            if (additionalContexts){
                _.each(additionalContexts, function (context) {
                    params.context = self._getContext(list, {additionalContext: context});
                    makeDefaultRecords.push(self._makeDefaultRecord(list.model, params));
                });
            } else {
                params.context = self._getContext(list);
                makeDefaultRecords.push(self._makeDefaultRecord(list.model, params));
            }

            return $.when.apply($, makeDefaultRecords).then(function (){
                var ids = [];
                _.each(arguments, function (id){
                    ids.push(id);

                    list._changes.push({operation: 'ADD', id: id, position: position, isNew: true});
                    var record = self.localData[id];
                    list._cache[record.res_id] = id;
                    if (list.orderedResIDs) {
                        // Here is the moment where we can decide where we want our new line to be inserted
                        var index = self._getNewLineIndex(list, position, params)
                        list.orderedResIDs.splice(index, 0, record.res_id);
                        // list could be a copy of the original one
                        self.localData[list.id].orderedResIDs = list.orderedResIDs;
                    }
                });

                return ids;
            });
        },

    })

});
