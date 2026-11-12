# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from random import randint

from odoo import _, api, models, fields
from odoo.exceptions import UserError


class DocumentsTag(models.Model):
    _name = 'documents.tag'
    _description = "Tag"
    _order = "sequence, name"

    @api.model
    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer('Sequence', default=10)
    color = fields.Integer('Color', default=_get_default_color)
    tooltip = fields.Char(help="Text shown when hovering on this tag", string="Tooltip")  # Deprecated
    document_ids = fields.Many2many('documents.document', 'document_tag_rel')
    facet_id = fields.Many2one(
        'documents.facet', string="Category", index=True, ondelete='set null',
        help="Category under which the tag is grouped in the left panel.")

    # The same tag name can be used in several categories (e.g. "2024" in
    # "Fiscal years" and in "Payslips"), but only once per category, and only
    # once among the tags without category.
    _tag_name_facet_unique = models.Constraint(
        'unique (name, facet_id)',
        "This tag name is already used in this category",
    )
    _tag_name_no_facet_unique = models.UniqueIndex(
        "(name) WHERE facet_id IS NULL",
        "Tag name already used (tags without category)",
    )

    @api.depends('name', 'facet_id.name')
    @api.depends_context('documents_tag_show_facet')
    def _compute_display_name(self):
        """Show "Category > Tag" in the tag selection dropdowns, so that tags
        with the same name in different categories can be told apart."""
        if not self.env.context.get('documents_tag_show_facet'):
            return super()._compute_display_name()
        for tag in self:
            tag.display_name = f"{tag.facet_id.name} > {tag.name}" if tag.facet_id else tag.name

    @api.ondelete(at_uninstall=False)
    def _unlink_except_used_in_server_action(self):
        external_ids = self._get_external_ids()
        resource_refs = [f'documents.tag,{k}' for k in external_ids.keys()]
        if external_ids and self.env['ir.actions.server'].search_count([('resource_ref', 'in', resource_refs)], limit=1):
            raise UserError(_("You cannot delete tags used in server actions."))
