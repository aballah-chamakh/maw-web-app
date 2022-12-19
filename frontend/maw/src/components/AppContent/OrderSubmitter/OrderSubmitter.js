import './OrderSubmitter.scss' ;
import {useState,useEffect} from 'react' ;
import { useNavigate,useParams } from 'react-router-dom';
import axios from 'axios' ;
import { API_ENDPOINT } from '../../../globals';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import GenericTable from '../../CommonComponents/GenericTable/GenericTable';
import ServerLoading from '../../CommonComponents/ServerLoading/ServerLoading';


const OrderSubmitter = (props)=>{
    const [isLoading,setIsLoading] = useState(true)
    const [loadingActionTxt,setLoadingActionTxt] = useState('loading orders to submit')
    const [submittingProgress,setSubmittingProgress] = useState(null)
    const [isServerLoading,setServerIsLoading] = useState(false)
    const [orders,setOrders] = useState([])
    const [ordersSelectedAll,setOrdersSelectedAll] = useState(false)



    const navigate = useNavigate()
    const {orders_loader_id}  = useParams()

    const order_keys = ['selected','id','first and last name','city','delegation','locality','carrier']
    
    const dropdown_keys = {
        'carrier' : ['AFEX','LOXBOX']
    }

    useEffect(()=>{
       // LOAD THE ORDERS FROM THE SERVER GIVEN THE orders_loader_id
       if(orders_loader_id) { 
            axios.get(API_ENDPOINT+'/orders_loader/'+orders_loader_id+'/monitor').then(res=>{
                // SET THE ORDERS AND THEIR SELECTED ALL STATE
                let data = res.data
                // REDIRECT TO LOADING ORDERS WHEN THE ORDER LOADER IS CANCELED
                if (data.canceled){
                    navigate('/load_orders')
                }
                let orders = data.orders  
                let orders_selected_all = data.orders_selected_all
                setOrders(orders)
                setOrdersSelectedAll(orders_selected_all)
                // REMOVE THE LOADING 
                setIsLoading(false)

                // CHECK IF THE SELECTOR IS WORKING 
                if(res.data.is_selector_working){
                    
                    // SET THE SERVER IS LOADING 
                    setServerIsLoading(true)

                    // KEEP MONITORING UNTIL THE SELECTOR IS DONE 
                    let intv = setInterval(()=>{
                        axios.get(API_ENDPOINT+'/orders_loader/'+orders_loader_id+'/monitor').then(res=>{
                            let data = res.data 
                            let is_selector_working = data.is_selector_working

                            // ONCE THE SELECTOR IS DONE DO THE FOLLOWING 
                            if(!is_selector_working){
                                // UPDATE THE ORDERS 
                                let orders = data.orders 
                                let orders_selected_all = data.orders_selected_all
                                setOrders(orders)
                                setOrdersSelectedAll(orders_selected_all)
                                
                                // HIDE THE SERVER IS LOADING INTERFACE
                                setServerIsLoading(false)

                                // CLEAR THE INTERVAL 
                                clearInterval(intv)
                            }

                        })

                    },3000)

                }
            })
        }
    },[orders_loader_id])

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

            // SET SERVER LOADING 
            setServerIsLoading(false)

        })

    }
    
    const cancelOrderLoader = ()=>{
        setServerIsLoading(true)
        axios.put(API_ENDPOINT+'/orders_loader/'+orders_loader_id+'/cancel').then(res=>{
           
            navigate('/load_orders')
        })
    }

    const submitOrders = ()=>{
        setIsLoading(true)
        setLoadingActionTxt('submitting orders')
        axios.post(API_ENDPOINT+'/orders_submitter/launch',{orders_loader_id:orders_loader_id}).then((res)=>{
            let orders_submitter_id = res.data.orders_submitter_id 
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
                            navigate('/load_orders',{state:{submitted_orders_len:data.progress.orders_to_be_submitted}})
                            clearInterval(intv)
                        }
                        req_is_done = true  
                    })
                }

            },5000)
        })
    }

    return(

        !isLoading ? 
            <div className='order-submitter'>

                <p className='order-submitter-title'>{orders.length} order(s) to submit to carrier(s)</p>

                <GenericTable  keys={order_keys} orders={orders} ordersSelectedAll={ordersSelectedAll} dropdown_keys={dropdown_keys} handleDropdownChange={handleDropdownChange} maxHeight='75vh' handleSelectChange={handleSelectChange}/>
                
                <div className='order-submitter-actions'>
                    <button className='order-submitter-actions-submit' onClick={submitOrders}>submit to carriers</button>
                    <button className='order-submitter-actions-cancel' onClick={cancelOrderLoader}>cancel</button>
                </div>
                <ServerLoading show={isServerLoading} />
            </div>
        :
        <LoadingPage progress={submittingProgress} action_txt={loadingActionTxt} done_action_txt="were submitted"  />
    
    )
}
export default OrderSubmitter