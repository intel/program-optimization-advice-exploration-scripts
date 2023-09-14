import React from 'react';
import MainPage from './components/MainPage';
import { Route, Routes } from 'react-router-dom';
import LoopPage from './components/LoopPage';
function App() {
    return (
        <Routes>
            <Route path="/" element={<MainPage />} />
            <Route path="/loop" element={<LoopPage />} />
        </Routes>
    );
}

export default App;