import { useState,useEffect } from "react"
import axios from "axios"
import './OrderMonitoror.scss'
import LoadingPage from "../../CommonComponents/LoadingPage/LoadingPage"
import GenericTable from "../../CommonComponents/GenericTable/GenericTable"
import GenericModal from "../../CommonComponents/GenericModal/GenericModal"
import ResultPopupContent from "./ResultPopupContent/ResultPopupContent"
import { API_ENDPOINT } from "../../../globals"




const OrderMonitoror = ()=>{
    const [isLoading,setIsLoading] = useState(true)
    const [loadingActionTxt,setLoadingActionTxt] = useState('loading orders to monitor')
    const [progress,setProgress] = useState(null)
    const [orders,setOrders] = useState([])
    const [isResultPopupShowed,setResultPopupShowed] = useState(false)
    const [resultPopupData,setResultPopupData] = useState({title:'',conv_errors:{},orders:[],old_monitor_orders_len:0})
    // useState({title:'',orders:[]})
    const order_keys = ['order_id','state','carrier']

    useEffect(()=>{
        axios.get(API_ENDPOINT+"/monitor_orders").then(res=>{
            let orders = res.data 
            setOrders(orders)
            setIsLoading(false)
        })
    },[])

    const closeOrderMonitoror = ()=>{
        setResultPopupShowed(false)
    }
    
    const monitorOrders = ()=>{
        setIsLoading(true)
        setLoadingActionTxt('monitoring orders')
        axios.post(API_ENDPOINT+'/orders_monitoror/launch').then(res=>{
            let orders_monitoror_id = res.data.orders_monitoror_id
            let req_done  = true 
            let intv =  setInterval(()=>{
                if(req_done){
                    req_done = false 
                    axios.get(API_ENDPOINT+'/orders_monitoror/'+orders_monitoror_id+'/monitor').then(res=>{
                        
                        let data = res.data 

                        if(data.state=='FINISHED'){
                            // RESET THE LOADING PAGE 
                            setIsLoading(false)
                            setLoadingActionTxt('loading orders to monitor')

                            // UPDATE MONITOR ORDERS AFTER MONITORING 
                            setOrders(data.new_monitor_orders)


                            // HANDLE RESULTS DATA IF IT EXIST 
                            if(data.results){
                                // SET THE RESULT DATA FOR THE POPUP 
                                setResultPopupData({
                                    title:data.results.length +'/'+progress.orders_to_be_monitored+' order(s) were updated',
                                    orders:data.results,
                                    old_monitor_orders_len:progress.orders_to_be_monitored,
                                    conv_errors : data.conv_errors
                                })
                
                                // LOAD THE RESULT POPUP
                                setResultPopupShowed(true)
                            }

                            
                            // CLEAN THE PROGRESS FOR THE NEXT TIME WHEN WE MONITOR WE DON'T START THE LOADING PAGE 
                            // WITH THE OLD PROGRESS DATA 
                            //setProgress(null)


                            // CLEAR THE INTERVAL 
                            clearInterval(intv)

                        }else if(data.progress){
                            setProgress(data.progress)
                        }
                        req_done = true
                    })
                }
            },5000)
        })
    }

    return(
        !isLoading ? 

        <div class='order-monitoror'>
            <p className='order-monitoror-title'>{orders.length} order(s) to monitor</p>
            <GenericTable keys={order_keys} orders={orders} maxHeight='70vh' />
            <button className='order-monitoror-monitor-btn' onClick={monitorOrders} >monitor order(s)</button>
            <GenericModal type='result' size='lg' show={isResultPopupShowed} 
                          title={resultPopupData.title} closeModal={closeOrderMonitoror}
                          result_content={<ResultPopupContent resultPopupData={resultPopupData}   />} />
        </div>
        : <LoadingPage action_txt={loadingActionTxt} done_action_txt='were monitored' progress={progress} />
    )
}

export default OrderMonitoror