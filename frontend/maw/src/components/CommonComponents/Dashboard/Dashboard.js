import './Dashboard.scss' ;
/*

PROPS OF THE Dashboard COMPONENT :

NAMES            VALUES 
dashboardData => {kpi_name:kpi value}
kpi_item_nb_fontSize => number 
kpi_item_width => numver (the width of pki)
kpi_item_margin_direction => top or bottom (the vertical direction of the margin)

*/
const Dashboard = (props)=>{
    const get_item_margin = (margin_direction,margin_value)=>{
        let margin = '0px 0px 10px 0px'
        if(margin_direction == 'top'){
            margin = margin_value ? `${margin_value} 0px 0px 0px` : '10px 0px 0px 0px'
        }else {
            margin = margin_value ? `0px 0px ${margin_value}px 0px` : '0px 0px 10px 0px'
        }
        return margin
    }
    return(
        <div className='dashboard-container'>
            {Object.keys(props.dashboardData).map((dashboard_kpi_name)=>(
                <div className='dashboard-container-item' style={{width:props.kpi_item_width,'margin': get_item_margin(props.kpi_item_margin_direction,props.kpi_item_margin_value)}}>
                    <p className='dashboard-container-item-nb' style={{fontSize:props.kpi_item_nb_fontSize}} >{props.dashboardData[dashboard_kpi_name]}</p>
                    <p className='dashboard-container-item-name'>{dashboard_kpi_name}</p>
                </div>
            ))}
        </div>
    )
}

export default Dashboard