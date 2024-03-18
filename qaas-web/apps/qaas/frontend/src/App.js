import React, { useState } from 'react';
import { HashRouter, Routes, Route, useLocation } from 'react-router-dom';
import QaaSRouting from './components/QaaSRouting';
import WelcomePageTableOfContentsDrawer from './components/sidebar/WelcomePageTableOfContentsDrawer';
import TopBar from './components/TopBar';
import GeneratedPage from './components/job_submission/GeneratedPage';
import { SSEProvider } from './components/contexts/SSEContext';

export default function App() {

    const ConditionalTopBar = ({ noTopBarRoutes }) => {
        const location = useLocation();
        const showTopBar = !noTopBarRoutes.some(route => route.path === location.pathname);
        return showTopBar ? <TopBar /> : null;
    };
    const [isLoading, setIsLoading] = useState(false);
    const [shouldLoadHTML, setShouldLoadHTML] = useState(false);
    const [drawerContent, setDrawerContent] = useState(<WelcomePageTableOfContentsDrawer />);
    const noTopBarRoutes = [

        { path: "/generated", component: GeneratedPage },
    ]

    return (
        <SSEProvider>

            <HashRouter>
                <div className="main-container">
                    <ConditionalTopBar noTopBarRoutes={noTopBarRoutes} />
                    <Routes>

                        {noTopBarRoutes.map(({ path, component: Component }) => (
                            <Route key={path} path={path} element={<Component />} />
                        ))}
                    </Routes>
                    <div className="content-container">
                        <QaaSRouting drawerContent={drawerContent} setDrawerContent={setDrawerContent} isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />
                    </div>
                </div>
            </HashRouter>
        </SSEProvider>


    );
}

