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
import DefinitionsTab from './text_pages/DefinitionsTab';
import InitialQaaSOfferings from './text_pages/InitialQaaSOfferings';
import Miniapps from './text_pages/Miniapps';
import Apps from './text_pages/Apps';
import Libraries from './text_pages/Libraries';
import Portability from './text_pages/Portability';
import Gfcor from './text_pages/Gfcor';
import Multiprocessor from './text_pages/Multiprocessor';
import GfSystem from './text_pages/GfSystem';
import GfArch from './text_pages/GfArch';
import PerfByScalabilityType from './text_pages/PerfByScalabilityType';
import GfCost from './text_pages/GfCost';
import TypeOfScaling from './text_pages/TypeOfScaling';
import Oneview from './text_pages/Oneview';
import BestAppInsightsPerDomain from './text_pages/BestAppInsightsPerDomain';
import CompilerDetails  from './text_pages/CompilerDetails';
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
                <Route path="/definitions" element={<DefinitionsTab />} />
                <Route path="/login" element={<LoginPage />} />

                <Route path="*" element={
                    <FixedMenuLayout drawerContent={drawerContent} mainContent={
                        <Routes>
                            <Route path="/" element={<WelcomePage />} />
                            <Route path="/generated" element={<GeneratedPage />} />
                            <Route path="/quality_definitions" element={<QualityDefinitions />} />
                            <Route path="/constraints_and_scope" element={<ConstraintsAndScope />} />
                            <Route path="/initial_qaas_offerings" element={<InitialQaaSOfferings />} />
                            <Route path="/cq_overview" element={<CQOverview />} />

                            <Route path="/cq_overview_performance" element={<CQOverviewPerformance />} />
                            <Route path="/miniapps" element={<Miniapps />} />
                            <Route path="/apps" element={<Apps />} />
                            <Route path="/libraries" element={<Libraries />} />
                            <Route path="/cq_overview_portability" element={<Portability />} />
                            <Route path="/gf_cor" element={<Gfcor />} />
                            <Route path="/gf_system" element={<GfSystem />} />
                            <Route path="/gf_arch" element={<GfArch />} />

                            <Route path="/cq_overview_multiprocessor" element={<Multiprocessor />} />
                            <Route path="/compiler_details" element={<CompilerDetails />} />

                            <Route path="/perf_by_scalability_type" element={<PerfByScalabilityType />} />
                            <Route path="/gf_cost" element={<GfCost />} />
                            <Route path="/type_of_scaling_replication_factors" element={<TypeOfScaling />} />
                            <Route path="/oneview" element={<Oneview />} />
                            <Route path="/best_app_insights_per_domain" element={<BestAppInsightsPerDomain />} />

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
