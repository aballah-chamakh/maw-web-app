
import {useState} from 'react'
import { useNavigate } from 'react-router-dom';
import App from '../../App';
import './AppSidebar.scss' ;
import {Link} from 'react-router-dom' ;


const AppSidebar = (props)=>{
    const [isSidebarHidden,setIsSidebarHidden] = useState(false) ;
    const navigate = useNavigate()

    const toggleSidebar = ()=>{
        setIsSidebarHidden((prevIsSidebarHidden)=>{
            let newIsSidebarHidden = !prevIsSidebarHidden ;
            if (newIsSidebarHidden){
                document.querySelector('.app-sidebar-container').style.width = '3%' ;
                document.querySelector('.app-content-container').style.marginLeft = '3%' ;

            }else{
                document.querySelector('.app-sidebar-container').style.width = '17%' ;
                document.querySelector('.app-content-container').style.marginLeft = '17%' ;
            }   
            return newIsSidebarHidden
        })
     }

    return(
        <div className="app-sidebar-container">
            { ! isSidebarHidden  ? 
                <div class="app-sidebar-apparent">
                    <div class="app-sidebar-apparent-header">
                        <p>mawlety</p>
                        <i onClick={toggleSidebar} class='fas fa-arrow-left'></i>
                    </div>
                    <div class="app-sidebar-apparent-logo">
                        <img src='http://127.0.0.1:8000/media/maw_logo.jpg' />
                    </div>
                    <div class="app-sidebar-apparent-navigation">
                        <ul>
                            <li  onClick={()=>{navigate("/load_orders")}}> <i style={{marginRight:'15px',position:'relative',left:'4px'}} class='fas fa-cloud-download-alt'></i> <p>load orders</p></li>
                            <li onClick={()=>{navigate("/monitor_orders")}}><i style={{marginRight:'15px',position:'relative',left:'4px'}} class='far fa-eye'></i> <p>monitor orders</p></li>
                            <li onClick={()=>{navigate("/loxbox_areas")}}><i class="material-icons">location_on</i><p>loxbox areas</p></li>
                            <li onClick={()=>{navigate("/settings")}}><i class="material-icons">settings</i><p>settings</p></li>
                        </ul>
                    </div>
                </div>:

                <div class="app-sidebar-hidden">
                    <div class="app-sidebar-hidden-header">
                        <i onClick={toggleSidebar} class='fas fa-arrow-right'></i>
                    </div>
                    <div class="app-sidebar-hidden-logo">
                        <img src='http://127.0.0.1:8000/media/maw_logo.jpg' />
                    </div>
                    <div class="app-sidebar-hidden-navigation">
                        <ul>
                            <li  onClick={()=>{navigate("/load_orders")}}> <i class='fas fa-cloud-download-alt'></i></li>
                            <li onClick={()=>{navigate("/monitor_orders")}}><i class='far fa-eye'></i> </li>
                            <li onClick={()=>{navigate("/loxbox_areas")}}><i class="material-icons">location_on</i></li>
                            <li onClick={()=>{navigate("/settings")}}><i class="material-icons">settings</i></li>
                        </ul>
                    </div>
                </div>
            }

        </div>
    )
}
export default AppSidebar ;
