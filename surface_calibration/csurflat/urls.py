from django.urls import path
from .views import HomeView, WorkOrderDetailView, MeasurementDataView, FlatnessView, DeviationPlotView

urlpatterns = [
    path('', HomeView.as_view(), name="home"),
    path('<str:wid>/work_order', WorkOrderDetailView.as_view(), name="work_order_detail"),
    path('<str:wid>/measurement_data', MeasurementDataView.as_view(), name="measurement_data"),
    path('<str:wid>/flatness_data', FlatnessView.as_view(), name="flatness_data"),
    path('<str:wid>/deviation_plot', DeviationPlotView.as_view(), name="deviation_plot"),
]
