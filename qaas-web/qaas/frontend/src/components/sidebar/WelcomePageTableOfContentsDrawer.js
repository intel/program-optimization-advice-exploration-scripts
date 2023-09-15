import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import { useNavigate } from 'react-router-dom';
import DrawerItemsList from './DrawerItemList';

const WelcomePageTableOfContentsDrawer = () => {
    const navigate = useNavigate();
    const [selectedItem, setSelectedItem] = useState(null);
    const [expandedSections, setExpandedSections] = useState([]);

    const navigateToSection = (path, children) => {
        if (children) {
            if (!expandedSections.includes(path)) {
                setExpandedSections(prevSections => [...prevSections, path]);
            } else {
                setExpandedSections(prevSections => prevSections.filter(section => section !== path));
            }
        } else {
            navigate(path);
            setSelectedItem(path);
        }
    };

    const drawerItems = [
        { level: 1, text: 'Overview', path: '/' },
        { level: 1, text: 'A. Quality definitions', path: '/quality_definitions' },
        { level: 1, text: 'B. Constraints and Scope', path: '/constraints_and_scope' },
        {
            level: 1, text: 'C. Initial QaaS offerings', path: '/initial_qaas_offerings', children: [
                {
                    level: 2, text: 'C1. CQ Overview', path: '/c1', children: [
                        { level: 3, text: 'Overview', path: '/cq_overview' },
                        { level: 3, text: 'C1.1 Performance', path: '/cq_overview_performance' },
                        { level: 3, text: 'C1.2 Portability', path: '/cq_overview_portability' },
                        { level: 3, text: 'C1.3 Energy', path: '/cq_overview_energy' },
                    ]
                },
                { level: 2, text: 'C2. Automatic application analysis', path: '/automatic_application_analysis' },
                { level: 2, text: 'C3. Manual Interactive Mode', path: '/manual_interactive_mode' },
                {
                    level: 2, text: 'C4. Quality 10-year trend realities', path: '/c4', children: [
                        { level: 3, text: 'Overview', path: '/quality_10_year_trend_realities' },
                        { level: 3, text: 'C4.1 Conclusions', path: '/quality_10_year_trend_conclusions' },
                    ]
                },
            ]
        },
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

export default WelcomePageTableOfContentsDrawer;
