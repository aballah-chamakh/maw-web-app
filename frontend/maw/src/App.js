
import AppSidebar from './components/AppSidebar/AppSidebar';
import AppContent from './components/AppContent/AppContent';
import './App.scss'
import "react-widgets/styles.css";



function App() {

  
  return (
    <div className="app-container">
        <AppSidebar/>
        <AppContent/>
    </div>
    
  );
}

export default App;
