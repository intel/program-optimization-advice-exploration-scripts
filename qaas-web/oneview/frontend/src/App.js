import React from 'react';
import MainPage from './components/MainPage';
import { Route, Routes } from 'react-router-dom';
import GeneratedPage from './components/GeneratedPage';
import SelectedRunsBag from './components/SelectedRunBag';
function App() {
    return (
        <Routes>
            <Route path="/oneview" element={<MainPage />} />

            <Route path="/generated" element={<GeneratedPage />} />

        </Routes>
    );
}

export default App;