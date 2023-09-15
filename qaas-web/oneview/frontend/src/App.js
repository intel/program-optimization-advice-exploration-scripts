import React from "react";
import MainPage from './components/MainPage';
import { Route, Routes } from 'react-router-dom';
import GeneratedPage from './components/GeneratedPage';
import SelectedRunsBag from './components/SelectedRunBag';
import { BrowserRouter } from 'react-router-dom';
import { HashRouter } from 'react-router-dom';



const App = () => {
    return (
        <div>
            <HashRouter >
                <Routes>
                    <Route path="/oneview" element={<MainPage />} />
                    <Route path="/generated" element={<GeneratedPage />} />

                </Routes>
            </HashRouter>

        </div>
    );
};

export default App;