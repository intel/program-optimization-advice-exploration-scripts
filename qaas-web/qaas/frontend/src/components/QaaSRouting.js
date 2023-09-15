import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Route, Routes } from 'react-router-dom';

import WelcomePage from './text_pages/WelcomePage';
import BrowseResult from './BrowseResult';
import UserInputStepper from './UserInputInteractive';
import LoginPage from './LoginPage';
import GeneratedPage from './GeneratedPage';
import QualityDefinitions from './text_pages/QualityDefinitions';
import ConstraintsAndScope from './text_pages/ConstraintsAndScope';
import WelcomePageTableOfContentsDrawer from './sidebar/WelcomePageTableOfContentsDrawer';
import FixedMenuLayout from './layouts/FixedMenuLayout';
import CQOverview from './text_pages/CQOverview';
import CQOverviewPerformance from './text_pages/CQOverviewPerformance';
import AutomaticApplicationAnalysis from './text_pages/AutomaticApplicationAnalysis';
import ManualInteractiveMode from './text_pages/ManualInteractiveMode';
import Quality10YearTrendRealities from './text_pages/Quality10YearTrendRealities';
import Quality10YearTrendConclusions from './text_pages/Quality10YearTrendConclusions';
import IceLake from './text_pages/IceLake';
import SapphireRapids from './text_pages/SapphireRapids';
import SystemConfigDrawer from './sidebar/SystemConfigDrawer';
export default function QaaSRouting({ drawerContent, setDrawerContent, isLoading, shouldLoadHTML, setIsLoading, setShouldLoadHTML }) {
    const location = useLocation();

    useEffect(() => {
        if (location.pathname.startsWith('/system_config')) {
            setDrawerContent(<SystemConfigDrawer />);
        } else {
            setDrawerContent(<WelcomePageTableOfContentsDrawer />);
        }
    }, [location, setDrawerContent]);

    return (
        <>
            <Routes>
                <Route path="/input" element={<UserInputStepper isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />} />
                <Route path="/result" element={<BrowseResult isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />} />
                <Route path="*" element={
                    <FixedMenuLayout drawerContent={drawerContent} mainContent={
                        <Routes>
                            <Route path="/" element={<WelcomePage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/generated" element={<GeneratedPage />} />
                            <Route path="/quality_definitions" element={<QualityDefinitions />} />
                            <Route path="/constraints_and_scope" element={<ConstraintsAndScope />} />
                            <Route path="/cq_overview" element={<CQOverview />} />
                            <Route path="/cq_overview_performance" element={<CQOverviewPerformance />} />
                            <Route path="/automatic_application_analysis" element={<AutomaticApplicationAnalysis />} />
                            <Route path="/manual_interactive_mode" element={<ManualInteractiveMode />} />
                            <Route path="/quality_10_year_trend_realities" element={<Quality10YearTrendRealities />} />
                            <Route path="/quality_10_year_trend_conclusions" element={<Quality10YearTrendConclusions />} />
                            <Route path="/system_config/ice_lake" element={<IceLake />} />
                            <Route path="/system_config/sapphire_rapids" element={<SapphireRapids />} />
                        </Routes>
                    } />
                } />
            </Routes>
        </>
    );
}
