import './LoxboxAreas.scss' ;
import $ from "jquery";
import Checkbox from '../../../CommonComponents/Checkbox/Checkbox';


const LoxboxAreas = (props)=>{

    
    const down_classes_icon = 'far fa-arrow-alt-circle-down'
    const up_classes_icon = 'far fa-arrow-alt-circle-up'
    const address_level_to_sub_address_level = {
        'cities' : 'delegations',
        'delegations' : 'localities'
    }

    const toggleDropdown = (e,id)=>{
        let iconEl = e.target 
        let primaryEL = document.querySelector('#'+id.replace('sub','primary'))
        let subEl = $('#'+id)
        // OPEN THE SUB ELEMENT
        if(subEl.css('display') == 'none'){
            iconEl.className = up_classes_icon
            subEl.slideDown(20)
            primaryEL.style.borderRadius = "10px 10px 0px 0px"
        }else{ // CLOSE THE SUBELEMENT 
            iconEl.className = down_classes_icon
            subEl.slideUp(20)
            primaryEL.style.borderRadius = "10px"
        }        
    }

    const openElement = (current_element,iconEl) => {
        // OPEN THE SUB ELEMENT
        current_element.css('display','block')
        //slideDown(100,
        //'linear',()=>{
         //   alert('done done ')
         //   console.log($('#'+current_identifier).css('top'))
        //})

        // SET THE BORDER RADIUS OF THE PRIMARY ELEMENT
        $('#'+current_element.attr('id').replace('sub','primary')).css('borderRadius', "10px 10px 0px 0px")

        // SET THE Up ARROW ICON 
        iconEl.className = up_classes_icon
    } 

    const closeElement = (current_element,iconEl) => {
        // CLOSE THE SUB ELEMENT
        current_element.css('display','none')
        
        //slideUp(100,'linear',()=>{
         //   alert('up up ')
        //})

        // RESET THE BORDER RADIUS OF THE PRIMARY ELEMENT
        $('#'+current_element.attr('id').replace('sub','primary')).css('borderRadius',"10px")

        // SET THE DOWN ARROW ICON 
        iconEl.className = down_classes_icon
    } 



    const close_opened_same_identifier_address_level_recursively = (identifier,iconEl) =>{
        let splitted_identifier = identifier.split('_')
        let last_idx_len = identifier.split('_').at(-1).length 
        let pre_identifier_address_level = identifier.slice(0,-last_idx_len)
        let idx = 0 
        let current_element = $('#'+pre_identifier_address_level + idx)

        while(current_element.length>0){

            if(current_element.css('display') != 'none'){

                // IN THE CITY ADDRESS LEVEL CHECK IF HE HAVE AN OPENED DELEGATION THEN CLOSE IT 
                if(splitted_identifier.length == 3){
                    close_opened_same_identifier_address_level_recursively(identifier+'_0',iconEl)
                }

                closeElement(current_element,iconEl)
                break 
            }
            idx += 1 
            current_element = $("#"+pre_identifier_address_level + idx)
        }
    }

    const toggleElement = (e,identifier)=>{
        console.log('top before : '+$('#'+identifier).position().top)
        let iconEl = e.target 
        let splitted_identifier = identifier.split('_')
        let current_element = $('#'+identifier)
        let main_action = current_element.css('display') == 'none' ? 'open' : 'close'
        if (main_action == 'close'){
            let address_level = splitted_identifier.length == 3 ?  'city' : 'delegation'
            if(address_level == 'city'){
                // CHECK IF THE CITY HAVE AN OPENED DELEGATION THEN CLOSE IT 
                close_opened_same_identifier_address_level_recursively(identifier+'_0',iconEl)
                // CLOSE THE CITY
                closeElement(current_element,iconEl)
            }else{
                // CLOSE THE DELEGATION
                closeElement(current_element,iconEl)
            }
        }else{
            
            close_opened_same_identifier_address_level_recursively(identifier,iconEl)
            openElement(current_element,iconEl)
            window.scrollTo(0,$('#'+identifier.replace('sub','primary')).position().top)
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

    const get_selected_sub_address_elements = (address_level,sub_address_level_element)=>{
        if (address_level != 'localities' && !sub_address_level_element.selected){
            let cnt = 0 
            let sub_address_level = address_level_to_sub_address_level[address_level] 
            sub_address_level_element[sub_address_level].map(el=>{
                    cnt +=  el.selected  ?  1 : 0  
            })
            if(cnt > 0){
                return cnt+" "+sub_address_level+" are selected"
            }
        }
        return ""
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
                {current_address_level_data[address_level].map((sub_address_level_data,sub_address_lebel_idx)=>{
                    let selected_sub_address_elements =  get_selected_sub_address_elements(address_level,sub_address_level_data)
                    return (<div className='loxbox-areas-item'>
                        <div className='loxbox-areas-item-primary' id={get_identifier('primary',sub_address_lebel_idx)}>
                            <div className='loxbox-areas-item-primary-left'>
                                <Checkbox checked={sub_address_level_data.selected} handleChange={()=>{props.handleSelectChange(get_identifier('',sub_address_lebel_idx))}}/> 
                                <p>{sub_address_level_data.name} { selected_sub_address_elements ? <span className='highlight'>{selected_sub_address_elements}</span> : null } </p>
                            </div>
                            {address_level != 'localities' ? 
                            <i className='far fa-arrow-alt-circle-down' onClick={(e)=>{toggleElement(e,get_identifier('sub',sub_address_lebel_idx))}}></i>
                            :null}
                        </div>
                        {address_level != 'localities' ? 
                        <div className='loxbox-areas-item-sub' id={get_identifier('sub',sub_address_lebel_idx)}>
                            <LoxboxAreas current_address_level_data={sub_address_level_data} current_address_level_idx={sub_address_lebel_idx} parent_idxs={get_the_next_parent_identifier()} handleSelectChange={props.handleSelectChange}  />
                        </div>
                        :null }
                    </div>)
                   })
                }
                
            </div>
        </div>  
    )
}

export default LoxboxAreas