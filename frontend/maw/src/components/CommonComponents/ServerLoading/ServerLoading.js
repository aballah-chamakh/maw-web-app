import React from "react";
import ClipLoader  from "react-spinners/ClipLoader";

import './ServerLoading.scss' ;

const ServerLoading = (props)=>{
    return(
        <div className="server-loading-container" style={{display:props.show ? 'flex' : 'none'}}>
            <ClipLoader 

                    color="white"
                    size={70}
             
               
                    cssOverride={{borderWidth:'10px'}}
                />
        </div>
    )
}
export default ServerLoading ;