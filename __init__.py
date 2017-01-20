# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import work


def register():
    Pool.register(
        work.ProjectSummary,
        work.Work,
        module='project_management_merited_amounts', type_='model')
