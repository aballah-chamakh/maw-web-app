import './GenericTable.scss' ;
import Checkbox from '../Checkbox/Checkbox';

const GenericTable = (props)=>{
    let address_keys = ['city','delegation','locality']
    return(
        <div style={{maxHeight:props.maxHeight,overflowY:'auto'}}>
        <table class="table generic-table align-middle justify-middle" style={{fontSize:props.fontSize, textAlign: props.textAlign}} >
            <thead >
                <tr>
                    {props.keys.map(key=>{
                        if (key == 'selected'){
                            return <th scope="col"><Checkbox name="select_unselect_all" handleChange={props.handleSelectChange} checked={props.ordersSelectedAll} /></th>
                        }else{
                            return <th scope="col">{key}</th>
                        }
                    })
                    }
                </tr>
            </thead>
            
            <tbody>
                {props.orders.map(order=>{
                    return(
                        <tr>
                            {props.keys.map(key=>{
                                if (key == 'selected'){
                                    return <td ><Checkbox name={'order_'+order.id} handleChange={props.handleSelectChange} checked={order.selected} /></td>
                                }else if (key == 'first and last name'){
                                    return <td>{order.customer_detail.firstname} {order.customer_detail.lastname}</td>
                                }else if (address_keys.includes(key)){
                                    return <td>{order.address_detail[key]}</td>
                                }else if (props.dropdown_keys && props.dropdown_keys[key]){
                                    return (<td>
                                            <select class="form-select" value={order[key]} name={'select_order_'+order.id} onChange={props.handleDropdownChange} >
                                                {props.dropdown_keys[key].map(opt=><option value={opt} >{opt}</option>)}
                                            </select>
                                        </td>)
                                }else if (props.highlight_keys && Object.keys(props.highlight_keys).includes(key)){
                                    return <td><span class="generic-table-highlight" style={{backgroundColor:props.highlight_keys[key]}}>{order[key]}</span></td>
                                }else{
                                    return <td >{order[key]}</td>
                                }
                            })
                            }
                        </tr>
                    )
                })
                }
           
            </tbody>
            
        </table></div>
    )
}
export default GenericTable ;