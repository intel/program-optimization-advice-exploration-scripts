import React from 'react';
import '../css/drawer.css'
const FixedMenuLayout = ({ drawerContent, mainContent }) => {
    return (
        <div style={{ display: 'flex' }}>
            <div className='drawer-width' style={{ flexShrink: 0 }}>
                {drawerContent}
            </div>
            <div style={{ flexGrow: 1, marginLeft: '10px' }}>
                {mainContent}
            </div>
        </div>
    );
};

export default FixedMenuLayout;
