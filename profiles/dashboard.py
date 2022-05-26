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

        # Column 1

        self.children.append(modules.ModelList(
            title='❇️ Most Used',
            column=1,
            models=(
                'indicators.models.Topic',
                'indicators.models.indicator.Indicator',
            ),
            # hack to quickly make the links not burn your eyes out
            pre_content="""
            <style>
                        .grp-link-external {
                        color: #309bbf !important;
                        font-weight: 600; 
                        text-decoration: underline !important;
                        }
                     </style>
            """,
        ))

        self.children.append(modules.ModelList(
            title='📚 Taxonomy',
            column=1,
            models=(
                'indicators.models.Taxonomy',
                'indicators.models.Domain',
                'indicators.models.Subdomain',
                'indicators.models.Topic',
            )
        ))

        self.children.append(modules.ModelList(
            title='📊 Indicator',
            column=1,
            models=(
                'indicators.models.indicator.Indicator',
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

        self.children.append(modules.ModelList(
            title='🏡 Housing',
            column=1,
            models=(
                'public_housing.models.Account',
                'public_housing.models.Watchlist',
            )
        ))

        self.children.append(modules.ModelList(
            title='🌎 Geographies',
            column=1,
            models=(
                'geo.models.Neighborhood',
                'geo.models.BlockGroup',
                'geo.models.Tract',
                'geo.models.CountySubdivision',
                'geo.models.County',
                'geo.models.ZipCodeTabulationArea',
                'geo.models.SchoolDistrict',
            )
        ))

        self.children.append(modules.ModelList(
            _('🛂 Administration'),
            column=2,
            collapsible=True,
            models=('django.contrib.*',),
        ))

        self.children.append(modules.ModelList(
            _('🏷 Context'),
            column=2,
            collapsible=True,
            models=(
                'context.models.Tag',
                'context.models.ContextItem'
            )
        ))

        self.children.append(modules.AppList(
            _('All Models'),
            collapsible=True,
            column=2,
            css_classes=('grp-closed',),
            exclude=('django.contrib.*',),
        ))

        # Column 3

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
            limit=10,
            collapsible=False,
            column=3,
        ))
