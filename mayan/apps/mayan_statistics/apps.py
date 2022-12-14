from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_object, menu_secondary, menu_tools
from mayan.apps.navigation.classes import SourceColumn

from .classes import StatisticLineChart, StatisticNamespace
from .links import (
    link_statistic_namespace_detail,
    link_statistic_namespace_list,
    link_statistic_queue,
    link_statistic_detail,
    link_statistics
)


class StatisticsApp(MayanAppConfig):
    app_namespace = 'statistics'
    app_url = 'statistics'
    has_static_media = True
    has_tests = True
    name = 'mayan.apps.mayan_statistics'
    static_media_ignore_patterns = (
        'statistics/node_modules/chart.js/book.*',
        'statistics/node_modules/chart.js/karma.conf.*',
        'statistics/node_modules/chart.js/samples/*',
        'statistics/node_modules/chart.js/src/*',
        'statistics/node_modules/chart.js/*docs*',
    )
    verbose_name = _('Statistics')

    def ready(self):
        super().ready()

        SourceColumn(
            attribute='schedule',
            # Translators: Schedule here is a noun, the 'schedule' at
            # which the statistic will be updated
            include_label=True, label=_('Schedule'),
            source=StatisticLineChart
        )

        SourceColumn(
            attribute='get_last_update', include_label=True,
            label=_('Last update'), source=StatisticLineChart
        )

        menu_object.bind_links(
            links=(link_statistic_detail, link_statistic_queue),
            sources=(StatisticLineChart,)
        )
        menu_object.bind_links(
            links=(link_statistic_namespace_detail,),
            sources=(StatisticNamespace,)
        )
        menu_secondary.bind_links(
            links=(link_statistic_namespace_list,),
            sources=(
                StatisticNamespace, 'statistics:statistic_namespace_list'
            )
        )
        menu_tools.bind_links(links=(link_statistics,))
