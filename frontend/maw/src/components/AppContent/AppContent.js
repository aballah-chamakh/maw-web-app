import './AppContent.scss' ;
import { Routes,Route } from 'react-router-dom';
import OrderLoader from './OrderLoader/OrderLoader';
import OrderSubmitter from './OrderSubmitter/OrderSubmitter';
import OrderMonitoror from './OrderMonitoror/OrderMonitoror';
import LoxboxAreasContainer from './LoxboxAreasContainer/LoxboxAreasContainer';


const AppContent = (props)=>{
    return(
        <div className="app-content-container">

          <Routes>
                    <Route path="/load_orders" element={<OrderLoader />} />
                    <Route path="/load_orders/:orders_loader_id/submit_orders" element={<OrderSubmitter />} />
                    <Route path="/monitor_orders" element={<OrderMonitoror />} />
                    <Route path="/loxbox_areas" element={<LoxboxAreasContainer />} />
          </Routes>
          
        </div>
    )
}
export default AppContent ;
