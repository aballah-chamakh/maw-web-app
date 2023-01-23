import './SettingContainer.scss' ;
import axios from 'axios';
import { useEffect,useState } from 'react';
import * as Yup from 'yup';
import { API_ENDPOINT } from '../../../globals';
import LoadingPage from '../../CommonComponents/LoadingPage/LoadingPage';
import SettingCard from './SettingCard/SettingCard';
import ServerLoading from '../../CommonComponents/ServerLoading/ServerLoading';

const SettingContainer = (props)=>{
    const [setting,setSetting] = useState(null)
    const [loading,setLoading] = useState(true)
    const [serverLoading,setServerLoading] = useState(false)

    useEffect(()=>{
        axios.get(API_ENDPOINT+'/get_setting').then(res=>{
            setSetting(res.data)
            setLoading(false)
        })
    },[])

    const afexValidation =  Yup.object({
        afexEmail: Yup.string()
          .email('Invalid email address')
          .required('Required'),
        afexPassword: Yup.string()
          .required('Required'),
    })

    const loxboxValidation =  Yup.object({
        loxboxEmail: Yup.string()
          .required('Required'),
          loxboxPassword: Yup.string()
          .required('Required'),
    })

    const mawletyValidation =  Yup.object({
        mawletyApiKey: Yup.string()
          .required('Required'),
    })
    
    const afexApiValidation =  Yup.object({
        afexClientId: Yup.number()
          .integer()
          .required('Required'),
        afexApiKey: Yup.string()
          .required('Required'),
    })


    return (
         !loading  ? 
        <div className='setting-container'>
            <div className='setting-container-header'>
                <p>Settings</p>
            </div>
            <div className='setting-container-body'>
                <SettingCard title="afex login credentials" setting_part="afex" formData={{afexEmail:setting.afex_email,afexPassword:setting.afex_password}} validationSchema={afexValidation} setServerLoading={setServerLoading}  />
                <SettingCard title="loxbox login credentials" setting_part="loxbox" formData={{loxboxEmail:setting.loxbox_email,loxboxPassword:setting.loxbox_password}} validationSchema={loxboxValidation} setServerLoading={setServerLoading}  />
                <SettingCard title="mawlety api credentials" setting_part="mawlety_api" formData={{mawletyApiKey:setting.mawlety_api_key}} validationSchema={mawletyValidation} setServerLoading={setServerLoading}  />
                <SettingCard title="afex api credentials" setting_part="afex_api" formData={{afexClientId:setting.afex_client_id,afexApiKey:setting.afex_api_key}} validationSchema={afexApiValidation} setServerLoading={setServerLoading}  />
            </div>
            <ServerLoading show={serverLoading} />
        </div> : 
        <LoadingPage action_txt={"loading settings"} />
        
    )
}
export default SettingContainer