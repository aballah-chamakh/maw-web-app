
import './ResultPopupContent.scss' ;
import GenericTable from '../../../CommonComponents/GenericTable/GenericTable';
import Dashboard from '../../../CommonComponents/Dashboard/Dashboard';

const ResultPopupContent = (props)=>{

    const result_popup_order_keys = ['order_id','carrier','old_state','new_state']
    const result_popup_conv_errors_keys = ['failed_state','carrier']
    const result_popup_highlight_keys = {'old_state':'grey','new_state':'green'}


    // CONVERTE conv_errors TO AN ARRAY + BRING THE COUNT OF ALL THE FAILED STATES
    const conv_errors_to_array = (conv_errors)=>{
        let conv_errors_arr = []
        let carriers = Object.keys(conv_errors)
        let failed_state_cnt =0
        carriers.map((carrier)=>{
            let failed_states = Object.keys(conv_errors[carrier])
            let failed_states_cnt = Object.values(conv_errors[carrier])
            failed_states.map((failed_state,idx)=>{
                conv_errors_arr.push({'failed_state':failed_state,'carrier':carrier})
                failed_state_cnt += failed_states_cnt[idx]
            })
        })
        return [conv_errors_arr,failed_state_cnt]
    }
    let [conv_errors_arr,failed_state_cnt] = conv_errors_to_array(props.resultPopupData.conv_errors)

    // GET ORDERS OVERVIEW AFTER MONITORING 
    const get_orders_overview = ()=>{

        let orders_overview = {
            'Expédiés' : 0 ,
            'Livrés' : 0,
            'Retours':0,
            'Annulés':0,
            'converter errors':failed_state_cnt,
            'the same': props.resultPopupData.old_monitor_orders_len - props.resultPopupData.orders.length - failed_state_cnt,
        }

        props.resultPopupData.orders.map(order=>{
            orders_overview[order['new_state']+'s'] += 1 
        })

        return orders_overview
    }
    let orders_overview = get_orders_overview(props.resultPopupData.orders)

    return(
        <>
            <div className='monitoring-card'>
                <p className='monitoring-card-header'>monitoring results overview</p>
                <div className='monitoring-card-overview'>
                    <Dashboard  dashboardData={orders_overview} kpi_item_margin_direction='top' kpi_item_margin_value='10' />                
                </div>
            </div>

            {props.resultPopupData.orders.length ?
            <div className='monitoring-card'>
                <p className='monitoring-card-header'>updated orders detail</p>
                <GenericTable keys={result_popup_order_keys} orders={props.resultPopupData.orders} maxHeight='75vh' fontSize='13px' textAlign='center'  highlight_keys={result_popup_highlight_keys} />
            </div> : null }

            {conv_errors_arr.length ? 
                <div className='monitoring-card'>                        
                    <p className='monitoring-card-header'>carrier states who failed to convert to mawlety state   </p>
                    <GenericTable keys={result_popup_conv_errors_keys} orders={conv_errors_arr} maxHeight='75vh' fontSize='13px' textAlign='left' />
                </div>
             : null}
        </>
    )
}

export default ResultPopupContent ;