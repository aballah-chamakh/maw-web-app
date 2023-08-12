import {useState,useEffect} from 'react' ;
import axios from 'axios' ;
import { useNavigate,useLocation } from 'react-router-dom';
import './OrderLoader.scss' ;
import OrderLoaderForm from './OrderLoaderForm/OrderLoaderForm';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import GenericModal from '../../CommonComponents/GenericModal/GenericModal';
import { API_ENDPOINT,networkIcon,unauhorizationIcon } from '../../../globals';


//fas fa-fingerprint
const OrderLoader = (props)=>{
    // CONSTANT ALERTS DATA fas fa-exclamation-triangle	
    const infoAlertData = {title:'info',icon : <i style={{color:'#101B82',fontSize:'45px'}} class="material-icons">info</i> , msg : 'no orders to load from mawlety.com given the date range'} ;
    const restrictedAlertData = {title:'restricted',icon:<i style={{color:'#D81010'}} className='fas fa-minus-circle'></i>,msg:"it's restricted to load orders while the lowbox areas selector process is running"};
    const successAlertData = {title:'success',icon:<i style={{color:'#28C20F'}} className="fas fa-check-circle"></i>,msg:"order(s) were submitted"};
    // CONSTANT ICONS 
    const exceptionIcon = <i style={{color:'#D81010'}} className="fas fa-exclamation-triangle"></i>

    const [lastUndoneStepChecked,setLastUndoneStepChecked] = useState(false)
    const [isLoading,setIsLoading] = useState(true)
    const [actionTxt,setActionTxt] = useState("checking if the last orders loader finished")
    const [progress,setProgress] = useState(null)
    const [isInfoModalShowed,setInfoModalShowed] = useState(false)
    const [isRestrictedModalShowed,setRestrictedModalShowed] = useState(false)
    const [isSuccessModalShowed,setSuccessModalShowed] = useState(false)
    const [isProcessModalShowed,setProcessModalShowed] = useState(false)
    const [nbDaysAgo,setNbDaysAgo] = useState(0)
    const [startDate,setStartDate] = useState(new Date())
    const [endDate,setEndDate] = useState(new Date())
    const [intv,setIntv] = useState(null )
    const [processAlertData,setProcessAlertData] = useState({title:'exception error',icon:exceptionIcon,msg:"HTTPSConnectionPool(host='mawlety.com', port=443): Max retries exceeded with url: /api/orders/?filter%5Bdate_add%5D=%5B2023-02-05,2023-02-06%5D&filter%5Bcurrent_state%5D=%5B3%5D&display=%5Bid,%20total_paid,%20id_carrier,%20transaction_id,%20address_detail,%20customer_detail,%20cart_products,%20current_state,%20date_add%5D&date=1 (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x000001DDEA98C970>: Failed to establish a new connection: [Errno 11001] getaddrinfo failed'))"} )
    const navigate = useNavigate()
    const location = useLocation()



    

    //alert("location.state : "+location.state)
    useEffect(()=>{
        //SHOW THE SUCCESS MODAL FOR THE LAST SUCCESSFULL SUBMITTING LAUNCH 
        // NOTE 1 : WE DON'T NEED TO CHECK IF THERE IS A REDIRECTION BECAUSE THE LAST SUBMITTING LAUNCH WAS SUCCESSFULL 
        // NOTE 2 : WHEN THE SUCCESS OF THE POPUP WILL BE CLOSED THE LOCATION STATE WILL CLEARED IN THE CLOSE HANDLER FUNCTION OF THE POPUP
        if(location.state){
            setIsLoading(false)
            //alert('success')
            if (location.state.submitted_orders_len){
                setSuccessModalShowed(true)
                openSuccessModal()
            }else if(location.state.unauthorization_error){ //INVALID_LOXBOX_AND_MAWL_API_KEY'
                let splitted_unauthorization = location.state.unauthorization_error.split('_')
                let title  = ''
                let msg = ''
                let unauthorization_party = splitted_unauthorization[1].toLowerCase()
                // HANDLE THIS STRUCTURE "INVALID_LOXBOX_AND_MAWLETY_API_KEY"
                if(location.state.unauthorization_error.includes('AND')){
                    let order_id = splitted_unauthorization.at(-1)
                    title = `${unauthorization_party} and mawlety unauhorization error`
                    msg = `the api keys of ${unauthorization_party} and mawlety are invalid , please go to the settings and update them then go to mawlety back office and set the state of the order with the id ${order_id} back to "Validé" then try again`
                }else{// HANDLE THIS STRUCTURE "INVALID_LOXBOX_API_KEY"
                    
                    let unauthorization_element = splitted_unauthorization[2] == 'API' ? 'api key' : 'credentials'
                    title = `${unauthorization_party} unauhorization error`
                    msg = `the ${unauthorization_element} of ${unauthorization_party} is invalid , please go to the settings and update it `
                    // HANDDLE  THIS CASE // INVALID_AFEX_CREDENTIALS_WHILE_MANIFESTING
                    if(splitted_unauthorization.at(-1) == 'MANIFESTING'){
                        msg += 'then go to the site of afex and manifest manually the recently created orders'
                    }else{
                        msg += 'then try again'
                    }
                }
                openProcessModal(unauhorizationIcon,title,msg)
            }else if(location.state.exception_error){
                // THE_MANIFEST_REQUEST_NOT_WORKING
                // NOTE : FOR NOW WE ARE ONLY HANDLING THE MANIFEST PROBLEM LATER WE MAY OTHER EXCEPTIONS  
                let title = "THE MANIFEST PROCESS IS NOT WORKING" 
                let msg = "the manifest process is not working any more , please go to the site of afex and manifest manually the recently created orders then ask abdallah to update the software for you"
                openProcessModal(exceptionIcon,title,msg)
            }else if(location.state.server_request_exception_error){
                let title  = 'server request exception error'
                let msg = location.state.server_request_exception_error
                openProcessModal(networkIcon,title,msg)
            }


        }else{
            //alert('check redirection ')
            // CHECK IF THERE IS A REDIRECTION TO DO 
            if (lastUndoneStepChecked == false){ // TO NOT MAKE THE CHECK AGAIN THE INTV IS UPDATED 
                //alert('really check redirection ')
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
    },[intv,location])

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

    const openProcessModal = (icon,title,msg)=>{
        setProcessModalShowed(true) ;
        setProcessAlertData(prevUnauthorizationAlert=>{
            let newUnauthorizationAlert = {...prevUnauthorizationAlert}
            newUnauthorizationAlert['icon'] = icon 
            newUnauthorizationAlert['title'] = title
            newUnauthorizationAlert['msg'] = msg 
            return newUnauthorizationAlert
        })
    }

    const closeProcessModal = ()=>{
        setProcessModalShowed(false) ;
        navigate(location.pathname, { replace: true });
         
    }



    const closeSuccessModal = ()=>{
        setSuccessModalShowed(false)
        // CLEAR THE LOCATION STATE 
        // NOTE 1 : WE ARE CLEARING THE STATE OF THE LOCATION IN TIMEOUT TO NOT MAKE THE POPUP DISAPEAR WITH 0 
        // TECHNICALLY WE ARE CLEARING STATE OF THE LOCATION IN ANOTHER RENDER CYCLE OTHER THAN THE ONE THAT WILL 
        // CAUSE THE POPUP TO DISAPEAR 
        // NOTE 2 :  THE CLEARING THE STATE OF THE LOCATION IN A TIMEOUT MAY CAUSE REPLACEMENT OF ANOTHER NAVIGATION 
        // IF THE USER GO TO ANOTHER PATH AFTER HE CLICK THE CLOSE BTN OF THE POPUP WITHIN 100ms , AND THIS IS NOT A BIG PROBLEM
        // BECAUSE  : 
        // RARELY WHEN THIS WILL HAPPEN BECAUSE HE MUST GO TO ANOTHER PATH WITHIN ONLY 100ms 
        // EVEN IF THIS HAPPENED , EVENTUALLY ONE TIME HE WILL GO TO ANOTHER PATH AFTER THE 100 SECOND
        // AND REPLACE THE NAVIGATION 

           
        setTimeout(()=>{
           navigate(location.pathname, { replace: true });
        },500)
        
    }

    const openSuccessModal = ()=>{
        setSuccessModalShowed(true)
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
                    
                    // OPEN THE INFO MODAL IF WE HAVE NO ORDERS TO LOAD 
                    if(data.orders.length == 0 && data.invalid_orders.length == 0){
                        if(data.unauthorization_error == 'INVALID_MAWLETY_API_KEY'){
                            let title = "mawlety unauhorization error"
                            let msg = "the api key of mawlety is invalid , please go to the settings and update it then try again"
                            openProcessModal(unauhorizationIcon,title,msg)
                        }else if(data.server_request_exception_error){
                            let title  = 'server request exception error'
                            let msg = data.server_request_exception_error
                            openProcessModal(networkIcon,title,msg)
                        }
                        else{
                            openInfoModal() ;
                        }
                        
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

    const date_to_str = (date)=>{
        // '%Y-%m-%d'
        return `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`
    }

    const loadOrders = ()=>{
        // SET THE LOADING PAGE 
        setIsLoading(true)
        setActionTxt("loading orders")

        // LAUNCH THE ORDERS LOADER 
        let firstDateStr = date_to_str(startDate)
        let endDateStr = date_to_str(endDate)
        let date_range = {start_date: firstDateStr,  end_date: endDateStr}
 
        axios.post(API_ENDPOINT+'/orders_loader/launch',{date_range:date_range}).then(res=>{
          let data = res.data 
          // HANDLE THE RESCTRICTION + RESET STATES 
          if (data.hasOwnProperty('restriction_msg')){
            setIsLoading(false)
            openRestrictedModal()
            return  ;
          }
          // MONITOR THE ORDER LOADER 
          let orders_loader_id = res.data.orders_loader_id
          monitor_loading_orders_progress(orders_loader_id)
          

        })
    }

    return(
        <>
        {!isLoading ? 
        <div class="order-loader-container">
           
            <OrderLoaderForm loadOrders={loadOrders} setStartDate={setStartDate} setEndDate={setEndDate} startDate={startDate} /> 
            <GenericModal show={isInfoModalShowed}  type='alert' title={infoAlertData.title} alertData={infoAlertData} closeModal={closeInfoModal} />
            <GenericModal show={isRestrictedModalShowed}  type='alert' title={restrictedAlertData.title} alertData={restrictedAlertData} closeModal={closeRestrictedModal} />
            <GenericModal show={isSuccessModalShowed}  type='alert' title={successAlertData.title} alertData={successAlertData} orders_len={location.state ? location.state.submitted_orders_len : 0 } closeModal={closeSuccessModal} />
            <GenericModal show={isProcessModalShowed}  type='alert'  title={processAlertData.title} alertData={processAlertData} closeModal={closeProcessModal} />
        </div> : 
        <LoadingPage progress={progress} action_txt={actionTxt} done_action_txt="were loaded"  />}</>

    )
}
export default OrderLoader ;

