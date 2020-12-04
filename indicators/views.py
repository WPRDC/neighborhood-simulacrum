from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from indicators.models import Domain, Subdomain, Indicator, DataViz, Variable, TimeAxis
from indicators.serializers import DomainSerializer, IndicatorSerializer, SubdomainSerializer, \
    TimeAxisPolymorphicSerializer
from indicators.serializers.variable import VariablePolymorphicSerializer
from indicators.serializers.viz import DataVizWithDataPolymorphicSerializer, DataVizPolymorphicSerializer
from indicators.utils import is_valid_region_query_request, get_region_from_query_params


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
        if is_valid_region_query_request(self.request):
            return DataVizWithDataPolymorphicSerializer
        return DataVizPolymorphicSerializer

    def get_serializer_context(self):
        context = super(DataVizViewSet, self).get_serializer_context()
        if is_valid_region_query_request(self.request):
            context['region'] = get_region_from_query_params(self.request)
        return context
