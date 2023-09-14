import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { HashRouter } from 'react-router-dom';
import WelcomePage from './components/text_pages/WelcomePage';
import BrowseResult from './components/BrowseResult';
import UserInputStepper from './components/UserInputInteractive';
import LoginPage from './components/LoginPage';
import CatalogPage from './components/text_pages/CatalogPage';
import LegalPage from './components/text_pages/LegalPage';
import ToolBackgroundPage from './components/text_pages/ToolBackgroundPage';
import GeneratedPage from './components/GeneratedPage';
import QualityDefinitions from './components/text_pages/QualityDefinitions';
import ConstraintsAndScope from './components/text_pages/ConstraintsAndScope';
import WelcomePageTableOfContentsDrawer from './components/WelcomePageTableOfContentsDrawer';
import FixedMenuLayout from './components/layouts/FixedMenuLayout';
import TopBar from './components/TopBar';
import CQOverview from './components/text_pages/CQOverview';
import CQOverviewPerformance from './components/text_pages/CQOverviewPerformance';
import AutomaticApplicationAnalysis from './components/text_pages/AutomaticApplicationAnalysis';
import ManualInteractiveMode from './components/text_pages/ManualInteractiveMode';
import Quality10YearTrendRealities from './components/text_pages/Quality10YearTrendRealities';
import Quality10YearTrendConclusions from './components/text_pages/Quality10YearTrendConclusions';
export default function App() {

    const [isLoading, setIsLoading] = useState(false);
    const [shouldLoadHTML, setShouldLoadHTML] = useState(false);
    const drawerContent = <WelcomePageTableOfContentsDrawer />;

    return (
        <HashRouter>
            <TopBar />
            <Routes>
                <Route path="/input" element={<UserInputStepper isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />} />
                <Route path="/result" element={<BrowseResult isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />} />
                <Route path="*" element={
                    <FixedMenuLayout drawerContent={drawerContent} mainContent={
                        <Routes>
                            <Route path="/" element={<WelcomePage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/legal" element={<LegalPage />} />
                            <Route path="/catalog" element={<CatalogPage />} />
                            <Route path="/tool" element={<ToolBackgroundPage />} />
                            <Route path="/generated" element={<GeneratedPage />} />
                            <Route path="/quality_definitions" element={<QualityDefinitions />} />
                            <Route path="/constraints_and_scope" element={<ConstraintsAndScope />} />
                            <Route path="/cq_overview" element={<CQOverview />} />
                            <Route path="/cq_overview_performance" element={<CQOverviewPerformance />} />
                            <Route path="/automatic_application_analysis" element={<AutomaticApplicationAnalysis />} />
                            <Route path="/manual_interactive_mode" element={<ManualInteractiveMode />} />
                            <Route path="/quality_10_year_trend_realities" element={<Quality10YearTrendRealities />} />
                            <Route path="/quality_10_year_trend_conclusions" element={<Quality10YearTrendConclusions />} />

                        </Routes>
                    } />
                } />
            </Routes>
        </HashRouter>

    );
}

// import React from "react";
// const App = () => {
//     return <h1>Hello React</h1>;
// };

// export default App;