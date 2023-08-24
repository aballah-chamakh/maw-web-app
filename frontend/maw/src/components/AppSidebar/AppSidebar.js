
import { useState,useEffect } from "react"
import { useNavigate } from 'react-router-dom';
import App from '../../App';
import './AppSidebar.scss' ;
import {Link} from 'react-router-dom' ;


const AppSidebar = (props)=>{
    const [isSidebarHidden,setIsSidebarHidden] = useState(false) ;
    const navigate = useNavigate()
    const [currentNavIdx,setCurrentNavIdx] = useState(1)

    useEffect(()=>{
       console.log("useEffect")
       let activeEl = document.querySelector(`img.active, li.active`);
       let clickedEl =  document.querySelector(`img[data-nav-idx='${currentNavIdx}'], li[data-nav-idx='${currentNavIdx}']`);
       if (activeEl) {
        activeEl.classList.remove('active')
       }
       clickedEl.classList.add('active')
    },[currentNavIdx])

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
    const handleNavigation = function (e,route){
      
        console.log("handle navigation")
        let clickedEl = e.target.tagName == 'P' || e.target.tagName == 'I'  ? e.target.parentElement : e.target ;
        setCurrentNavIdx(clickedEl.getAttribute('data-nav-idx'))
        navigate(route)
        
    }

    return(
        <div className="app-sidebar-container">
            { ! isSidebarHidden  ? 
                <div class="app-sidebar-apparent">
                    <div class="app-sidebar-apparent-header">
                        <img src='http://127.0.0.1:8000/media/upper_logo.png' height={'30px'}/>
                        <i onClick={toggleSidebar} class='fas fa-arrow-left'></i>
                    </div>
                    <div class="app-sidebar-apparent-logo">
                        <img data-nav-idx={0} onClick={(e)=>{handleNavigation(e,"/account")}}  src='http://127.0.0.1:8000/media/logo_8.png' />
                    </div>
                    <div class="app-sidebar-apparent-navigation">
                        <ul>
                            <li onClick={(e)=>{handleNavigation(e,"/load_orders")}} data-nav-idx={1}> <i style={{marginRight:'15px',position:'relative',left:'4px'}} class='fas fa-cloud-download-alt'></i> <p>Chargement des commandes</p></li>
                            <li onClick={(e)=>{handleNavigation(e,"/monitor_orders")}} data-nav-idx={2} ><i style={{marginRight:'15px',position:'relative',left:'4px'}} class='far fa-eye'></i> <p>Suivi des Commandes</p></li>
                            <li onClick={(e)=>{handleNavigation(e,"/carrier_per_zone")}} data-nav-idx={3} ><i class="material-icons">location_on</i><p>Transporteur par Zone</p></li>
                            <li onClick={(e)=>{handleNavigation(e,"/carriers")}} data-nav-idx={4} ><i class="material-icons" style={{marginLeft:'2px'}}>local_shipping</i><p>Transporteur</p></li>
                            <li onClick={(e)=>{handleNavigation(e,"/errors")}} data-nav-idx={5} ><i class="material-icons">error_outline</i><p>Erreur</p></li>
                            <li onClick={(e)=>{handleNavigation(e,"/settings")}} data-nav-idx={6} ><i class="material-icons">settings</i><p>Paramètres</p></li>
                        </ul>
                    </div>
                </div>:

                <div class="app-sidebar-hidden">
                    <div class="app-sidebar-hidden-header">
                        <i onClick={toggleSidebar} class='fas fa-arrow-right'></i>
                    </div>
                    <div class="app-sidebar-hidden-logo">
                        <img data-nav-idx={0} onClick={(e)=>{handleNavigation(e,"/account")}}  src='http://127.0.0.1:8000/media/icon_logo.png' />
                    </div>
                    <div class="app-sidebar-hidden-navigation">
                        <ul>
                            <li  onClick={(e)=>{handleNavigation(e,"/load_orders")}} data-nav-idx={1} > <i class='fas fa-cloud-download-alt'></i></li>
                            <li onClick={(e)=>{handleNavigation(e,"/monitor_orders")}} data-nav-idx={2} ><i class='far fa-eye'></i> </li>
                            <li onClick={(e)=>{handleNavigation(e,"/carrier_per_zone")}} data-nav-idx={3} ><i class="material-icons">location_on</i></li>
                            <li onClick={(e)=>{handleNavigation(e,"/carriers")}} data-nav-idx={4} ><i class="material-icons" >local_shipping</i></li>
                            <li onClick={(e)=>{handleNavigation(e,"/errors")}} data-nav-idx={5} ><i class="material-icons">error_outline</i></li>
                            <li onClick={(e)=>{handleNavigation(e,"/settings")}} data-nav-idx={6} ><i class="material-icons">settings</i></li>
                        </ul>
                    </div>
                </div>
            }

        </div>
    )
}
export default AppSidebar ;
