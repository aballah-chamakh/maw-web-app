import './LoxboxAreas.scss' ;
import $ from "jquery";
import Checkbox from '../../../CommonComponents/Checkbox/Checkbox';


const LoxboxAreas = (props)=>{

    
    const down_classes_icon = 'far fa-arrow-alt-circle-down'
    const up_classes_icon = 'far fa-arrow-alt-circle-up'

    const toggleDropdown = (e,id)=>{
        let iconEl = e.target 
        let primaryEL = document.querySelector('#'+id.replace('sub','primary'))
        let subEl = $('#'+id)
        if(subEl.css('display') == 'none'){
            iconEl.className = up_classes_icon
            subEl.slideDown(100)
            primaryEL.style.borderRadius = "10px 10px 0px 0px"
        }else{
            iconEl.className = down_classes_icon
            subEl.slideUp(100)
            primaryEL.style.borderRadius = "10px"
        }        
    }



    const get_identifier = (prefix='',sub_address_level_idx='') =>{
        let identifier = ''
        // CONSTRUCT THE IDENTIFIER IN THE CASE OF HAVING A PARENT IDXS
        if(props.parent_idxs){
            identifier = prefix ? prefix+'_' : prefix  // SET THE PREFIX OF THE IDENTIFIER 
            identifier += props.parent_idxs+'_' // ADD THE IDXS THE ALL THE ADDRESS LEVELS ABOVE THE CURRENT ONE
            identifier += current_address_level_idx // ADD THE SET THE IDX OF THE CURRENT ADDRESS LEVEL 
            identifier += sub_address_level_idx.toString() ?  '_' + sub_address_level_idx : sub_address_level_idx // ADD THE IDX OF ONE OF THE SUB ADDRESS LEVEL OF THE CURRENT ONE  
            
        }else{ // CONSTRUCT THE IDENTIFIER INTHE CASE OF HAVING NO PARENT ID (THE FIRT CALL OF THE COMPONENT)
          
            identifier = prefix ? prefix+'_' : prefix // SET THE PREFIX OF THE IDENTIFIER 
            identifier += current_address_level_idx // ADD THE SET THE IDX OF THE CURRENT ADDRESS LEVEL 
            identifier +=  sub_address_level_idx.toString() ?  '_'+sub_address_level_idx : sub_address_level_idx // ADD THE IDX OF ONE OF THE SUB ADDRESS LEVEL OF THE CURRENT ONE  
        }
        return identifier
    }

    const get_the_next_parent_identifier = ()=>{
        let identifier = ''

        if(props.parent_idxs){

            identifier  = props.parent_idxs+'_' // SET THE PREVIOUS PARENT IDXS 
            identifier += current_address_level_idx // ADD THE IDX OF THE CURRENT ADDRESS LEVEL 

        }else{
            identifier = current_address_level_idx // SET THE IDX OF THE CURRENT ADDRESS LEVEL 
        }

        return identifier
    }


    let current_address_level_data = props.current_address_level_data  
    let current_address_level_idx = props.current_address_level_idx  
    let address_level = Object.keys(current_address_level_data).at(-1)
    
    return(
   
        <div className='loxbox-areas'>
            <div className='loxbox-areas-header'>
                <p>{address_level}</p>
                <button onClick={()=>{props.handleSelectChange(get_identifier())}}>{!current_address_level_data.selected ?  'select all' : 'unselect all'}</button>
            </div>
            <div className='loxbox-areas-body'>
                {current_address_level_data[address_level].map((sub_address_level_data,sub_address_lebel_idx)=>(
                    <div className='loxbox-areas-item'>
                        <div className='loxbox-areas-item-primary' id={get_identifier('primary',sub_address_lebel_idx)}>
                            <div className='loxbox-areas-item-primary-left'>
                                <Checkbox checked={sub_address_level_data.selected} handleChange={()=>{props.handleSelectChange(get_identifier('',sub_address_lebel_idx))}}/> 
                                <p>{sub_address_level_data.name}</p>
                            </div>
                            {address_level != 'localities' ? 
                            <i className='far fa-arrow-alt-circle-down' onClick={(e)=>{toggleDropdown(e,get_identifier('sub',sub_address_lebel_idx))}}></i>
                            :null}
                        </div>
                        {address_level != 'localities' ? 
                        <div className='loxbox-areas-item-sub' id={get_identifier('sub',sub_address_lebel_idx)}>
                            <LoxboxAreas current_address_level_data={sub_address_level_data} current_address_level_idx={sub_address_lebel_idx} parent_idxs={get_the_next_parent_identifier()} handleSelectChange={props.handleSelectChange}  />
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