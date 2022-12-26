import './LoxboxAreasContainer.scss' ;
import { useState,useEffect } from 'react';
import axios from 'axios';
import $ from 'jquery' ;
import { API_ENDPOINT } from '../../../globals';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import LoxboxAreas from './LoxboxAreas/LoxboxAreas';
import ServerLoading from '../../CommonComponents/ServerLoading/ServerLoading';


const LoxboxAreasContainer = ()=>{
    const [loxboxAreas,setLoxboxAreas] = useState({})

    const [loadingActionTxt,setLoadingActionTxt] = useState('loading loxbox areas')

    const [lxSelectorProgress,setLxSelectorProgress] = useState(null)
    const [isLoading,setIsLoading] = useState(true)
    const [isServerLoading,setServerIsLoading] = useState(false)

    useEffect(()=>{
        // GRAB THE LOBOX AREAS ADDRESS LEVELS 
        axios.get(API_ENDPOINT+'/loxbox_areas').then((res)=>{
            let data = res.data 
            // CHECK IF THE SELECTOR PROCESS IS WORKING , IF SO 
            if(data.hasOwnProperty('is_working')){
                // SET THE PROGRESS OF THE SELECTOR 
                setLxSelectorProgress(data.progress)

                // SET THE LOADING ACTION TEXT RELATED TO THE SELECTOR PROCESS
                setLoadingActionTxt('selecting or deselecting address levels')

                // KEEP MONIROTING THE SELECTOR PROCESS UNTIL HE FINISH 
                const intv = setInterval(()=>{

                    axios.get(API_ENDPOINT+"/loxbox_areas").then(res=>{
                        let data = res.data 
                        // HANDLE THE FINISH OF THE SELECTOR PROCESS 
                        if(!data.hasOwnProperty('is_working')){
                            setIsLoading(false)
                            setLoxboxAreas(data)
                            clearInterval(intv)
                        }else{
                            // UPDATE THE PROGRESS DATA 
                            setLxSelectorProgress(data.progress)
                        }
                    })
    
                },5000)

            }else{ // OTHERWISE DISABEL THE LOADING PAGE AND SET LOBOX AREAS ADDRESS LEVELS 
                setIsLoading(false)
                setLoxboxAreas(res.data)
            }         
        })
    },[])

    const address_levels = ['loxbox_areas','cities','delegations','localities']

    const singular_address_levels = (address_level)=>{
        return {
            'loxbox_areas' : 'loxbox_areas',
            'cities' : 'city',
            'delegations' : 'delegation',
            'localities' : 'locality'
        }[address_level]
    }


    const are_last_address_level_elements_selected = (elements,exception_element_identifier)=>{
        // CHECK ALL THE ELEMENTS ARE SELECTED EXCEPT THE ELEMENT WHOS HAS exception_element_identifier
        for(let i=0;i<elements.length;i++){
            if (i == exception_element_identifier){
                continue 
            }

            if(!elements[i].selected){
                return false 
            } 
        }
        return true 
    }

    const get_last_address_level_element_s = (splitted_identifier,type,root_address_level_element=null)=>{
        let last_address_level_element_s = root_address_level_element ? root_address_level_element : loxboxAreas  ;

        splitted_identifier.map((id,idx)=>{
            id = parseInt(id)
            // SKIP THE ITERATION OF THE ROOT ADDRESS LEVEL OF THE IDENTIFIER BECAUSE : 
            // IN THE CASE OF ELEMENT : 
            //     THE ELEMENTS MUST BE AS THE INITIAL DATA 
            // IN THE CASE OF ELEMENTS  : 
            //     THE ROOT ADDRESS LEVEL OF THE IDENTIFIER HAVE NO SIBLINGGS 
            if(idx!=0){
                // HANDLE THE ELEMENTS CASE 
                if(type == 'elements'){
                    // IN THE LAST ITERATION GET THE SUB ELEMENTS OF THE LAST ELEMENTS 
                    if (splitted_identifier.length ==  idx + 1){
                        // LAST ELEMENTS = THE ELEMENT OF THE ADDRESS LEVEL ABOVE THE THE ADDRESS LEVEL OF THIS ITERATION[THE SUB ELEMENTS]
                        last_address_level_element_s = last_address_level_element_s[address_levels[idx]]
                    }else{
                        // LAST ELEMENT = THE ELEMENT OF THE ADDRESS LEVEL ABOVE THE THE ADDRESS LEVEL OF THIS ITERATION[THE SUB ELEMENTS][ID OF THE ADDRESS LEVEL OF THIS ITERATION]
                        last_address_level_element_s = last_address_level_element_s[address_levels[idx]][id]
                    }
                }else{ // HANDLE THE ELEMENT CASE 
                    // LAST ELEMENT  = THE ELEMENT OF THE ADDRESS LEVEL ABOVE THE THE ADDRESS LEVEL OF THIS ITERATION[THE SUB ELEMENTS][ID OF THE ADDRESS LEVEL OF THIS ITERATION]
                    last_address_level_element_s = last_address_level_element_s[address_levels[idx]][id]
                }
            }
        })
        return last_address_level_element_s
    }

    const get_additional_action_if_exist = (identifier)=>{
        // INITIATE THE ADDITIONAL ACTION 
        let additional_action = {action:'',idx:null}
        // SPLIT THE IDENTIFIER BY _
        let splitted_identifier = identifier.split('_')
        // INITIATE IS SELECT 
        let is_select = null 

        // THE WAY THIS LOOP DETECT THE ADDITIONAL ACTION IS 
        // FOREACH ADDRESS LEVEL OF THE IDENTIFIER EXCEPT FOR THE ROOT ADDRESS LEVEL
        //      UPDATE THE SPLITTED IDENTIFIER FOR EACH NEW IDENTIFIER 
        //      GET THE ELEMENTS OF THE LAST ADDRESS LEVEL OF THE IDENTIFIER 
        //      CHECK IF THE THOSE ELEMENTS ARE ALL SElECTED EXCEPT THE ONE WHO HAS THE LAST THE IDX OF THE ADDRESS LEVEL OF THE IDENTIFIER 
        //             IF SO : SET THE ADDITIONAL ACTION THE ADDRESS LEVEL ABOVE THE LAST ADDRESS LEVEL OF THE IDENTIFIER 
        //                   : REMOVE THE LAST ADDRESS LEVEL IDX FROM THE IDENTIFIER 
        //             OTHERWISE : BREAK 

        // FOREACH ADDRESS LEVEL OF THE IDENTIFIER EXCEPT FOR THE ROOT ADDRESS LEVEL
        let splitted_identifier_len = splitted_identifier.length
        for(let i=0;i<splitted_identifier_len-1;i++){
        
            // UPDATE THE SPLITTED IDENTIFIER FOR EACH NEW IDENTIFIER 
            splitted_identifier = identifier.split('_')
            // UPDATE THE last_address_level_identifier FOR EACH NEW  IDENTIFIER
            let last_address_level_identifier = splitted_identifier.at(-1)

            // GET THE ELEMENTS OF THE LAST ADDRESS LEVEL OF THE IDENTIFIER 
            let last_address_level_elements = get_last_address_level_element_s(splitted_identifier,'elements')

            // SET THE THE IS SELECT VALUE ONLY FROM THE INITIAL IDENTIFIER 
            if (i == 0){
                is_select = !last_address_level_elements[parseInt(last_address_level_identifier)]['selected']
            }

            // CHECK IF THE THOSE ELEMENTS ARE ALL SElECTED EXCEPT THE ONE WHO HAS THE LAST THE IDX OF THE ADDRESS LEVEL OF THE IDENTIFIER 
            if (are_last_address_level_elements_selected(last_address_level_elements,last_address_level_identifier)){
                // SET THE ADDITIONAL ACTION THE ADDRESS LEVEL ABOVE THE LAST ADDRESS LEVEL OF THE IDENTIFIER 
                additional_action.idx = splitted_identifier.length-2
                additional_action.action = singular_address_levels(address_levels[splitted_identifier.length-2]) +( is_select ?  '_select_all' : '_disable_select_all') 
                // REMOVE THE LAST ADDRESS LEVEL IDX FROM THE IDENTIFIER 
                identifier = identifier.slice(0,-(last_address_level_identifier.length+1)) 
            }else{ //OTHERWISE BREAK 
                
                break
            }
           
        }

        // RETURN THE ADDITIONAL ACTION 
        return additional_action
    }

    const select_or_deselect_address_level_element_recursively = (address_level_element,is_select)=>{

        // SELECT THE CURRENT ADDRESS LEVEL ELEMENT
        address_level_element.selected = is_select
        // GRAB THE LAST KEY OF THE CURRENT ADDRESS LEVEL ELEMENT
        let address_level_element_last_key = Object.keys(address_level_element).at(-1)

        // BREAK THE RECURSIVITY WHEN THE CURRENT ADDRESS LEVEL ELEMENT IS A LOCALITY
        if(!address_levels.includes(address_level_element_last_key)){
            return 
        }

        // SELECT THE SUB ADDRESS LEVEL ELEMENTS OF THE CURRENT ONE RECURSIVELY 
        address_level_element[address_level_element_last_key].map((sub_address_level_element)=>{
            select_or_deselect_address_level_element_recursively(sub_address_level_element,is_select)
        })

    }
    const handle_additional_action = (root_address_level_element,additional_action,splitted_identifier,is_select) =>{
        let first_idx_range = additional_action.idx 
        let last_idx_range = splitted_identifier.length - 2
        console.log(first_idx_range)
        console.log(last_idx_range)
        let address_level_ref_element = root_address_level_element

        // CLIP THE END PART OF splitted_identifier IN INDEX OF last_idx_range (+1 TO INCLUDE THE LAST INDEX RANGE)
        splitted_identifier.slice(0,last_idx_range+1).map((address_level_idx,idx)=>{
            
            // SKIP THE FIRST ADDRESS LEVEL IDX BECAUSE HIS ADDRESS LEVEL ELEMENT IS THE SAME AS THE INITIAL ONE 
            if(idx != 0){
                let address_level_element_last_key = Object.keys(address_level_ref_element).at(-1)
                address_level_ref_element = address_level_ref_element[address_level_element_last_key][address_level_idx]
            }

            // SELECT THE CURRENT ADDRESS LEVEL ELEMENT IF HIS IDX IN RANGE OF ELEMENT TO BE SELECTED 
            if (idx >= first_idx_range && idx <= last_idx_range){
                console.log('included idx : '+idx)
                address_level_ref_element.selected = is_select 
            }
        })

    }


    
    const handleSelectChange = (identifier)=>{
        setServerIsLoading(true)
        let newLoxboxAreas = {...loxboxAreas}
        let splitted_identifier = identifier.split('_')
        let last_address_level_element = get_last_address_level_element_s(splitted_identifier,'element',newLoxboxAreas)
        
        let additional_action = {action:''}
        
        // SKIP THE IDENTIFIER WHICH HAVE ONLY THE ROOT ADDRESS LEVEL WHICH DOESN'T HAVE ADDITIONAL ACTION AT ALL 
        if (splitted_identifier.length != 1){
            additional_action = get_additional_action_if_exist(identifier)
            console.log(additional_action)
        }
        
        let is_select = !last_address_level_element.selected

        /*identifier = request.data.get('identifier')
        is_select = request.data.get('is_select')
        additional_action = request.data.get('additional_action')*/

        axios.put(API_ENDPOINT+'/launch_loxbox_areas_select_or_deselect',{
            identifier  : identifier ,
            is_select  : is_select , 
            additional_action : additional_action.action
        }).then((res)=>{

            

            const intv = setInterval(()=>{
                console.log("monitor_loxbox_areas_selector_process")
                axios.get(API_ENDPOINT+"/monitor_loxbox_areas_selector_process").then(res=>{
                    let progress = res.data 
                    if(progress.is_working == false){
                        setServerIsLoading(false)
                        
                        select_or_deselect_address_level_element_recursively(last_address_level_element,is_select)
                        
                        if(additional_action.action){
                            handle_additional_action(newLoxboxAreas,additional_action,splitted_identifier,is_select)
                        }
                        setLoxboxAreas(newLoxboxAreas)
                        clearInterval(intv)
                    }
                })

            },5000)

        })
    }


    return(
        !isLoading ? 
        <div className='loxbox-areas-container'>
            <LoxboxAreas handleSelectChange={handleSelectChange}  current_address_level_data={loxboxAreas} current_address_level_idx={loxboxAreas.id} /> 
            <ServerLoading show={isServerLoading}/>
        </div>  : 
        <LoadingPage  action_txt={loadingActionTxt} progress={lxSelectorProgress} items_name='address levels' />

    )
}

export default LoxboxAreasContainer