import './OrderLoaderForm.scss' ;
import DatePicker from "react-widgets/DatePicker";


const OrderLoaderForm = (props)=>{

    const handleChange = (date,date_field)=>{
        if(date_field == 'start_date'){
            props.setStartDate(date) ;
        }else{
            props.setEndDate(date) ;
        }
    }
    return(
        <div class="order-loader-form-container">
            <i  className='fa fa-cart-arrow-down order-loader-form-container-icon'></i>

            <div class='form-group'>
                <label>Date du début</label>
                <DatePicker
                    defaultValue={new Date()}
                    valueFormat={{ dateStyle: "medium" }}
                    onChange={(date)=>{handleChange(date,'start_date')}}
                />
            </div>
            <div class='form-group'>
                <label>Date du fin</label>
                <DatePicker
                    defaultValue={new Date()}
                    valueFormat={{ dateStyle: "medium" }}
                    onChange={(date)=>{handleChange(date,'end_date')}}
                    min={props.startDate}
                />
            </div>
            <button className='order-loader-form-container-button' onClick={props.loadOrders} >Chargez les commandes</button>
        </div>
    )
}
export default OrderLoaderForm ;

//                 <input type="number" className="form-control" placeholder='nb of days ago (including today)' value={props.nbDaysAgo} onChange={handleChange} />


