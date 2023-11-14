import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import { useNavigate } from 'react-router-dom';
import DrawerItemsList from './DrawerItemList';
import { useNavigationState } from '../hooks/useNavigationState';

const drawerItems = [
    { level: 1, text: 'Overview', path: '/system_config', status: 'empty' },
    { level: 1, text: 'Architectures', path: '/system_config/architecture' },

    { level: 2, text: 'Sky Lake', path: '/system_config/sky_lake' },
    { level: 2, text: 'Ice Lake', path: '/system_config/ice_lake' },
    { level: 2, text: 'Sapphire Rapids', path: '/system_config/sapphire_rapids' },
    { level: 1, text: 'Compilers', path: '/system_config/compilers' },

];

const SystemConfigDrawer = () => {
    const initialHash = window.location.hash.split('#').pop();
    const { expandedSections, selectedItem, navigateToSection, goBack, navStack } = useNavigationState(drawerItems, initialHash);



    return (
        <div>
            <Drawer
                className="drawer"
                anchor="left"
                variant="permanent"
                ModalProps={{
                    hideBackdrop: true,
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
