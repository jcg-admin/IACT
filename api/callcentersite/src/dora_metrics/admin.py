"""Admin para metricas DORA."""

from django.contrib import admin

from .models import DORAMetric


@admin.register(DORAMetric)
class DORAMetricAdmin(admin.ModelAdmin):
    """Admin para DORAMetric."""

    list_display = ["cycle_id", "feature_id", "phase_name", "decision", "created_at"]
    list_filter = ["phase_name", "decision", "created_at"]
    search_fields = ["cycle_id", "feature_id"]
    readonly_fields = ["created_at"]

    def get_readonly_fields(self, request, obj=None):
        """Hacer cycle_id readonly cuando se edita."""
        if obj:  # Editando existente
            return self.readonly_fields + ["cycle_id"]
        return self.readonly_fields
