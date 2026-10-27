from django.db.models import Count, Sum
from django.views.generic import TemplateView
from django.shortcuts import redirect
import json

from apps.master_data.models import Commodity, CommodityGroup
from apps.spatial.models import MasterLayer, SuitabilityAnalysisResult, ExpertReview


class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('/spatial/map/')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Role flags untuk conditional rendering di template
        context['is_admin'] = user.is_superuser or user.has_role('admin')
        context['is_tenaga_ahli'] = user.has_role('tenaga_ahli')

        context['total_layers'] = MasterLayer.objects.filter(is_active=True).count()
        context['total_commodities'] = Commodity.objects.count()
        context['total_commodity_groups'] = CommodityGroup.objects.count()

        # Analysis stats
        context['total_analysis'] = SuitabilityAnalysisResult.objects.count()
        context['completed_analysis'] = SuitabilityAnalysisResult.objects.filter(
            status='completed'
        ).count()
        context['active_analysis'] = SuitabilityAnalysisResult.objects.filter(
            is_active=True
        ).count()

        # Expert reviews
        context['total_reviews'] = ExpertReview.objects.count()

        # Recent results (last 5)
        context['recent_results'] = SuitabilityAnalysisResult.objects.select_related(
            'commodity', 'base_layer'
        ).order_by('-created_at')[:5]

        # --- Data chart: distribusi komoditas per grup ---
        group_counts = (
            Commodity.objects
            .values('group__name')
            .annotate(count=Count('id'))
            .order_by('group__name')
        )
        commodity_group_chart = {
            'labels': [g['group__name'] or 'Tanpa Grup' for g in group_counts],
            'data': [g['count'] for g in group_counts],
        }
        context['commodity_group_chart'] = commodity_group_chart
        context['commodity_group_chart_json'] = json.dumps(commodity_group_chart)

        # --- Data chart: komoditas tanpa kriteria kesesuaian ---
        context['commodities_without_criteria'] = (
            Commodity.objects
            .annotate(criteria_count=Count('characteristics'))
            .filter(criteria_count=0)
            .count()
        )

        # --- Data chart: distribusi kelas S1–N (akumulasi hasil selesai) ---
        completed = SuitabilityAnalysisResult.objects.filter(status='completed')
        class_distribution = {
            'labels': ['S1', 'S2', 'S3', 'N'],
            'data': [
                completed.aggregate(total=Sum('s1_count'))['total'] or 0,
                completed.aggregate(total=Sum('s2_count'))['total'] or 0,
                completed.aggregate(total=Sum('s3_count'))['total'] or 0,
                completed.aggregate(total=Sum('n_count'))['total'] or 0,
            ],
        }
        context['class_distribution'] = class_distribution
        context['class_distribution_json'] = json.dumps(class_distribution)

        return context