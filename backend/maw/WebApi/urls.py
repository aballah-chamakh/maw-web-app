
from django.urls import path
from .views.loading_orders_views import *
from .views.submitting_orders_views import *
from .views.monitoring_orders_views import *

urlpatterns = [
    # LOADING ORDERS URLS 
    path('orders_loader/launch', launch_orders_loader),
    path('orders_loader/<int:id>/monitor', monitor_orders_loader),
    

    # SUBMITTING ORDERS URLS 
    # orders_submitter/id/monitor
    path('toggle_order_selection', toggle_order_selection),
    path('orders_submitter/launch', launch_orders_submitter),
    path('orders_submitter/<int:id>/monitor', monitor_orders_submitter),
    
    # MONITORING ORDERS URLS
    path('monitor_orders', monitor_orders_list),
    path('orders_monitoror/launch', launch_orders_monitoror),
    path('orders_monitoror/<int:id>/monitor', monitor_orders_monitoror)

]