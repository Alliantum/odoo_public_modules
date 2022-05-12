This module allows you to insert lines at any position in your list views.

By default in Odoo, you get two options about where you prefer to enter new records in your list views. The option is available in `tree` views as the attribute `editable`, and values are `bottom` or `top`. However, what if in some cases you would like to enter a specific line at a concrete position in your list, maybe your list is huge, and even have multiple pages and make it very complicated or impossible to create your new line, and move it (just when a handler for sequences is available) to your desired position.

For cases like this, with this module you will have a new attribute available for your `tree` views! The new attribute is `insert`, and the value for it is a *boolean*.
