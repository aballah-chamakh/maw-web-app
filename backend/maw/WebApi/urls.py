
from django.urls import path
from .views.loading_orders_views import *
from .views.submitting_orders_views import *
from .views.monitoring_orders_views import *
from .views.loxbox_areas_views import *  
from .views.setting_views import *  

urlpatterns = [
    # LOADING ORDERS URLS 
    path('orders_loader/launch', launch_orders_loader),
    path('orders_loader/<int:id>/cancel', cancel_orders_loader),
    path('orders_loader/<int:id>/monitor', monitor_orders_loader),
    path('get_last_undone_step_of_the_last_order_loader', get_last_undone_step_of_the_last_order_loader),
    
    

    # SUBMITTING ORDERS URLS 
    path('set_order_carrier', set_order_carrier),
    path('toggle_order_selection', toggle_order_selection),
    path('select_unselect_all_orders', select_unselect_all_orders),
    path('orders_submitter/launch', launch_orders_submitter),
    path('orders_submitter/<int:id>/monitor', monitor_orders_submitter),
    
    # MONITORING ORDERS URLS²
    path('monitor_orders', monitor_orders_list),
    path('orders_monitoror/launch', launch_orders_monitoror),
    path('orders_monitoror/<int:id>/monitor', monitor_orders_monitoror),

    #LOXBOX AREAS URLS 
    
    path('monitor_loxbox_areas_selector_process', monitor_loxbox_areas_selector_process),
    path('loxbox_areas', loxbox_areas_list),
    path('launch_loxbox_areas_select_or_deselect',loxbox_areas_select_or_deselect),

    # SETTING URL  
    path('get_setting', get_setting),
    path('update_setting', update_setting),


]


"""
    OLD  WAY OF SELECTING AND DESELECTING 
    path('loxbox_areas/<str:select_type>', loxbox_areas_select_unselect_all),
    path('city/<int:city_id>/<str:select_type>', city_select_unselect_all),
    path('delegation/<int:delegation_id>/<str:select_type>', delegation_select_unselect_all),
    path('locality/<int:locality_id>/<str:select_type>', locality_select_unselect),

"""

