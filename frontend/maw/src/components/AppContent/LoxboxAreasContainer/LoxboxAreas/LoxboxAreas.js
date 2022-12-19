import './LoxboxAreas.scss' ;
import Checkbox from '../../../CommonComponents/Checkbox/Checkbox';


const LoxboxAreas = (props)=>{

    let loxbox_areas_type = Object.keys(props.data).at(-1)
    const down_classes_icon = 'far fa-arrow-alt-circle-down'
    const up_classes_icon = 'far fa-arrow-alt-circle-up'
    const toggleDropdown = (e,id)=>{
        let iconEl = e.target 
        let subEl = document.querySelector('#'+id)
        if(subEl.style.display == 'none'){
            iconEl.className = up_classes_icon
            subEl.style.display = 'block'
        }else{
            iconEl.className = down_classes_icon
            subEl.style.display = 'none'
        }        
    }
    return(
   
        <div className='loxbox-areas'>
            <div className='loxbox-areas-header'>
                <p>{Object.keys(props.data).at(-1)}</p>
                <button onClick={()=>{}}>select all</button>
            </div>
            <div className='loxbox-areas-body'>
                {props.data[loxbox_areas_type].map((el)=>(
                    <div className='loxbox-areas-item'>
                        <div className='loxbox-areas-item-primary'>
                            <div className='loxbox-areas-item-primary-left'>
                                <Checkbox /> 
                                <p>{el.name}</p>
                            </div>
                            <i className='far fa-arrow-alt-circle-down' onClick={(e)=>{toggleDropdown(e,props.parent_id ? 'sub_'+props.parent_id+'_'+props.data.id+'_'+el.id:'sub_'+props.data.id+'_'+el.id)}}></i>
                        </div>
                        {loxbox_areas_type != 'localities' ? 
                        <div className='loxbox-areas-item-sub' id={props.parent_id ? 'sub_'+props.parent_id+'_'+props.data.id+'_'+el.id:'sub_'+props.data.id+'_'+el.id}>
                            <LoxboxAreas data={el} parent_id={props.parent_id ? props.parent_id+'_'+props.data.id :props.data.id} />
                        </div>
                        :null }
                    </div>
                ))
                }
                
            </div>
        </div>  
    )
}

export default LoxboxAreas