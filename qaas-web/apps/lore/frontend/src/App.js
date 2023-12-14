import React from 'react';
import MainPage from './components/MainPage';
import { Route, Routes } from 'react-router-dom';
import LoopPage from './components/LoopPage';
import { HashRouter } from 'react-router-dom';

function App() {
    return (
        <HashRouter >
            <Routes>
                <Route path="/" element={<MainPage />} />
                <Route path="/loop" element={<LoopPage />} />
            </Routes>
        </HashRouter>

    );
}

export default App;