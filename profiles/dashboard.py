"""
This file was generated with the customdashboard management command and
contains the class for the main dashboard.

To activate your index dashboard add the following to your settings.py::
    GRAPPELLI_INDEX_DASHBOARD = 'profiles.dashboard.CustomIndexDashboard'
"""

from django.utils.translation import gettext_lazy as _

from grappelli.dashboard import modules, Dashboard
from grappelli.dashboard.utils import get_admin_site_name


class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for www.
    """

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        self.children.append(modules.ModelList(
            title='❇️ Quick List',
            column=1,
            models=(
                'indicators.models.Indicator',
                'indicators.models.viz.DataViz',
            ),
            # hack to quickly make the links not burn your eyes out
            pre_content='<style>.grp-link-external { color: blue !important; text-decoration: underline !important;}</style>'
        ))

        self.children.append(modules.ModelList(
            title='📚 Taxonomy',
            column=1,
            models=(
                'indicators.models.Domain',
                'indicators.models.Subdomain',
                'indicators.models.Indicator',
            )
        ))

        self.children.append(modules.ModelList(
            title='📊 Data Visualization',
            column=1,
            models=(
                'indicators.models.viz.DataViz',
                'indicators.models.variable.Variable',
                'indicators.models.time.TimeAxis',
            )
        ))

        self.children.append(modules.ModelList(
            title='💾 Sources',
            column=1,
            models=(
                'indicators.models.source.CKANSource',
                'indicators.models.source.CensusSource',
            )
        ))

        self.children.append(modules.AppList(
            _('All Models'),
            collapsible=True,
            column=1,
            css_classes=('collapse closed',),
            exclude=('django.contrib.*',),
        ))

        self.children.append(modules.ModelList(
            _('Administration'),
            column=2,
            collapsible=True,
            models=('django.contrib.*',),
        ))

        self.children.append(modules.LinkList(
            _('External Links'),
            column=3,
            children=[
                {
                    'title': _('Profiles Data Explorer'),
                    'url': 'https://profiles.wprdc.org/explore/',
                    'external': True,
                },
                {
                    'title': _('WPRDC Components'),
                    'url': 'https://profiles.wprdc.org/components',
                    'external': True,
                },
                {
                    'title': _('Django Documentation'),
                    'url': 'http://docs.djangoproject.com/',
                    'external': True,
                },
                {
                    'title': _('Grappelli Documentation'),
                    'url': 'http://packages.python.org/django-grappelli/',
                    'external': True,
                },
                {
                    'title': _('Grappelli Google-Code'),
                    'url': 'http://code.google.com/p/django-grappelli/',
                    'external': True,
                },
            ]
        ))

        self.children.append(modules.RecentActions(
            _('Recent actions'),
            limit=5,
            collapsible=False,
            column=2,
        ))
