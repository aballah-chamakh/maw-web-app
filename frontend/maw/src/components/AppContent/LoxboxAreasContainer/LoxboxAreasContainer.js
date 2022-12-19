import './LoxboxAreasContainer.scss' ;
import { useState,useEffect } from 'react';
import axios from 'axios';
import { API_ENDPOINT } from '../../../globals';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import LoxboxAreas from './LoxboxAreas/LoxboxAreas';

const LoxboxAreasContainer = ()=>{
    const [loxboxAreas,setLoxboxAreas] = useState({})
    const [isLoading,setIsLoading] = useState(true)

    useEffect(()=>{
        axios.get(API_ENDPOINT+'/loxbox_areas').then((res)=>{
            setIsLoading(false)
            setLoxboxAreas(res.data)
        })
    },[])

    return(
        !isLoading ? 
        <div className='loxbox-areas-container'>
            <LoxboxAreas  data={loxboxAreas} /> 
        </div>  : 
        <LoadingPage  action_txt='loading loxbox areas' />

    )
}

export default LoxboxAreasContainer