import React, { useState } from 'react';
import { HashRouter } from 'react-router-dom';
import QaaSRouting from './components/QaaSRouting';
import WelcomePageTableOfContentsDrawer from './components/sidebar/WelcomePageTableOfContentsDrawer';
import TopBar from './components/TopBar';
export default function App() {

    const [isLoading, setIsLoading] = useState(false);
    const [shouldLoadHTML, setShouldLoadHTML] = useState(false);
    const [drawerContent, setDrawerContent] = useState(<WelcomePageTableOfContentsDrawer />);

    return (
        <HashRouter>
            <div className="main-container">
                <TopBar />
                <div className="content-container">
                    <QaaSRouting drawerContent={drawerContent} setDrawerContent={setDrawerContent} isLoading={isLoading} shouldLoadHTML={shouldLoadHTML} setIsLoading={setIsLoading} setShouldLoadHTML={setShouldLoadHTML} />
                </div>
            </div>
        </HashRouter>

    );
}

