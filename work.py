    # This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from decimal import Decimal
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, ModelSQL, fields
from trytond.model import UnionMixin
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateAction, Button
from sql import Column
from trytond.pyson import PYSONEncoder

__all__ = ['Work', 'ProjectSummary', 'PurchaseLine']
_ZERO = Decimal('0.0')


class PurchaseLine:
    __name__ = 'purchase.line'
    __metaclass__ = PoolMeta

    @classmethod
    def get_total(cls, lines, names):
        res = super(PurchaseLine, cls).get_total(lines, names)
        res['cost_merited'] = {}
        limit_date = Transaction().context.get('limit_date')
        for line in lines:
            res['cost_merited'][line.id] = line._get_shipped_amount(
                limit_date)

        for key in res.keys():
            if key not in names:
                del res[key]

        return res


class ProjectSummary(UnionMixin, ModelSQL, ModelView):
    'Project Summary'
    __name__ = 'project.work.summary'
    revenue_merited = fields.Function(fields.Numeric('Revenue (F)'),
        'get_total')
    cost_merited = fields.Function(fields.Numeric('Cost (F)'),
        'get_total')


class Work:
    __name__ = 'project.work'
    __metaclass__ = PoolMeta
    cost_moves = fields.Function(fields.One2Many('account.move.line', None,
        'Cost Move Lines'), 'get_cost_moves')
    cost_merited = fields.Function(fields.Numeric('Cost (M)'),
        'get_total')

    @classmethod
    def _get_summary_fields(cls):
        return super(Work, cls)._get_summary_fields() + ['cost_merited']

    @classmethod
    def _get_cost_merited(cls, works):
        res = {}
        limit_date = Transaction().context.get('limit_date')
        for work in works:
            res[work.id] = 0
            for line in work.purchase_lines:
                res[work.id] += line._get_shipped_amount(limit_date)
        return res

    @classmethod
    def get_cost_moves(cls, works, name):
        res = {}
        pool = Pool()
        MoveLine = pool.get('account.move.line')
        for work in works:
            res[work.id] = []
            lines = [x.id for x in work.purchase_lines]
            if not lines:
                continue
            move_lines = MoveLine.search([('purchase_line', 'in', lines)])
            res[work.id] += [x.id for x in move_lines]
        return res
