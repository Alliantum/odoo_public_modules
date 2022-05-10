odoo.define('odoo_insert_line_position.InsertableListRenderer', [
    'web.core',
    'web.dom',
    'web.ListRenderer',
    'web.EditableListRenderer'
], function (require) {

    var core = require('web.core');
    var dom = require('web.dom');
    var ListRenderer = require('web.ListRenderer');

    var _t = core._t;

    ListRenderer.include({
        events: _.extend({}, ListRenderer.prototype.events, {
            'mouseenter tr.o_data_row': '_onHoverRowEnter',
            'mouseleave tr.o_data_row': '_onHoverRowLeave',
            'click td.all_insert_cell': '_onInsertLine'
        }),

        /**
         * @constructor
         * @param {Widget} parent
         * @param {any} state
         * @param {Object} params
         * @param {boolean} params.hasSelectors
         */
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            this.parent = parent;
            this.renderInsertLine = parent.mode === 'edit' && parent.activeActions && parent.activeActions.insert ? true : false;
        },

        _onHoverRowEnter: function (ev) {
            if (
                this.renderInsertLine &&
                ev.currentTarget.nextSibling &&
                ev.currentTarget.nextSibling.firstChild &&
                !this._isLastInsertRow(ev.currentTarget)
            ) {
                ev.currentTarget.nextSibling.firstChild.style = "height: 0.5rem;";
            }
        },

        _onHoverRowLeave: function (ev) {
            if (
                this.renderInsertLine &&
                ev.currentTarget.nextSibling &&
                ev.currentTarget.nextSibling.firstChild &&
                !this._isLastInsertRow(ev.currentTarget)
            ) {
                ev.currentTarget.nextSibling.firstChild.style = "";
            }
        },

        // Avoid to show any option to insert under the last line
        _isLastInsertRow: function (rowElement) {
            var nextInsertFound = false;
            rowElement = rowElement.nextElementSibling;
            while (!nextInsertFound && rowElement && (rowElement.classList.contains('all_insert_row') || rowElement.classList.contains('o_data_row'))) {
                rowElement = rowElement.nextElementSibling;
                if (rowElement.className === 'all_insert_row') {
                    nextInsertFound = true;
                }
            }
            return !nextInsertFound;
        },

        /**
         * @override
         * @private
         */
        _getRecordID: function (rowIndex) {
            var $tr;
            if (this.nextIndex) {
                $tr = this.$('table.o_list_table > tbody > tr').not('.all_insert_row').eq(rowIndex);
            } else {
                $tr = this.$('table.o_list_table > tbody > tr').eq(rowIndex);
            }
            return $tr.data('id');
        },

        /**
         * @override
         */
        editRecord: function (recordID) {
            // And we need this, to focus edition on the new created line, at the correct position
            var rowIndex;
            if (this.nextIndex) {
                rowIndex = this.nextIndex;
            } else {
                var $row = this._getRow(recordID);
                rowIndex = $row.prop('rowIndex') - 1;
            }
            return this._selectCell(rowIndex, 0);
        },

        /**
         * @override
         * @private
         */
        _onCellClick: function (event) {
            this.nextIndex = null;
            this._super.apply(this, arguments);
        },

        _onInsertLine: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var context = ev.currentTarget.dataset.context && ev.currentTarget.dataset.context || {};
            if (this.renderInsertLine && ev.currentTarget.dataset.nextIndex) {
                this.el.className += " hideHandlers";
                // We save the nextIndex as a class variable. It will be used by the list_editable_renderer.js.
                // Also this value in the context too, so ca be read by the basic_model.js
                context.index = this.nextIndex = parseInt(ev.currentTarget.dataset.nextIndex);
                if (ev.currentTarget.dataset.handleField) {
                    _.extend(context, {
                        [`default_${ev.currentTarget.dataset.handleField}`]: parseInt(ev.currentTarget.dataset.sequence),
                        avoid_override_position: true
                    });
                }
            }
            // but we do want to unselect current row
            var self = this;
            this.unselectRow().then(function () {
                // This is triggering the method '_onAddRecord' in the relational_fields.js in /web/src/js/fields.js
                self.trigger_up('add_record', {
                    context:[context]
                });
            });
        },

        _renderInsertRow: function (record, i) {
            // When creating a new record, for example a SO with many lines inside, before saving it, its lines will have all the same sequence
            // and we don't want this, because if someone insert a line, and all the lines have the same sequence,
            // that line will lost its position and will go to the bottom because of having a bigger sequence.
            if (!this.parent.res_id && !this.initialSequenceReset) {
                var rows = this.state.data;
                var order = _.findWhere(this.state.orderedBy, {name: this.handleField});
                var asc = !order || order.asc;

                var sequences = _.pluck(_.pluck(rows, 'data'), this.handleField);
                var rowIDs = _.pluck(rows, 'id');

                if (!asc) {
                    rowIDs.reverse();
                }
                this.trigger_up('resequence', {
                    rowIDs: rowIDs,
                    offset: _.min(sequences),
                    handleField: this.handleField,
                });
                this.initialSequenceReset = true;
            }
            var $tr;
            if ( this.renderInsertLine ) {
                // Adding the "Insert Line" element
                var $td = $('<td/>', {
                    class: 'all_insert_cell',
                    colspan: '99',
                    'data-next-index': i + 1,
                    'data-handle-field': this.hasHandle && this.handleField || '',
                    'data-sequence': this.hasHandle && record.data[this.handleField]
                }).append(
                    $("<div style='width: 1rem; display: inline-block' ><i class='fa fa-arrow-right all_insert_cell_icon' /></div>"),
                    $("<span class='all_insert_cell_text' />").text(_t("Insert Line"))
                );

                $tr = $('<tr/>', { class: 'all_insert_row'})
                    .data('id', record.id)
                    .append($td);
            } else {
                $tr = $('<tr/>');
            }
            return $tr;
        },

        /**
         * @override
         * @private
         */
        _renderBody: function () {
            var self = this;
            var $body = this._super.apply(this, arguments);
            if (this.hasHandle) {
                $body.sortable({
                    axis: 'y',
                    items: '> tr.o_data_row',
                    helper: 'clone',
                    handle: '.o_row_handle',
                    stop: function (event, ui) {
                        // update currentID taking moved line into account
                        if (self.currentRow !== null) {
                            if (self.currentRow < self.state.data.length){
                                var currentID = self.state.data[self.currentRow].id;
                                self.currentRow = self._getRow(currentID).index();
                            } else if (self.currentRow/2 < self.state.data.length && Number.isInteger(self.currentRow/2)){
                                var currentID = self.state.data[self.currentRow / 2].id;
                                self.currentRow = self._getRow(currentID).index();
                            }
                        }
                        self.unselectRow().then(function () {
                            // we need to ignore here too the rows that are not of class o_data_row so using the handler to reorder items will work too
                            var index = self.$('.o_data_row').index(ui.item);
                            self._moveRecord(ui.item.data('id'), index);
                        });
                    },
                });
            }
            return $body;
        },

        /**
         * @override
         * @private
         */
        _renderRows: function () {
            var $rows = [];
            for (const [i, record] of this.state.data.entries()) {
                $rows.push(this._renderRow(record));
                if (this.renderInsertLine) {
                    $rows.push(this._renderInsertRow(record, i));
                }
            }

            if (this.addCreateLine) {
                var $tr = $('<tr>');
                var colspan = this._getNumberOfCols();

                if (this.handleField) {
                    colspan = colspan - 1;
                    $tr.append('<td>');
                }

                var $td = $('<td>')
                    .attr('colspan', colspan)
                    .addClass('o_field_x2many_list_row_add');
                $tr.append($td);
                $rows.push($tr);

                if (this.addCreateLine) {
                    _.each(this.creates, function (create, index) {
                        var $a = $('<a href="#" role="button">')
                            .attr('data-context', create.context)
                            .text(create.string);
                        if (index > 0) {
                            $a.addClass('ml16');
                        }
                        $td.append($a);
                    });
                }
            }
            return $rows;
        },

        /**
         * @override
         */
        confirmUpdate: function (state, id, fields, ev) {
            /*
            * In this method we have added our rows with class '.all_insert_row' inside the logic, but for the rest is the same original method
            */

           var oldData = this.state.data;
           this._setState(state);
           var self = this;
            return this.confirmChange(state, id, fields, ev).then(function () {
                // If no record with 'id' can be found in the state, the
                // confirmChange method will have rerendered the whole view already,
                // so no further work is necessary.
                var record = self._getRecord(id);
                if (!record) {
                    return;
                }

                _.each(oldData, function (rec) {
                    if (rec.id !== id) {
                        self._destroyFieldWidgets(rec.id);
                    }
                });

                // re-render whole body (outside the dom)
                self.defs = [];
                var $newBody = self._renderBody();
                var defs = self.defs;
                delete self.defs;

                return Promise.all(defs).then(function () {
                    // update registered modifiers to edit 'mode' because the call to
                    // _renderBody set baseModeByRecord as 'readonly'
                    _.each(self.columns, function (node) {
                        self._registerModifiers(node, record, null, {mode: 'edit'});
                    });

                    // store the selection range to restore it once the table will
                    // be re-rendered, and the current cell re-selected

                    self.el.className = self.el.className.replace("hideHandlers ", "");
                    var currentRowID;
                    var currentWidget;
                    var focusedElement;
                    var selectionRange;
                    if (self.currentRow !== null) {
                        currentRowID = self._getRecordID(self.currentRow);
                        currentWidget = self.allFieldWidgets[currentRowID][self.currentFieldIndex];
                        if (currentWidget) {
                            focusedElement = currentWidget.getFocusableElement().get(0);
                            if (currentWidget.formatType !== 'boolean' && focusedElement) {
                                selectionRange = dom.getSelectionRange(focusedElement);
                            }
                        }
                    }

                    // remove all data rows except the one being edited, and insert
                    // data rows of the re-rendered body before and after it
                    var $editedRow = self._getRow(id);
                    $editedRow.nextAll('.o_data_row, .all_insert_row').remove();
                    $editedRow.prevAll('.o_data_row, .all_insert_row').remove();
                    var $newRow = $newBody.find('.o_data_row[data-id="' + id + '"]');
                    $newRow.prevAll('.o_data_row, .all_insert_row').get().reverse().forEach(function (row) {
                        $(row).insertBefore($editedRow);
                    });
                    $newRow.nextAll('.o_data_row, .all_insert_row').get().reverse().forEach(function (row) {
                        $(row).insertAfter($editedRow);
                    });

                    if (self.currentRow !== null) {
                        var newRowIndex = $editedRow.prop('rowIndex') - 1;
                        self.currentRow = newRowIndex;
                        return self._selectCell(newRowIndex, self.currentFieldIndex, {force: true})
                            .then(function () {
                                // restore the selection range
                                currentWidget = self.allFieldWidgets[currentRowID][self.currentFieldIndex];
                                if (currentWidget) {
                                    focusedElement = currentWidget.getFocusableElement().get(0);
                                    if (selectionRange) {
                                        dom.setSelectionRange(focusedElement, selectionRange);
                                    }
                                }
                            });
                    }
                });
            });
        },

    _onRemoveIconClick: function (event) {
        this.el.className = this.el.className.replace("hideHandlers ", "");
        this._super.apply(this, arguments);
    },

    });
});
