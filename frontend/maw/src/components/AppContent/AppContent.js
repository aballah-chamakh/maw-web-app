import './AppContent.scss' ;
import { Routes,Route } from 'react-router-dom';
import OrderLoader from './OrderLoader/OrderLoader';
import OrderSubmitter from './OrderSubmitter/OrderSubmitter';
import OrderMonitoror from './OrderMonitoror/OrderMonitoror';
import LoxboxAreasContainer from './LoxboxAreasContainer/LoxboxAreasContainer';
import SettingContainer from './SettingContainer/SettingContainer';
import Test from './Test' ;

const AppContent = (props)=>{
    return(
        <div className="app-content-container">

          <Routes>
                    <Route path="/load_orders" element={<OrderLoader />} />
                    <Route path="/load_orders/:orders_loader_id/submit_orders" element={<OrderSubmitter />} />
                    <Route path="/monitor_orders" element={<OrderMonitoror />} />
                    <Route path="/loxbox_areas" element={<LoxboxAreasContainer />} />
                    <Route path="/settings" element={<SettingContainer />} />
                    <Route path="/test" element={<Test />} />
                    <Route path="/account" element={<Test />} />
          </Routes>
          
        </div>
    )
}
export default AppContent ;
