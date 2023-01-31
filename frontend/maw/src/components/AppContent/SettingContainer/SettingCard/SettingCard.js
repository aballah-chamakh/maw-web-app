import './SettingCard.scss'
import { useFormik } from 'formik';
import axios from 'axios' ;
import { API_ENDPOINT } from '../../../../globals';
import Checkbox from '../../../CommonComponents/Checkbox/Checkbox';


const SettingCard  = (props)=>{


    const formik = useFormik({
        initialValues: props.formData,
        validationSchema: props.validationSchema,
        onSubmit: formData => {
            props.setServerLoading(true)
            axios.put(API_ENDPOINT+'/update_setting',{setting_part:props.setting_part,form_data:formData }).then(res=>{
                console.log(res.data)
                props.setServerLoading(false)
            })
        },
    });

    const getLabel = (key)=>{
        let splitted_label =  key.split(/(?=[A-Z])/);
        let label = ""
        splitted_label.map(el=>{
            label += el.toLowerCase()+" "
        })
        return label

    }

    const passwodTypeKey  = ['Password','mawletyApiKey','afexApiKey','loxboxApiKey']

    const handleCheckboxChange = (input_name)=>{
        let inpEl = document.querySelector('input[name='+input_name+']')
        if(inpEl.type == 'text'){
            inpEl.type = 'password'
           
        }else{
            inpEl.type = 'text'
        }
    }

    return(
        <div className='setting-card'>
            <div className='setting-card-header'>
                <p>{props.title}</p>
            </div>
            <div className='setting-card-body'>
                <form onSubmit={formik.handleSubmit}>
                    {Object.keys(props.formData).map(key=>(
                        <div className='form-group'>
                            <label htmlFor={key} >{getLabel(key)}</label>
                            <input
                                id={key}
                                name={key}
                                type={passwodTypeKey.some(el=>key.includes(el)) ? 'password' : 'text'}
                                onChange={formik.handleChange}
                                onBlur={formik.handleBlur}
                                value={formik.values[key]}
                                className='form-control'
                                style={formik.touched[key] && formik.errors[key] ? {borderColor: 'red',outline:'none !important'} : null}
                            />
                            {formik.touched[key] && formik.errors[key] ? (
                                    <p style={{color:'red'}}>{formik.errors[key]}</p>
                            ) : null}
                            { passwodTypeKey.some(el=>key.includes(el))  ? <div className='toggle-password-visibility' ><Checkbox handleChange={()=>{handleCheckboxChange(key)}} /><p>show password</p></div>  : null }
                        </div>
                    ))}
                    <button type="submit">update</button>
                </form>
            </div>
        </div>
    )
}
export default SettingCard