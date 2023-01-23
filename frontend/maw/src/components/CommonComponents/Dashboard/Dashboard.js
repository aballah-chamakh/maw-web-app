import './Dashboard.scss' ;

const Dashboard = (props)=>{
    return(
        <div className='dashboard-container'>
            {Object.keys(props.dashboardData).map((dashboard_kpi_name)=>(
                <div className='dashboard-container-item' style={{width:props.kpi_item_width,'margin':props.kpi_item_margin_direction == 'top' ? '10px 0px 0px 0px' : '0px 0px 10px 0px'}}>
                    <p className='dashboard-container-item-nb' style={{fontSize:props.kpi_item_nb_fontSize}} >{props.dashboardData[dashboard_kpi_name]}</p>
                    <p className='dashboard-container-item-name'>{dashboard_kpi_name}</p>
                </div>
            ))}
        </div>
    )
}

export default Dashboard