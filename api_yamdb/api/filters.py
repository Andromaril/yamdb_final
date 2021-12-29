from django_filters import CharFilter, Filter, FilterSet, NumberFilter
from reviews.models import Title


class SlugFilter(Filter):
    def filter(self, qs, value):
        if not value:
            return qs
        self.lookup_expr = 'slug'
        return super(SlugFilter, self).filter(qs, value)


class TitleFilter(FilterSet):
    category = SlugFilter('category_id')
    genre = SlugFilter('genre')
    year = NumberFilter()
    name = CharFilter(lookup_expr='icontains')

    class Meta:
        model = Title
        fields = {'name', 'year', 'category', 'genre', }
