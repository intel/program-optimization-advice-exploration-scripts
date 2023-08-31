import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
// import TimestampListBox from './components/TimestampListBox';
import { BrowserRouter, Route, Routes } from "react-router-dom";
// import LaunchOneviewPage from './components/LaunchOneviewPage';
import WelcomePage from './components/WelcomePage';
import BrowseResult from './components/BrowseResult';
import UserInputStepper from './components/UserInputInteractive';
import QaasPage from './components/QaasPage';
import LoginPage from './components/LoginPage';
import CatalogPage from './components/CatalogPage';
import LegalPage from './components/LegalPage';
import ToolBackgroundPage from './components/ToolBackgroundPage';
import GeneratedPage from './components/GeneratedPage';
import QualityDefinitions from './components/QualityDefinitions';
import ConstraintsAndScope from './components/ConstraintsAndScope';
import WelcomePageTableOfContentsDrawer from './components/WelcomePageTableOfContentsDrawer';
import FixedMenuLayout from './components/layouts/FixedMenuLayout';
import TopBar from './components/TopBar';
export default function App() {

  const [isLoading, setIsLoading] = useState(false);
  const [shouldLoadHTML, setShouldLoadHTML] = useState(false);
  const drawerContent = <WelcomePageTableOfContentsDrawer />;

  return (
    <BrowserRouter>
      <TopBar />
      <Routes>
        <Route path="/input" element={<UserInputStepper isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />} />
        <Route path="/result" element={<BrowseResult isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />} />
        <Route path="*" element={
          <FixedMenuLayout drawerContent={drawerContent} mainContent={
            <Routes>
              <Route path="/" element={<WelcomePage />} />
              <Route path="/qaas" element={<QaasPage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/legal" element={<LegalPage />} />
              <Route path="/catalog" element={<CatalogPage />} />
              <Route path="/tool" element={<ToolBackgroundPage />} />
              <Route path="/generated" element={<GeneratedPage />} />
              <Route path="/quality_definitions" element={<QualityDefinitions />} />
              <Route path="/constraints_and_scope" element={<ConstraintsAndScope />} />
            </Routes>
          } />
        } />
      </Routes>
    </BrowserRouter>

  );
}

/** render */
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
