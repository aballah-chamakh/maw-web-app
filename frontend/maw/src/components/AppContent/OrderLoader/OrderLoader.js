import {useState} from 'react' ;
import axios from 'axios' ;
import { useNavigate } from 'react-router-dom';
import './OrderLoader.scss' ;
import OrderLoaderForm from './OrderLoaderForm/OrderLoaderForm';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import GenericModal from '../../CommonComponents/GenericModal/GenericModal';
import { API_ENDPOINT } from '../../../globals';

const infoAlertData = {title:'info',icon : <i style={{color:'#101B82',fontSize:'45px'}} class="material-icons">info</i> , msg : 'no orders to load from mawlety.com given the number of days ago '} ;
const restrictedAlertData = {title:'restricted',icon:<i style={{color:'#D81010'}} className='fas fa-minus-circle'></i>,msg:"it's restricted to load orders while the lowbox areas selector process is running"};

const OrderLoader = (props)=>{
    const [isLoading,setIsLoading] = useState(false)
    const [progress,setProgress] = useState(null)
    const [isInfoModalShowed,setInfoModalShowed] = useState(false)
    const [isRestrictedModalShowed,setRestrictedModalShowed] = useState(false)
    const [nbDaysAgo,setNbDaysAgo] = useState(0)

    const navigate = useNavigate()

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

    const loadOrders = ()=>{
        // SET THE LOADING PAGE 
        setIsLoading(true)

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

          // INITIATE THE REG STATE 
          // THIS VAR WILL MAKE SURE THAT WE ARE NOT LOADING A NEW REQ BEFORE THE EXISTINF REG IS DONE 
          // THIS WILL PREVENT THE CASE OF A NEW REQ FINISH BEFORE THE OLD REQ IN THIS CASE WE WILL HAVE 
          // THE PROGRESS DATA HAVE THE NEW DATA THEN THE OLD DATA 
          let req_is_done = true  

          const intv = setInterval(()=>{
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
                            navigate('/load_orders/'+orders_loader_id+'/submit_orders',{state:{'orders':data.orders,'orders_selected_all':data.orders_selected_all}})

                        }
                        console.log('clear interval')
                        // CLEAR THE MONITORING INTERVAL 
                        clearInterval(intv)
                    }

                    // SET THE CURRENT REQUEST TO DONE 
                    req_is_done = true 


                })
            }
          },5000)


        })
    }

    return(

        !isLoading ? 
        <div class="order-loader-container">
            <OrderLoaderForm nbDaysAgo={nbDaysAgo} setNbDaysAgo={setNbDaysAgo} loadOrders={loadOrders} /> 
            <GenericModal show={isInfoModalShowed}  type='alert' title={infoAlertData.title} alertData={infoAlertData} closeModal={closeInfoModal} />
            <GenericModal show={isRestrictedModalShowed}  type='alert' title={restrictedAlertData.title} alertData={restrictedAlertData} closeModal={closeRestrictedModal} />
        </div> : 
        <LoadingPage progress={progress} action_txt="loading orders" done_action_txt="were submitted"  />

    )
}
export default OrderLoader ;

