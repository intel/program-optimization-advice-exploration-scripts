import React, { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Route, Routes } from 'react-router-dom';

import WelcomePage from './text_pages/WelcomePage';
import UserInputStepper from './job_submission/UserInputInteractive';
import LoginPage from './LoginPage';
import GeneratedPage from './job_submission/GeneratedPage';
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
import IceLake from './text_pages/systemconfig/IceLake';
import SapphireRapids from './text_pages/systemconfig/SapphireRapids';
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
import SystemConfig from './text_pages/systemconfig/SystemConfig';
import MultiCompilerGains from './text_pages/MultiCompilerGains';
import QaaSSearches from './text_pages/QaaSSearches';
import QaaSSearchesL2 from './text_pages/QaaSSearchesL2';
import NavigationPage from './navigation/NavigationPage';
import OverViewQaaS from './text_pages/OverViewQaaS';
import UnicorePerfContents from './text_pages/clickin/UnicorePerfContents';
import MultiprocessorCompContents from './text_pages/clickin/MultiprocessorCompContents';
import MultiprocessorPerfContents from './text_pages/clickin/MultiprocessorPerfContents';
import PerfImprove from './text_pages/clickin/PerfImprove';
import FlagRecMiniapps from './text_pages/clickin/FlagRecMiniapps';
import AMGHACCClickTarget from './text_pages/clickin/AMGHACCClickTarget';
import TableOfContents from './TableOfContents';
import ApplicationPortability from './text_pages/clickin/ApplicationPortability';
import BrowseResult from './job_submission/BrowseResult';
import SettingsSelector from './job_submission/SettingSelector';
export const layoutRoutes = [
    { path: "/input", component: UserInputStepper },
    { path: "/settings_select", component: SettingsSelector },

    { path: "/results", component: BrowseResult },
    { path: "/definitions", component: DefinitionsTab },
    { path: "/login", component: LoginPage },
    { path: "/", component: NavigationPage },
    { path: "/table_of_contents", component: TableOfContents },

    { path: "/overview", component: OverViewQaaS },
    { path: "/qaas/overview/unicore_performance_comparisons", component: UnicorePerfContents },
    { path: "/qaas/overview/compiler_comparison", component: MultiprocessorCompContents },
    { path: "/qaas/overview/multicore_performance_comparisons", component: MultiprocessorPerfContents },
    { path: "/qaas/overview/how_to_improve_performance", component: PerfImprove },
    { path: "/qaas/overview/developer_flag_recommendations", component: FlagRecMiniapps },
    { path: "/qaas/overview/AMG_HACC_click_target", component: AMGHACCClickTarget },
    { path: "/qaas/overview/application_portability", component: ApplicationPortability },

    { path: "/qaas/cq_overview", component: CQOverview },
    // { path: "/qaas/cq_overview_performance", component: CQOverviewPerformance },
    // { path: "/qaas", component: WelcomePage },
    // { path: "/qaas/quality_definitions", component: QualityDefinitions },
    { path: "/qaas/constraints_and_scope", component: ConstraintsAndScope },
    // { path: "/qaas/initial_qaas_offerings", component: InitialQaaSOfferings },
    // { path: "/qaas/miniapps", component: Miniapps },
    // { path: "/qaas/apps", component: Apps },
    // { path: "/qaas/libraries", component: Libraries },
    // { path: "/qaas/cq_overview_portability", component: Portability },
    // { path: "/qaas/gf_cor", component: Gfcor },
    // { path: "/qaas/gf_system", component: GfSystem },
    // { path: "/qaas/gf_arch", component: GfArch },
    // { path: "/qaas/cq_overview_multiprocessor", component: Multiprocessor },
    // { path: "/qaas/compiler_details", component: CompilerDetails },
    // { path: "/qaas/quality_10_year_trend_conclusions", component: Quality10YearTrendConclusions },
    // { path: "/qaas/perf_by_scalability_type", component: PerfByScalabilityType },
    // { path: "/qaas/gf_cost", component: GfCost },
    // { path: "/qaas/type_of_scaling_replication_factors", component: TypeOfScaling },
    // { path: "/qaas/oneview", component: Oneview },
    // { path: "/qaas/best_app_insights_per_domain", component: BestAppInsightsPerDomain },
    // { path: "/qaas/automatic_application_analysis", component: AutomaticApplicationAnalysis },
    // { path: "/qaas/manual_interactive_mode", component: ManualInteractiveMode },
    // { path: "/qaas/quality_10_year_trend_realities", component: Quality10YearTrendRealities },
    // { path: "/qaas/multi_compiler_gains", component: MultiCompilerGains },
    // { path: "/qaas/qaas_searches", component: QaaSSearches },
    // { path: "/qaas/qaas_searches_l2", component: QaaSSearchesL2 },
    { path: "/system_config", component: SystemConfig },
    // { path: "/system_config/sky_lake", component: SkyLake },
    // { path: "/system_config/ice_lake", component: IceLake },
    // { path: "/system_config/sapphire_rapids", component: SapphireRapids },
    // { path: "/system_config/icc", component: ICC },
    // { path: "/system_config/gcc", component: GCC }
];
const otherRoutes = [

    { path: "/generated", component: GeneratedPage },
]

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

        <Routes>

            {layoutRoutes.map(({ path, component: Component }) => (
                <Route key={path} path={path} element={<Component />} />
            ))}
            {otherRoutes.map(({ path, component: Component }) => (
                <Route key={path} path={path} element={<Component />} />
            ))}
            {/* <Route path="*" element={
                <FixedMenuLayout drawerContent={drawerContent} mainContent={
                    <Routes>
                        {layoutRoutes.map(({ path, component: Component }) => (
                            <Route key={path} path={path} element={<Component />} />
                        ))}
                    </Routes>
                }
                />
            } /> */}


        </Routes>

    );
}
