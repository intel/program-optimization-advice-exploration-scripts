import React from 'react';
import '../css/drawer.css';

const FixedMenuLayout = ({ drawerContent, mainContent }) => {
    return (
        <div className="layout-container">
            <div className="drawer-width">
                {drawerContent}
            </div>

            <div className="main-content">
                {mainContent}
            </div>
        </div>
    );
};

export default FixedMenuLayout;
