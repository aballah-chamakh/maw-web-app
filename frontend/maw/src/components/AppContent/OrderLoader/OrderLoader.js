import {useState,useEffect} from 'react' ;
import axios from 'axios' ;
import { useNavigate,useLocation } from 'react-router-dom';
import './OrderLoader.scss' ;
import OrderLoaderForm from './OrderLoaderForm/OrderLoaderForm';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import GenericModal from '../../CommonComponents/GenericModal/GenericModal';
import { API_ENDPOINT } from '../../../globals';

const infoAlertData = {title:'info',icon : <i style={{color:'#101B82',fontSize:'45px'}} class="material-icons">info</i> , msg : 'no orders to load from mawlety.com given the number of days ago '} ;
const restrictedAlertData = {title:'restricted',icon:<i style={{color:'#D81010'}} className='fas fa-minus-circle'></i>,msg:"it's restricted to load orders while the lowbox areas selector process is running"};
const successAlertData = {title:'success',icon:<i style={{color:'#28C20F'}} className="fas fa-check-circle"></i>,msg:"order(s) were submitted"};

const OrderLoader = (props)=>{
    const [lastUndoneStepChecked,setLastUndoneStepChecked] = useState(false)
    const [isLoading,setIsLoading] = useState(true)
    const [actionTxt,setActionTxt] = useState("checking if the last orders loader finished")
    const [progress,setProgress] = useState(null)
    const [isInfoModalShowed,setInfoModalShowed] = useState(false)
    const [isRestrictedModalShowed,setRestrictedModalShowed] = useState(false)
    const [isSuccessModalShowed,setSuccessModalShowed] = useState(false)
    const [nbDaysAgo,setNbDaysAgo] = useState(0)
    const [intv,setIntv] = useState(null )

    const navigate = useNavigate()
    const location = useLocation()

   
    

    useEffect(()=>{
        // SHOW THE SUCCESS MODAL FOR THE LAST SUCCESSFULL SUBMITTING LAUNCH 
        // NOTE : WE DON'T NEED TO CHECK IF THERE IS A REDIRECTION BECAUSE THE LAST SUBMITTING LAUNCH WAS SUCCESSFULL 
        if(location.state && location.state.submitted_orders_len){
            setActionTxt("loading orders")
            setIsLoading(false)
            setSuccessModalShowed(true)
        }else{
            // CHECK IF THERE IS A REDIRECTION TO DO 
            if (lastUndoneStepChecked == false){ // TO NOT MAKE THE CHECK AGAIN THE INTV IS UPDATED 
                setLastUndoneStepChecked(true)
                axios.get(API_ENDPOINT+'/get_last_undone_step_of_the_last_order_loader').then((res)=>{
                    let data = res.data
                    let undone_step = data.undone_step
                    
                   
                    
                    /*
                    if last_orders_loader_obj.state['state'] == 'working' : 
                    undone_step = "SHOW_ORDERS_LOADER_PROGRESS"
                    elif last_orders_loader_obj.state['canceled'] == False and  last_orders_loader_obj.get_orders_submitter_state() == None : 
                        undone_step = "SHOW_ORDERS_TO_SUBMIT"
                    elif last_orders_loader_obj.state['canceled'] == False and  last_orders_loader_obj.get_orders_submitter_state() == "working": 
                        undone_step = "SHOW_ORDERS_SUBMITTER_PROGRESS" 
                    */
                    switch(undone_step){
    
                        case "SHOW_ORDERS_LOADER_PROGRESS" : 
                            setActionTxt("loading orders")
                            monitor_loading_orders_progress( data.orders_loader_id)
                        break 
                        case "SHOW_ORDERS_TO_SUBMIT" : 
                            navigate('/load_orders/'+data.orders_loader_id+'/submit_orders')
                        break 
                        case "SHOW_ORDERS_SUBMITTER_PROGRESS" : 
                            navigate('/load_orders/'+data.orders_loader_id+'/submit_orders',{state:{orders_submitter_id : data.orders_submitter_id}})
                        break 
                        case "" : 
                            setIsLoading(false)
                        break 

                    }
                })
            }
        }

        return ()=>{
          
            if(intv){
                clearInterval(intv)
            }
        }
    },[location,intv])

    const closeInfoModal = ()=>{
        setInfoModalShowed(false) ;
    }

    const openInfoModal = ()=>{
        setInfoModalShowed(true) ;
    }

    const closeRestrictedModal = ()=>{
        setRestrictedModalShowed(false) ;
    }

    const openRestrictedModal = ()=>{
        setRestrictedModalShowed(true) ;
    }

    const closeSuccessModal = ()=>{
        setSuccessModalShowed(false)
        setTimeout(()=>{
            navigate(location.pathname, { replace: true });
        },500)
        
    }

    const monitor_loading_orders_progress = (orders_loader_id)=>{
        // INITIATE THE REQ STATE 
        // THIS VAR WILL MAKE SURE THAT WE ARE NOT LOADING A NEW REQ BEFORE THE EXISTINF REG IS DONE 
        // THIS WILL PREVENT THE CASE OF A NEW REQ FINISH BEFORE THE OLD REQ IN THIS CASE WE WILL HAVE 
        // THE PROGRESS DATA HAVE THE NEW DATA THEN THE OLD DATA 
        let req_is_done = true  

        const monitor_loading_progress_intv = setInterval(()=>{
        // CHECK IF THE PREVIOUS REQUEST IS DONE 
        if(req_is_done){
            // SET THE CURRENT REQUEST NOT DONE YET
            req_is_done = false 

            axios.get(API_ENDPOINT+'/orders_loader/'+orders_loader_id+'/monitor').then(res=>{
                let data = res.data  ;

                // UPDATE THE PROGRESS DATA 
                if(data.progress){
                    console.log('set progress')
                    setProgress(data.progress)
                }

                // CHECK IF THE ORDERS LOADER IS FINISHED 
                if(data.state == 'FINISHED'){
                    console.log('finished')
                    
                    // RESET STATES 
                    setIsLoading(false)
                    setProgress(null)
                    setNbDaysAgo(0)
                    
                    // OPEN THE INFO MODAL IF WE HAVE NO ORDERS TO LOAD 
                    if(data.orders.length == 0){
                        openInfoModal() ;
                    }else{
                        navigate('/load_orders/'+orders_loader_id+'/submit_orders')

                    }
                    console.log('clear interval')
                    // CLEAR THE MONITORING INTERVAL 
                    clearInterval(monitor_loading_progress_intv)
                }

                // SET THE CURRENT REQUEST TO DONE 
                req_is_done = true 
            })
        }
        },5000)
        setIntv(monitor_loading_progress_intv)
    } 

    const loadOrders = ()=>{
        // SET THE LOADING PAGE 
        setIsLoading(true)
        setActionTxt("loading orders")

        // LAUNCH THE ORDERS LOADER 
        axios.post(API_ENDPOINT+'/orders_loader/launch',{ days_ago: nbDaysAgo }).then(res=>{
          let data = res.data 

          // HANDLE THE RESCTRICTION + RESET STATES 
          if (data.hasOwnProperty('restriction_msg')){
            setIsLoading(false)
            openRestrictedModal()
            setNbDaysAgo(0)
            return  ;
          }

          // MONITOR THE ORDER LOADER 
          let orders_loader_id = res.data.orders_loader_id
          monitor_loading_orders_progress(orders_loader_id)
          

        })
    }

    return(

        !isLoading ? 
        <div class="order-loader-container">
            <OrderLoaderForm nbDaysAgo={nbDaysAgo} setNbDaysAgo={setNbDaysAgo} loadOrders={loadOrders} /> 
            <GenericModal show={isInfoModalShowed}  type='alert' title={infoAlertData.title} alertData={infoAlertData} closeModal={closeInfoModal} />
            <GenericModal show={isRestrictedModalShowed}  type='alert' title={restrictedAlertData.title} alertData={restrictedAlertData} closeModal={closeRestrictedModal} />
            <GenericModal show={isSuccessModalShowed}  type='alert' title={successAlertData.title} alertData={successAlertData} orders_len={location.state ? location.state.submitted_orders_len : 0 } closeModal={closeSuccessModal} />
        </div> : 
        <LoadingPage progress={progress} action_txt={actionTxt} done_action_txt="were loaded"  />

    )
}
export default OrderLoader ;

