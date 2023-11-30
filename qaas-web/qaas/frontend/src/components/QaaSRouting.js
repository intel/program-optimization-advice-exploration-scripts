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
import CompilerDetails from './text_pages/CompilerDetails';
import SystemConfig from './text_pages/SystemConfig';
import SkyLake from './text_pages/SkyLake';
import MultiCompilerGains from './text_pages/MultiCompilerGains';
import QaaSSearches from './text_pages/QaaSSearches';
import QaaSSearchesL2 from './text_pages/QaaSSearchesL2';
import NavigationPage from './navigation/NavigationPage';
import OverViewQaaS from './text_pages/OverViewQaaS';
import UnicorePerfContents from './text_pages/UnicorePerfContents';
import MultiprocessorCompContents from './text_pages/clickin/MultiprocessorCompContents';
import MultiprocessorPerfContents from './text_pages/clickin/MultiprocessorPerfContents';
import PerfImprove from './text_pages/clickin/PerfImprove';
import FlagRecMiniapps from './text_pages/FlagRecMiniapps';
import AMGHACCClickTarget from './text_pages/clickin/AMGHACCClickTarget';
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
                <Route path="/" element={<NavigationPage />} />

                <Route path="*" element={
                    <FixedMenuLayout drawerContent={drawerContent} mainContent={
                        <Routes>
                            <Route path="/qaas" element={<WelcomePage />} />
                            <Route path="/qaas/quality_definitions" element={<QualityDefinitions />} />
                            <Route path="/qaas/constraints_and_scope" element={<ConstraintsAndScope />} />
                            <Route path="/qaas/initial_qaas_offerings" element={<InitialQaaSOfferings />} />
                            <Route path="/qaas/overview" element={<OverViewQaaS />} />
                            <Route path="/qaas/overview/unicore_perf_contents" element={<UnicorePerfContents />} />
                            <Route path="/qaas/overview/multiprocessor_comp_contents" element={<MultiprocessorCompContents />} />
                            <Route path="/qaas/overview/multiprocessor_perf_contents" element={<MultiprocessorPerfContents />} />
                            <Route path="/qaas/overview/perf_improve" element={<PerfImprove />} />
                            <Route path="/qaas/overview/flag_rec_miniapps" element={<FlagRecMiniapps />} />
                            <Route path="/qaas/overview/AMG_HACC_click_target" element={<AMGHACCClickTarget />} />

                            <Route path="/qaas/cq_overview" element={<CQOverview />} />
                            <Route path="/qaas/cq_overview_performance" element={<CQOverviewPerformance />} />
                            <Route path="/qaas/miniapps" element={<Miniapps />} />
                            <Route path="/qaas/apps" element={<Apps />} />
                            <Route path="/qaas/libraries" element={<Libraries />} />
                            <Route path="/qaas/cq_overview_portability" element={<Portability />} />
                            <Route path="/qaas/gf_cor" element={<Gfcor />} />
                            <Route path="/qaas/gf_system" element={<GfSystem />} />
                            <Route path="/qaas/gf_arch" element={<GfArch />} />
                            <Route path="/qaas/cq_overview_multiprocessor" element={<Multiprocessor />} />
                            <Route path="/qaas/compiler_details" element={<CompilerDetails />} />
                            <Route path="/qaas/quality_10_year_trend_conclusions" element={<Quality10YearTrendConclusions />} />
                            <Route path="/qaas/perf_by_scalability_type" element={<PerfByScalabilityType />} />
                            <Route path="/qaas/gf_cost" element={<GfCost />} />
                            <Route path="/qaas/type_of_scaling_replication_factors" element={<TypeOfScaling />} />
                            <Route path="/qaas/oneview" element={<Oneview />} />
                            <Route path="/qaas/best_app_insights_per_domain" element={<BestAppInsightsPerDomain />} />
                            <Route path="/qaas/automatic_application_analysis" element={<AutomaticApplicationAnalysis />} />
                            <Route path="/qaas/manual_interactive_mode" element={<ManualInteractiveMode />} />
                            <Route path="/qaas/quality_10_year_trend_realities" element={<Quality10YearTrendRealities />} />
                            <Route path="/qaas/multi_compiler_gains" element={<MultiCompilerGains />} />
                            <Route path="/qaas/qaas_searches" element={<QaaSSearches />} />
                            <Route path="/qaas/qaas_searches_l2" element={<QaaSSearchesL2 />} />

                            <Route path="/system_config" element={<SystemConfig />} />
                            <Route path="/system_config/sky_lake" element={<SkyLake />} />
                            <Route path="/system_config/ice_lake" element={<IceLake />} />
                            <Route path="/system_config/sapphire_rapids" element={<SapphireRapids />} />

                        </Routes>
                    } />
                } />
            </Routes>
        </>
    );
}
