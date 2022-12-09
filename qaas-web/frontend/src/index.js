import React,{useState} from 'react';
import ReactDOM from 'react-dom/client';
// import TimestampListBox from './components/TimestampListBox';
import { BrowserRouter, Route, Routes } from "react-router-dom";
// import LaunchOneviewPage from './components/LaunchOneviewPage';
import WelcomePage from './components/WelcomePage';
import Navbar from './components/NavBar';
import BrowseResult from './components/BrowseResult';
import UserInputStepper from './components/UserInputInteractive';
import QaasPage from './components/QaasPage';
import LoginPage from './components/LoginPage';
import CatalogPage from './components/CatalogPage';
import LegalPage from './components/LegalPage';
import ToolBackgroundPage from './components/ToolBackgroundPage';
export default function App() {

  const [isLoading, setIsLoading] = useState(false);
  const [shouldLoadHTML, setShouldLoadHTML] = useState(false);
  return (

    <div>
      <React.StrictMode>
        <BrowserRouter>
          <Navbar />

          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/input" element={<UserInputStepper isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML}/>} />
            <Route path="/result" element={<BrowseResult isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML}/>} />
            <Route path="/qaas" element={<QaasPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/legal" element={<LegalPage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/tool" element={<ToolBackgroundPage />} />
          </Routes>
        </BrowserRouter>
      </React.StrictMode>
      {/* <GenerateRunButton /> */}
      {/* <TimestampListBox /> */}
      {/* <HomePage /> */}

    </div>
  );
}

/** render */
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
