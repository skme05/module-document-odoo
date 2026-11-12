# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import api, fields, models


class DocumentsFacet(models.Model):
    """Tag category ("facet"), used to group the tags in the left panel of the
    Documents app (e.g. "Années fiscales" > 2023, 2024...), as it was the case
    before Odoo 18. The table name is the historical one (documents_facet), so
    that facets kept in the database by a migration are reused."""
    _name = 'documents.facet'
    _description = "Tag Category"
    _order = "sequence, name"

    @api.model
    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    color = fields.Integer('Color', default=_get_default_color)
    tooltip = fields.Char(help="Text shown when hovering on this tag category", string="Tooltip")
    tag_ids = fields.One2many('documents.tag', 'facet_id', string="Tags")
