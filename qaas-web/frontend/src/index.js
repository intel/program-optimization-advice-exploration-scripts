import React from 'react';
import ReactDOM from 'react-dom/client';
// import TimestampListBox from './components/TimestampListBox';
import { BrowserRouter, Route, Routes } from "react-router-dom";
// import LaunchOneviewPage from './components/LaunchOneviewPage';
import WelcomePage from './components/WelcomePage';
import Navbar from './components/NavBar';
import BrowseResult from './components/BrowseResult';
import UserInputStepper from './components/UserInputInteractive';
export default function App() {

  return (

    <div>
      <React.StrictMode>
        <BrowserRouter>
          <Navbar />

          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/input" element={<UserInputStepper />} />
            <Route path="/result" element={<BrowseResult />} />

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
