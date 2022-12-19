import './GenericModal.scss' ;
import Modal from 'react-bootstrap/Modal';


const GenericModal = (props)=>{


    return(
        <Modal show={props.show} onHide={props.closeModal} animation={true} size={props.size} >
           <div className="generic-modal">
                <div className="generic-modal-header" style={{borderBottom: props.type != 'alert' ? 'none' :'1px solid'}}>
                        <p className="generic-modal-header-title"> {props.title}</p>
                        <i onClick={props.closeModal} className="fas fa-times"></i>
                </div>
                {props.type == 'alert' ? 
                    <div className="generic-modal-body">
                        {props.alertData.icon}
                        <p>{props.orders_len} {props.alertData.msg}</p>
                    </div> 
                : <div style={{marginBottom:'10px'}}>{props.result_table}</div> }
                <div className="generic-modal-footer">
                        <button onClick={props.closeModal} >ok</button>
                </div>
           </div>
        </Modal>
    )
}

/*
    // RESTRICTED 
    <i style={{color:'#D81010'}} className='fas fa-minus-circle'></i>
  
    // INFO
    <i style={{color:'#101B82',fontSize:'45px'}} class="material-icons">info</i>
    
    // SUCCESS
    <i style={{color:'#28C20F'}} className="fas fa-check-circle"></i>
                
*/
export default GenericModal;