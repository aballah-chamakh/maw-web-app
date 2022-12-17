import './Checkbox.scss' ;

const Checkbox = (props)=>{
    return(
        <label class="checkbox-container"><input type="checkbox" name={props.name} checked={props.checked} onChange={props.handleChange} /><span class="fake-checkbox"></span></label>
    )
}

export default Checkbox ;