import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import { useNavigate } from 'react-router-dom';
import DrawerItemsList from './DrawerItemList';
import { useNavigationState } from '../hooks/useNavigationState';

const drawerItems = [
    { level: 1, text: 'Overview', path: '/system_config' },
    {
        level: 1, text: 'Architectures', path: '/system_config/architecture', children: [
            { level: 2, text: 'Sky Lake', path: '/system_config/sky_lake' },
            { level: 2, text: 'Ice Lake', path: '/system_config/ice_lake' },
            { level: 2, text: 'Sapphire Rapids', path: '/system_config/sapphire_rapids' },
        ],
    },


    {
        level: 1, text: 'Compilers', path: '/system_config/compilers', children: [
            { level: 2, text: 'ICC', path: '/system_config/icc' },
            { level: 2, text: 'GCC', path: '/system_config/gcc' },
        ],

    },


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
