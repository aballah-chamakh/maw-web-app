import React,{useEffect,useState} from "react";
import ClipLoader  from "react-spinners/ClipLoader";
import $ from 'jquery' ;
import './ServerLoading.scss' ;

const ServerLoading = (props)=>{
    const [app_sidebar_container_width_per,set_app_sidebar_container_width_per] = useState(0)
    const [server_loading_width_per,set_server_loading_width_per] = useState('100%')



    useEffect(()=>{
        let sideBarWidth = $('.app-sidebar-container').width() / $('body').width() * 100
        set_app_sidebar_container_width_per(sideBarWidth+'%')
        set_server_loading_width_per((100 - sideBarWidth)+'%')

        const resizeObserver = new ResizeObserver((entries)=>{
            let sideBarWidth = entries[0].contentBoxSize[0].inlineSize / $('body').width() * 100
            set_app_sidebar_container_width_per(sideBarWidth+'%')
            set_server_loading_width_per((100 - sideBarWidth)+'%')
        })
        let app_sidebar_container =  $('.app-sidebar-container')[0]
        
        resizeObserver.observe(app_sidebar_container)

        return ()=>{resizeObserver.disconnect()}

    },[])
    return(
        <div className="server-loading-container" style={{marginLeft:app_sidebar_container_width_per,width:server_loading_width_per,display:props.show ? 'flex' : 'none'}}>
            <ClipLoader 

                    color="white"
                    size={70}
             
               
                    cssOverride={{borderWidth:'10px'}}
                />
        </div>
    )
}
export default ServerLoading ;