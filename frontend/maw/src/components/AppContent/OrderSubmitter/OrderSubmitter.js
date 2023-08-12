import './OrderSubmitter.scss' ;
import {useState,useEffect} from 'react' ;
import { useNavigate,useParams,useLocation} from 'react-router-dom';
import axios from 'axios' ;
import { API_ENDPOINT } from '../../../globals';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import GenericTable from '../../CommonComponents/GenericTable/GenericTable';
import ServerLoading from '../../CommonComponents/ServerLoading/ServerLoading';
import Dashboard from '../../CommonComponents/Dashboard/Dashboard';


const OrderSubmitter = (props)=>{
    const [isLoading,setIsLoading] = useState(true)
    const [didMount,setDidMount] = useState(false)
    const [loadingActionTxt,setLoadingActionTxt] = useState('loading orders to submit')
    const [submittingProgress,setSubmittingProgress] = useState(null) //{'current_order_id' : 1000 ,'submitted_orders_len' :  0,'orders_to_be_submitted': 100,'carrier':'afex'})
    const [isServerLoading,setServerIsLoading] = useState(false)
    const [loadingServerTxt,setLoadingServerTxt] = useState('selecting or deselecting order(s)')
    const [orders,setOrders] = useState([])
    const [invalidOrders,setInvalidOrders] = useState([])
    const [ordersSelectedAll,setOrdersSelectedAll] = useState(false)
    const [monitorIntv,setMonitorIntv] = useState(null)
    const [selectorIntv,setSelectorIntv] = useState(null)



    const navigate = useNavigate()
    const location = useLocation()
    const {orders_loader_id}  = useParams()

    const order_keys = ['selected','id','created_at','firstname','city','delegation','locality','carrier']
    
    const invalid_order_keys = ['order_id','created_at','invalid_fields']
    const invalid_order_highlight_keys = {'invalid_fields':'#D33C3C'}

    const dropdown_keys = {
        'carrier' : ['AFEX','LOXBOX']
    }   


    useEffect(()=>{
       // alert("CALL THE USE EFFECT "+selectorIntv)
        if (didMount  == false){
            setDidMount(true)
        
            // MONITORING THE PREGRESS OF SUBMITTING OF THE LAST ORDERS SUBMITTER 
            if(location.state){
                let orders_submitter_id = location.state.orders_submitter_id 
                setIsLoading(true)
                setLoadingActionTxt('submitting orders')
                monitorSubmittingOrders(orders_submitter_id)

            } // LOAD THE ORDERS FROM THE SERVER GIVEN THE orders_loader_id
            else if(orders_loader_id) { 
                        // GRAB THE ORDERS TO SUBMIT OR KEEP MONITORING UNTIL THE SELECTOR IS DONE THEN GRAB THE ORDERS 
                        let intv = setInterval(()=>{
                            axios.get(API_ENDPOINT+'/orders_loader/'+orders_loader_id+'/monitor').then(res=>{

                                let data = res.data 
                                let is_selector_working = data.is_selector_working
                                let orders = data.orders 
                                let invalid_orders = data.invalid_orders 
                                let orders_selected_all = data.orders_selected_all
                                
                                // ONCE THE SELECTOR IS DONE DO THE FOLLOWING 
                                if(!is_selector_working){
                                    // UPDATE THE ORDERS 
                 
                                    setOrders(orders)
                                    setInvalidOrders(invalid_orders)
                                    setOrdersSelectedAll(orders_selected_all)
                                    
                                    // HIDE THE SERVER IS LOADING INTERFACE IF EXIST 
                                    setServerIsLoading(false)
                                    // REMOVE THE LOADING IF EXIST 
                                    setIsLoading(false)
                                    
                                    // CLEAR THE INTERVAL 
                                    clearInterval(intv)
                                }else if(isServerLoading == false){ // WHEN THE THE SELECTOR IS WORKING AND THE SERVER LOADING SPINNER WAS NOT SAT 
                                    setOrders(orders)
                                    setOrdersSelectedAll(orders_selected_all)
                                    // REMOVE THE LOADING 
                                    setIsLoading(false)

                                    // SET THE SERVER IS LOADING 
                                    setServerIsLoading(true)
                                }

                            })

                        },3000)
                        setSelectorIntv(intv)
            }
        }
        return ()=>{
            //alert("clean up "+monitorIntv)
            if(selectorIntv){
                clearInterval(selectorIntv)
            }

            if(monitorIntv){
                clearInterval(monitorIntv)
            }
        }
    },[orders_loader_id,monitorIntv,selectorIntv])

    const handleSelectChange = (e)=>{
        // SET SERVER LOADING 
        setServerIsLoading(true)

        

        // GRAB THE TARGETED CHECKBOX ELEMENT 
        let checkbox = e.target 

        // HANDLE SINGLE ORDER CHECKBOX
        if(checkbox.name.includes('order')){
            // EXTRACT ORDER ID FROM THE CHECKBOX NAME 
            let order_id = parseInt(checkbox.name.split('_')[1])

            // ADD ADDITUONAL ACTIONS IF THEY EXIST IN THE SELECTED AND DESELECT CASE
            let additional_action = ''
            if (checkbox.checked){
                additional_action = 'selected_all'
                orders.every(order => {
                    console.log(order.selected==false && order.id != order_id)
                    if(order.selected==false && order.id != order_id){
                        additional_action = '' 
                        return false 
                    }
                    return true 
                })  
            }else{
                if(ordersSelectedAll){
                    additional_action = 'remove_selected_all'
                }
            }
            console.log(additional_action)
            
            // TOGGLE THE ORDER SELECTION IN THE SERVER
            axios.put(API_ENDPOINT+'/toggle_order_selection',{orders_loader_id:orders_loader_id,order_id:order_id,additional_action:additional_action}).then(res=>{
                // TOGGLE THE ORDER SELECTION IN THE FRONT
                setOrders(prevOrders=>{
                    let newOrders = [...prevOrders]
                    newOrders.every(order => {
                        if(order.id==order_id){
                            order.selected = !order.selected  ;
                            return false 
                        }
                        return true 
                    })  
                    return newOrders ;
                })
                // HANDLE ADDITIONAL ACTION IF IT EXIST IN THE FRONT
                if (additional_action){
                    if(additional_action == 'selected_all'){
                        setOrdersSelectedAll(true)
                    }else{
                        setOrdersSelectedAll(false)
                    }
                }
                // DISABLE SERVER LOADING
                setServerIsLoading(false)
            })
        }else{ // HANDLE SELECT OR UNSELECT ALL ORDERS CHECKBOX 
            let checked = checkbox.checked 
            let action = checked ? 'select_all' : 'unselect_all' ;

            axios.put(API_ENDPOINT+'/select_unselect_all_orders',{orders_loader_id:orders_loader_id,action:action}).then(res=>{
                // HANDLE THE ACTION IN THE FRONT 
                setOrders(prevOrders=>{
                    let newOrders = [...prevOrders]
                    newOrders.forEach(order => {
                        order.selected = checked;
                    })  
                    return newOrders ;
                })
                setOrdersSelectedAll(checked)

                // DISABLE SERVER LOADING
                setServerIsLoading(false)
                
            })

        }
    }
    const handleDropdownChange = (e)=>{
        // SET SERVER LOADING 
        setServerIsLoading(true)
        setLoadingServerTxt('updating the carrier of an order')

        let selectEl = e.target 
        let order_id =  parseInt(selectEl.name.split('_')[2])
        let carrier = selectEl.value 

        // UPDATE THE CARRIER OF THE ORDER IN THE SERVER
        axios.put(API_ENDPOINT+'/set_order_carrier',{orders_loader_id:orders_loader_id,order_id:order_id,carrier:carrier}).then(res=>{
            
            // UPDATE THE CARRIER OF THE ORDER IN THE FRONT
            setOrders(prevOrders=>{
                let newOrders = [...prevOrders]
                newOrders.every(order => {
                    if(order.id==order_id){
                        order.carrier = carrier  ;
                        return false 
                    }
                    return true 
                })  
                return newOrders ;
            })

            // REMOVE SERVER LOADING 
            setServerIsLoading(false)
            setLoadingServerTxt('selecting or deselecting order(s)')

        })

    }
    
    const cancelOrderLoader = ()=>{
        setServerIsLoading(true)
        setLoadingServerTxt('canceling ...')
        axios.put(API_ENDPOINT+'/orders_loader/'+orders_loader_id+'/cancel').then(res=>{
           
            navigate('/load_orders')
        })
    }
    const monitorSubmittingOrders = (orders_submitter_id)=>{
        let req_is_done = true  
        let intv = setInterval(()=>{
            if(req_is_done){
                req_is_done = false 
                axios.get(API_ENDPOINT+'/orders_submitter/'+orders_submitter_id+'/monitor').then((res)=>{
                    let data = res.data 
                    if(data.progress){
                        setSubmittingProgress(data.progress)
                    }
                    if(data.state=='FINISHED'){
                        let state = { }
                        if(data.unauthorization_error ){
                            state = {unauthorization_error : data.unauthorization_error}
                        }
                        else if(data.server_request_exception_error){
                            state = {server_request_exception_error : data.server_request_exception_error}
                        }
                        else if(data.exception_error){
                            state = {exception_error : data.exception_error}
                        }
                        else{
                            state = {submitted_orders_len: data.progress.orders_to_be_submitted}
                        }
                        
                        navigate('/load_orders',{state:state})
                        clearInterval(intv)
                    }
                    req_is_done = true  
                })
            }

        },5000)
        setMonitorIntv(intv)
    }
    const getOrdersToSubmitDashboardData = ()=>{
        let ordersToSubmitDashboardData ={
            'valid orders': orders.length,
            'valid afex orders':0,
            'valid loxbox orders':0,
            'invalid orders':invalidOrders.length
        }
        orders.map(order=>{
            if(order.carrier =='AFEX'){
                ordersToSubmitDashboardData['valid afex orders'] +=1
            }else{
                ordersToSubmitDashboardData['valid loxbox orders'] +=1
            }
        })
        return ordersToSubmitDashboardData
    } 
    const submitOrders = ()=>{
        setIsLoading(true)
        setLoadingActionTxt('submitting orders')
        axios.post(API_ENDPOINT+'/orders_submitter/launch',{orders_loader_id:orders_loader_id}).then((res)=>{
            let orders_submitter_id = res.data.orders_submitter_id 
            monitorSubmittingOrders(orders_submitter_id)

        })
    }

    return(

        !isLoading ? 
            <div className='order-submitter'>

                <p className='order-submitter-title'>order(s) to submit to carrier(s)</p>

                <Dashboard dashboardData={getOrdersToSubmitDashboardData()} kpi_item_width={'24.5%'} kpi_item_nb_fontSize={'25px'} kpi_item_margin_value='15'  />
                {invalidOrders.length  ?
                    <div className='order-submitter-card'>
                    <p className='order-submitter-card-title'>{invalidOrders.length} invalid order(s) </p>
                    <GenericTable  keys={invalid_order_keys} orders={invalidOrders} maxHeight='75vh' highlight_keys={invalid_order_highlight_keys} fontSize={'15px'} />
                </div> : null}
                
                {orders.length ? 
                    <div className='order-submitter-card'>
                    <p className='order-submitter-card-title'>{orders.length} valid order(s) </p>
                    <GenericTable fontSize={'15px'}  keys={order_keys} orders={orders} ordersSelectedAll={ordersSelectedAll} dropdown_keys={dropdown_keys} handleDropdownChange={handleDropdownChange} maxHeight='75vh' handleSelectChange={handleSelectChange}/>
                    <div className='order-submitter-card-actions'>
                        <button className='order-submitter-card-actions-submit' onClick={submitOrders}>submit to carriers</button>
                        <button className='order-submitter-card-actions-cancel' onClick={cancelOrderLoader}>cancel</button>
                    </div>
                </div> : null}

                <ServerLoading show={isServerLoading} title={loadingServerTxt} />
              
            </div>
        :
        <LoadingPage progress={submittingProgress} action_txt={loadingActionTxt} done_action_txt="were submitted"  />
    
    )
}
export default OrderSubmitter