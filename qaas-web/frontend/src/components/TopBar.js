import React from 'react';
import './css/TopBar.css';
import SelectedRunsBag from './SelectedRunBag';

function TopBar({ selectedRows, setSelectedRows }) {


    return (
        <div className="top-bar">
            <span className="home">ONE View: Application Repository for Developers</span>
            <div className="selected-runs-bag">
                <SelectedRunsBag selectedRows={selectedRows} setSelectedRows={setSelectedRows} />
            </div>
        </div>
    );
}

export default TopBar;