import { useState,useEffect } from "react"
import axios from "axios"
import './OrderMonitoror.scss'
import LoadingPage from "../../CommonComponents/LoadingPage/LoadingPage"
import GenericTable from "../../CommonComponents/GenericTable/GenericTable"
import GenericModal from "../../CommonComponents/GenericModal/GenericModal"
import Dashboard from "../../CommonComponents/Dashboard/Dashboard"
import ResultPopupContent from "./ResultPopupContent/ResultPopupContent"
import { API_ENDPOINT,networkIcon,unauhorizationIcon } from '../../../globals';


const OrderMonitoror = ()=>{
    const [isLoading,setIsLoading] = useState(true)
    const [loadingActionTxt,setLoadingActionTxt] = useState('checking if the last orders monitoror was completed')
    const [progress,setProgress] = useState(null)
    const [orders,setOrders] = useState([])
    const [monitorIntv,setMonitorIntv] = useState(null)
    const [didMount,setDidMount] = useState(false)
    const [isResultPopupShowed,setResultPopupShowed] = useState(false)
    const [isProcessModalShowed,setProcessModalShowed] = useState(false)
    const [resultPopupData,setResultPopupData] = useState({title:'',conv_errors:{},orders:[],old_monitor_orders_len:0})
    const [processAlertData,setProcessAlerttData] = useState({title:"",icon:<i style={{color:'#D81010'}} className="fas fa-fingerprint"></i>,msg:""} )
    // useState({title:'',orders:[]})
    const order_keys = ['order_id','state','carrier']

    useEffect(()=>{
        if(didMount == false){
            setDidMount(true)
            axios.get(API_ENDPOINT+"/monitor_orders").then(res=>{
                // {'is_the_last_monitoror_working':is_the_last_monitoror_working,'all_monitor_orders':all_monitor_orders}
                let data  = res.data 
                let last_monitoror = data.last_monitoror 
                if(last_monitoror.is_working){
                    setLoadingActionTxt('monitoring orders')
                    monitorMonitoringOrders(last_monitoror.orders_monitoror_id)
                }else{
                    let orders = res.data.all_monitor_orders
                    setOrders(orders)
                    setIsLoading(false)
                }
            })
        }
    return ()=>{
        clearInterval(monitorIntv)
    }
    },[monitorIntv])

    const closeOrderMonitoror = ()=>{
        setResultPopupShowed(false)
    }

    const openProcessModal = (icon,title,msg)=>{
        setProcessModalShowed(true)
        setProcessAlerttData({
            icon : icon,
            title:title, 
            msg : msg
        })
    }

    const closeProcessModal = ()=>{
        setProcessModalShowed(false)
        setIsLoading(false)
        setProgress(null)
    }

    const monitorMonitoringOrders = (orders_monitoror_id)=>{
        let req_done  = true 
        let intv =  setInterval(()=>{
            if(req_done){
                req_done = false 
                axios.get(API_ENDPOINT+'/orders_monitoror/'+orders_monitoror_id+'/monitor').then(res=>{
                    let data = res.data 

                    if(data.state=='FINISHED'){
                     
                        

                        // UPDATE MONITOR ORDERS AFTER MONITORING 
                        setOrders(data.new_monitor_orders)

                        // HANDLE UNAUTHORIZATION ERROR IF IT EXIST 

                        if(data.unauthorization_error){

                            let splitted_unauthorization = data.unauthorization_error.split('_')
                   
                            let unauthorization_party = splitted_unauthorization[1].toLowerCase()

                            let unauthorization_element = splitted_unauthorization[2] == 'API' ? 'api key' : 'credentials'
                            
                            let title = `${unauthorization_party} unauhorization error`
                            let msg = `the ${unauthorization_element} of ${unauthorization_party} is invalid , please go to the settings and update it then try again`
                            
                            openProcessModal(unauhorizationIcon,title,msg)

                        
                        }else if(data.server_request_exception_error){
                            let title  = 'server request exception error'
                            let msg = data.server_request_exception_error
                            openProcessModal(networkIcon,title,msg)

                        }

                        // HANDLE RESULTS DATA
                        else{
                            // SET THE RESULT DATA FOR THE POPUP 
                            setResultPopupData({
                                title:data.results.length +'/'+data.progress.orders_to_be_monitored+' order(s) were updated',
                                orders:data.results,
                                old_monitor_orders_len:data.progress.orders_to_be_monitored,
                                conv_errors : data.conv_errors
                            })
            
                            // LOAD THE RESULT POPUP
                            setResultPopupShowed(true)
                            // RESET THE LOADING PAGE 
                            setIsLoading(false)
                            // RESET THE PROGRESS
                            setProgress(null)

                        }
                        

                        // CLEAR THE INTERVAL 
                        clearInterval(intv)

                    }else if(data.progress){
                        setProgress(data.progress)
                    }
                    req_done = true
                })
            }
        },5000)
        setMonitorIntv(intv)
    }
    
    const monitorOrders = ()=>{
        setIsLoading(true)
        setLoadingActionTxt('monitoring orders')
        axios.post(API_ENDPOINT+'/orders_monitoror/launch').then(res=>{
            let orders_monitoror_id = res.data.orders_monitoror_id
            monitorMonitoringOrders(orders_monitoror_id)
        })
    }
    const getDashboardData = ()=>{

        let dashboardData = {
            'afex orders'  : 0,
            'afex orders en cours de préparations' : 0,
            'afex orders expédiés' : 0,
            'loxbox orders'  : 0,
            'loxbox orders en cours de préparations' : 0,
            'loxbox orders expédiés' : 0,
        }

        orders.map(order=>{
            if(order.carrier == 'LOXBOX'){
                dashboardData['loxbox orders']  += 1 
                if (order.state == 'En cours de préparation'){
                    dashboardData['loxbox orders en cours de préparations']  += 1 
                }else{
                    dashboardData['loxbox orders expédiés']  += 1 
                }
            }else{
                dashboardData['afex orders']  += 1 
                if (order.state == 'En cours de préparation'){
                    dashboardData['afex orders en cours de préparations']  += 1 
                }else{
                    dashboardData['afex orders expédiés']  += 1 
                }
            }
            
        })

        return dashboardData
    }
    let dashboardData = getDashboardData()

    return(
        !isLoading ? 
        <>
        {orders.length ?
            <div class='order-monitoror'>
                
                <div style={{width:'100%'}}>
                    <p className='order-monitoror-title'>{orders.length} order(s) to monitor</p>
                    <Dashboard dashboardData={dashboardData} kpi_item_nb_fontSize = '20px' kpi_item_width='33%' kpi_item_margin_direction='Bottom'/>
                    <GenericTable keys={order_keys} orders={orders} maxHeight='70vh' margin='5px 0px 15px 0px' />
                    <button className='order-monitoror-monitor-btn' onClick={monitorOrders} >monitor order(s)</button>
                    <GenericModal type='result' size='lg' show={isResultPopupShowed} 
                                title={resultPopupData.title} closeModal={closeOrderMonitoror}
                                result_content={<ResultPopupContent resultPopupData={resultPopupData}   />} />
                </div> 
            
            </div> 
        
        :<div className='no-order-monitoror'>
            <i className="fas fa-shopping-cart"></i> 
            <p>no orders to monitor</p>
        </div>
            
        }</>
        :<> 
            <LoadingPage action_txt={loadingActionTxt} done_action_txt='were monitored' progress={progress} />
            <GenericModal show={isProcessModalShowed}  type='alert' title={processAlertData.title}
                         alertData={processAlertData} closeModal={closeProcessModal} />
        </>
    )
}

export default OrderMonitoror