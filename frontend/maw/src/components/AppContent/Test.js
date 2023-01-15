import { useEffect,useState } from "react"


const Test = ()=>{
    const [cnt,setCnt] = useState(0)
    let any = 0 

    useEffect(()=>{
        alert('CALLING USE EFFECT')
        return ()=>{
            alert("CALLING THE CLEAN UP "+any)
        }
    },[])




    return(
        <div>
            <h1>{cnt} {alert("RE-RENDER THE COMPONENT")}</h1>
            <button onClick={()=>{any += 100 ; alert(any)}}>INCREASE</button>
        </div>
    )

    /*
    const [anyx,setAnyx] = useState(null)
    let any = null 

    alert("render cycle => any : "+any+" anyx : "+anyx)
   
    useEffect(()=>{
        alert('CALLING USE EFFECT')
        return ()=>{
            alert("cleanup "+any)
        }
    },[any,anyx])

    const handleClick = ()=>{
        alert("any before  : "+any)
        any += 100
        setAnyx(100)
        alert("any after "+any)
    }

    const realRender = ()=>{
        alert("real render")
    }

    const showAny = ()=>{
        alert("show anyyyy : "+any)
    }


    return (
      <div>
        <h1 onClick={showAny}>Testing react {showAny()}</h1>
        <input onChange={showAny} />
        <button onClick={handleClick}>click me</button>
      </div>
    ) */
}
export default Test