import React from 'react';
import './css/TopBar.css';
import SelectedRunsBag from './SelectedRunBag';
import { useSelectionContext } from './contexts/SelectionContext';
function TopBar({ setShowGraph }) {
    const { selectedRows, handleRowSelection, baseline, handleBaselineSelection } = useSelectionContext();

    return (
        <div className="top-bar">
            <span className="home">ONE View: Application Repository for Developers</span>
            <div className="selected-runs-bag">
                <SelectedRunsBag selectedRows={selectedRows} setSelectedRows={handleRowSelection} baseline={baseline} setBaseline={handleBaselineSelection} setShowGraph={setShowGraph} />
            </div>
        </div>
    );
}

export default TopBar;