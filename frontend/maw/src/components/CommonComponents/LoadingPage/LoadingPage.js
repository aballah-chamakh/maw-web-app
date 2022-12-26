import './LoadingPage.scss' ;
import GridLoader  from "react-spinners/GridLoader";


const LoadingPage = (props)=>{
    
    // THIS BLOCK OF CODE SOLVE THE PROBLEM OF THE INCONSISTENCY IN THE THE NAMING OF done_orders AND orders_to_be_done
    // INITIATE orders_to_be_done/orders_to_be_done
    let done_orders =  0  ;
    let orders_to_be_done = 0 ;

    // CHECK IF THE PROGRESS EXIST 
    if(props.progress){

        // GRAB THE KEYS OF THE PROGRESS WITHOUT current_order_id
        let progress_keys = Object.keys(props.progress).filter(el=>el != 'current_order_id')

        // CHECK WHICH KEY VALUE IS BIGGER AND SET IT AS done_orders AND THE OTHER ONE AS orders_to_be_done
        if(props.progress[progress_keys[0]] > props.progress[progress_keys[1]]){
            done_orders = props.progress[progress_keys[1]]  ;
            orders_to_be_done = props.progress[progress_keys[0]]
        }else{
            done_orders = props.progress[progress_keys[0]]  ;
            orders_to_be_done = props.progress[progress_keys[1]]
        }

    }


    return (
        <div className="loading-page-container">
            {props.progress ? 
                <>
                    <p class="upper-txt"><span class="highlight">{done_orders} / {orders_to_be_done}</span> {props.items_name ? props.items_name : 'orders' } {props.done_action_txt}</p>
                    <GridLoader 
                        color="#276629"
                        size={20}
                    />
                    <div class="lower-txt">
                        {props.progress.current_order_id ? 
                            <>
                                <p>working on the order with id : </p>
                                <p class="highlight highlight-bg">{props.progress.current_order_id}</p>
                            </>:
                            <p>{props.action_txt}</p>
                        }

                    </div>
                </>

            : 
            <>
                <GridLoader 
                    color="#276629"
                    size={20}
                />
                <div class="lower-txt">
                    <p>{props.action_txt}</p>
                </div>
            </>
}
        </div>
    )

}
export default LoadingPage ;
