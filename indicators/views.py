from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geo.models import AdminRegion
from indicators.models import Domain, Topic, Indicator, Variable, TimeAxis, Taxonomy
from indicators.serializers import DomainSerializer, TopicSerializer, \
    TimeAxisPolymorphicSerializer, VariablePolymorphicSerializer, IndicatorWithDataSerializer, \
    IndicatorSerializer, IndicatorBriefSerializer, TaxonomySerializer, TopicBriefSerializer, TaxonomyBriefSerializer, \
    DomainBriefSerializer
from indicators.utils import is_geog_data_request, get_geog_from_request, ErrorRecord, ErrorLevel


class TaxonomyViewSet(viewsets.ModelViewSet):
    queryset = Taxonomy.objects.all()
    serializer_class = TaxonomySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return TaxonomyBriefSerializer
        return TaxonomySerializer


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return DomainBriefSerializer
        return DomainSerializer

    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super(DomainViewSet, self).retrieve(request, *args, **kwargs)



class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return TopicBriefSerializer
        return TopicSerializer

    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super(TopicViewSet, self).retrieve(request, *args, **kwargs)


class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariablePolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class TimeAxisViewSet(viewsets.ModelViewSet):
    queryset = TimeAxis.objects.all()
    serializer_class = TimeAxisPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]


class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', ]
    lookup_field = 'slug'

    def get_serializer_class(self):
        if self.action == 'list':
            return IndicatorBriefSerializer
        if is_geog_data_request(self.request):
            return IndicatorWithDataSerializer
        return IndicatorSerializer

    def get_serializer_context(self):
        """
        Context for indicators current used for
        `geog`: the geography data will be collected for
        `across_geogs`: set to True if the request should collect data for neighbor geogs too
        """
        context = super(IndicatorViewSet, self).get_serializer_context()

        if is_geog_data_request(self.request):
            try:
                context['geography'] = get_geog_from_request(self.request)
            except AdminRegion.DoesNotExist as e:
                print(e)  # todo: figure out how we should log stuff
                context['error'] = ErrorRecord(
                    ErrorLevel.ERROR,
                    f'Can\'t find "{self.request.query_params.get("geog")}".'
                ).as_dict()

        context['across_geogs'] = self.request.query_params.get('acrossGeogs', False)

        return context

    @method_decorator(cache_page(settings.VIEW_CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super(IndicatorViewSet, self).retrieve(request, *args, **kwargs)
