import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import { useNavigate } from 'react-router-dom';
import DrawerItemsList from './DrawerItemList';

const SystemConfigDrawer = () => {
    const navigate = useNavigate();
    const [selectedItem, setSelectedItem] = useState(null);
    const [expandedSections, setExpandedSections] = useState([]);

    const navigateToSection = (path) => {
        navigate(path);
        setSelectedItem(path);
    };

    const drawerItems = [
        { level: 1, text: 'Ice Lake', path: '/system_config/ice_lake' },
        { level: 1, text: 'Sapphire Rapids', path: '/system_config/sapphire_rapids' },
    ];

    return (
        <div>
            <Drawer
                className="drawer"
                anchor="left"
                variant="permanent"
                ModalProps={{
                    hideBackdrop: true,
                }}
                sx={{
                    '& .MuiDrawer-paper': {
                        marginTop: '50px',
                        alignItems: 'center',
                        minWidth: '250px',
                    },
                }}
            >
                <List>
                    <DrawerItemsList
                        items={drawerItems}
                        navigateToSection={navigateToSection}
                        selectedItem={selectedItem}
                        expandedSections={expandedSections}
                    />
                </List>
            </Drawer>
        </div>
    );
};

export default SystemConfigDrawer;
