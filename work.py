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


__all__ = ['Work', 'ProjectSummary']


class ProjectSummary(UnionMixin, ModelSQL, ModelView):
    'Project Summary'

    __name__ = 'project.work.summary'

    revenue_merited = fields.Function(fields.Numeric('Revenue (M)'),
        'get_total')
    cost_merited = fields.Function(fields.Numeric('Cost (M)'),
        'get_total')

    @classmethod
    def _get_summary_fields(cls):
        return cls._get_summary_fields() + ['revenue_merited', 'cost_merited']


class Work:
    __name__ = 'project.work'
    __metaclass__ = PoolMeta

    cost_moves = fields.Function(fields.One2Many('account.move.line', None,
        'Cost Move Lines'), 'get_cost_moves')
    cost_merited = fields.Function(fields.Numeric('Cost (M)'),
        'get_total')

    @classmethod
    def _get_cost_merited(cls, works):
        res = {}
        pool = Pool()
        MoveLine = pool.get('account.move.line')
        for work, moves in cls.get_cost_moves(works, 'cost_moves').iteritems():
            moves = MoveLine.browse()
            res[work] = sum(l.debit - l.credit
                for l in moves if l and not l.reconciliation)
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
