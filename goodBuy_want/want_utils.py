from django.db.models import *
from .models import *
# -------------------------
# 收物貼fk串接
# -------------------------
def wantInformation_many(wants):
    return (
        wants
        .select_related('permission')
        .prefetch_related(
            Prefetch('wanttag_set', queryset=WantTag.objects.select_related('tag')),
            Prefetch('images', queryset=WantImg.objects.filter(is_cover=True)),
        )
    )