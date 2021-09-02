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
            if (this.renderInsertLine && ev.currentTarget.nextSibling && !this._isLastInsertRow(ev.currentTarget) &&  ev.currentTarget.nextSibling.firstChild) {
                ev.currentTarget.nextSibling.firstChild.style = "height: 0.5rem;";
            }
        },

        _onHoverRowLeave: function (ev) {
            if (this.renderInsertLine && ev.currentTarget.nextSibling && !this._isLastInsertRow(ev.currentTarget) && ev.currentTarget.nextSibling.firstChild) {
                ev.currentTarget.nextSibling.firstChild.style = "";
            }
        },

        // Avoid to show any option to insert under the last line
        _isLastInsertRow: function (rowElement) {
            var nextInsertFound;
            rowElement = rowElement.nextElementSibling;
            while (rowElement && (rowElement.classList.contains('all_insert_row') || rowElement.classList.contains('o_data_row')) && !nextInsertFound) {
                rowElement = rowElement.nextElementSibling;
                if (rowElement.className === 'all_insert_row') {
                    nextInsertFound = true;
                }
            }
            return !nextInsertFound;
        },

        editRecord: function (recordID) {
            // And we need this, to focus edition on the new created line, at the correct position
            var rowIndex = this.nextIndex || _.findIndex(this.state.data, {id: recordID});
            this._selectCell(rowIndex, 0);
        },

        _onInsertLine: function (ev) {
            ev.preventDefault();
            ev.stopPropagation();
            var context = ev.currentTarget.dataset.context && ev.currentTarget.dataset.context || {};
            if (this.renderInsertLine && ev.currentTarget.dataset.nextIndex) {
                // We save the nextIndex as a class variable. It will be used by the list_editable_rederer.js.
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
            // When creating a new record, for example a SO with many lines inside, before save that SO those lines will have all the same sequence,
            // and we don't want this because, if someone insert a line, and all the lines have the same sequence,
            // our lines will lost their position and will go to the button becase have bigger sequence
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
            let $tr;
            const self = this;
            if ( self.renderInsertLine ) {
                // Adding the "Insert Line" element
                const $td = $('<td/>', {
                    class: 'all_insert_cell',
                    colspan: '99',
                    'data-next-index': i + 1,
                    'data-handle-field': self.hasHandle && self.handleField || '',
                    'data-sequence': self.hasHandle && record.data[self.handleField]
                }).append($("<div style='width: 1rem; display: inline-block' ><i class='fa fa-arrow-right all_insert_cell_icon' /></div>"), $("<span class='all_insert_cell_text' />").text(_t("Insert Line")))

                $tr = $('<tr/>', { class: 'all_insert_row'})
                    .data('id', record.id)
                    .append($td);
            } else {
                $tr = $('<tr/>');
            }
            return $tr;
        },

        _renderRows: function () {
            var self = this;
            let $rows = [];
            for (const [i, record] of this.state.data.entries()) {
                if (this.renderInsertLine) {
                    $rows.push(this._renderRow(record), this._renderInsertRow(record, i));
                } else {
                    $rows.push(this._renderRow(record));
                }
            }

            if (this.addCreateLine) {
                var $tr = $('<tr>');
                var colspan = self._getNumberOfCols();

                if (this.handleField) {
                    colspan = colspan - 1;
                    $tr.append('<td>');
                }

                var $td = $('<td>')
                    .attr('colspan', colspan)
                    .addClass('o_field_x2many_list_row_add');
                $tr.append($td);
                $rows.push($tr);

                _.each(self.creates, function (create, index) {
                    var $a = $('<a href="#" role="button">')
                        .attr('data-context', create.context)
                        .text(create.string);
                    if (index > 0) {
                        $a.addClass('ml16');
                    }
                    $td.append($a);
                });
            }
            return $rows;
        },

        confirmUpdate: function (state, id, fields, ev) {
            var self = this;

            // store the cursor position to restore it once potential onchanges have
            // been applied
            var currentRowID, currentWidget, focusedElement, selectionRange;
            if (self.currentRow !== null) {
                currentRowID = this.state.data[this.currentRow].id;
                currentWidget = this.allFieldWidgets[currentRowID][this.currentFieldIndex];
                if (currentWidget) {
                    focusedElement = currentWidget.getFocusableElement().get(0);
                    if (currentWidget.formatType !== 'boolean') {
                        selectionRange = dom.getSelectionRange(focusedElement);
                    }
                }
            }

            var oldData = this.state.data;
            this.state = state;
            return this.confirmChange(state, id, fields, ev).then(function () {
                // If no record with 'id' can be found in the state, the
                // confirmChange method will have rerendered the whole view already,
                // so no further work is necessary.
                var record = _.findWhere(state.data, {id: id});
                if (!record) {
                    return;
                }
                var oldRowIndex = _.findIndex(oldData, {id: id});
                var $row = self.$('.o_data_row:nth(' + oldRowIndex + ')');
                $row.nextAll('.o_data_row').remove();
                if (self.renderInsertLine) {
                    // Remove here also our old insert lines, but not the one for the changed one!
                    $row.next().nextAll('.o_data_row').remove();
                }
                $row.prevAll().remove();
                _.each(oldData, function (rec) {
                    if (rec.id !== id) {
                        self._destroyFieldWidgets(rec.id);
                    }
                });
                var newRowIndex = _.findIndex(state.data, {id: id});
                var $lastRow = !self.renderInsertLine ? $row : $row.next(); // The next row here in our case is the "insert" line
                _.each(state.data, function (record, index) {
                    if (index === newRowIndex) {
                        return;
                    }
                    var $newRow = self._renderRow(record);
                    if (index < newRowIndex) {
                        $newRow.insertBefore($row);
                    } else {
                        $newRow.insertAfter($lastRow);
                        $lastRow = $newRow;
                    }
                    // Just when the list is ready to work with insertion
                    if (self.renderInsertLine) {
                        var $newInsertRow = self._renderInsertRow(record, index);
                        // And insert our new insert line always after the lines that we're adding here from scratch
                        $newInsertRow.insertAfter($newRow);
                        if (index > newRowIndex) {
                            $lastRow = $newInsertRow;
                        }
                    }
                });
                if (self.currentRow !== null) {
                    self.currentRow = newRowIndex;
                    return self._selectCell(newRowIndex, self.currentFieldIndex, {force: true}).then(function () {
                        // restore the cursor position
                        currentRowID = self.state.data[newRowIndex].id;
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
        },
    });
});
