from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from geo.models import Geography
from indicators.models import Domain, Subdomain, Indicator, DataViz, Variable, TimeAxis
from indicators.serializers import (DomainSerializer, IndicatorSerializer, SubdomainSerializer,
                                    TimeAxisPolymorphicSerializer)
from indicators.serializers.variable import VariablePolymorphicSerializer
from indicators.serializers.viz import DataVizWithDataPolymorphicSerializer, DataVizPolymorphicSerializer
from indicators.utils import (is_region_data_request, get_region_from_query_params, REGION_TYPE_LABEL,
                              REGION_ID_LABEL, is_valid_geography_type, ErrorResponse, ErrorLevel, extract_geo_params)


class DomainViewSet(viewsets.ModelViewSet):
    queryset = Domain.objects.all()
    serializer_class = DomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class SubdomainViewSet(viewsets.ModelViewSet):
    queryset = Subdomain.objects.all()
    serializer_class = SubdomainSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class IndicatorViewSet(viewsets.ModelViewSet):
    queryset = Indicator.objects.all()
    serializer_class = IndicatorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class VariableViewSet(viewsets.ModelViewSet):
    queryset = Variable.objects.all()
    serializer_class = VariablePolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class TimeAxisViewSet(viewsets.ModelViewSet):
    queryset = TimeAxis.objects.all()
    serializer_class = TimeAxisPolymorphicSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class DataVizViewSet(viewsets.ModelViewSet):
    queryset = DataViz.objects.all()

    def get_serializer_class(self):
        if is_region_data_request(self.request):
            return DataVizWithDataPolymorphicSerializer
        return DataVizPolymorphicSerializer

    def get_serializer_context(self):
        context = super(DataVizViewSet, self).get_serializer_context()
        if is_region_data_request(self.request):
            try:
                context['geography'] = get_region_from_query_params(self.request)
            except Geography.DoesNotExist as e:
                print(e)  # todo: figure out how we should log stuff
                geo_type, geoid = extract_geo_params(self.request)
                context['error'] = ErrorResponse(ErrorLevel.ERROR,
                                                 f'Can\'t find "{geo_type}" with ID "{geoid}".').as_dict()
        return context
