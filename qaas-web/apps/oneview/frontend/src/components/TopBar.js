import React from 'react';
import './css/TopBar.css';
import SelectedRunsBag from './SelectedRunBag';
import { useSelectionContext } from './contexts/SelectionContext';
function TopBar({ setSelectedRows, baseline, setBaseline, setShowGraph }) {
    const { selectedRows } = useSelectionContext();


    return (
        <div className="top-bar">
            <span className="home">ONE View: Application Repository for Developers</span>
            <div className="selected-runs-bag">
                <SelectedRunsBag selectedRows={selectedRows} setSelectedRows={setSelectedRows} baseline={baseline} setBaseline={setBaseline} setShowGraph={setShowGraph} />
            </div>
        </div>
    );
}

export default TopBar;