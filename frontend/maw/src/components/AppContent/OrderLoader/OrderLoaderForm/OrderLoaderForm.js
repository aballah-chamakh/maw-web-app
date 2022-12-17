import './OrderLoaderForm.scss' ;


const OrderLoaderForm = (props)=>{

    const handleChange = (e)=>{
        let value = e.target.value  ;
        props.setNbDaysAgo(value) ;
    }
    return(
        <div class="order-loader-form-container">
            <i className='fa fa-cart-arrow-down'></i>
            <div class='form-group'>
                <label>Number of days ago</label>
                <input type="number" className="form-control" placeholder='nb of days ago (including today)' value={props.nbDaysAgo} onChange={handleChange} />
            </div>
            <button onClick={props.loadOrders} >load orders</button>
        </div>
    )
}
export default OrderLoaderForm ;

