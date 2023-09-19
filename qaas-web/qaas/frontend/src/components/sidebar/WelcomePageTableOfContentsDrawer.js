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
        navigate(path); //  navigate to path
        setSelectedItem(path);

        if (children) { // expand or collapse the children if they exist
            if (!expandedSections.includes(path)) {
                setExpandedSections(prevSections => [...prevSections, path]);
            } else {
                setExpandedSections(prevSections => prevSections.filter(section => section !== path));
            }
        }
    };

    const drawerItems = [
        { level: 1, text: 'Overview', path: '/' },
        {
            level: 1, text: 'A. Quality definitions', path: '/quality_definitions', children: [
                { level: 2, text: 'A.1 Detailed Definitions', path: '/quality_detailed_definitions' },
            ]
        },
        { level: 1, text: 'B. Constraints and Scope', path: '/constraints_and_scope' },
        {
            level: 1, text: 'C. Initial QaaS offerings', path: '/initial_qaas_offerings', children: [
                {
                    level: 2, text: 'C1. CQ Overview', path: '/cq_overview', children: [
                        {
                            level: 3, text: 'C1.1 Performance vs. compilers', path: '/cq_overview_performance', children: [
                                { level: 4, text: 'C1.1.1 Miniapps', path: '/miniapps' },
                                { level: 4, text: 'C1.1.2 Apps', path: '/apps' },
                                { level: 4, text: 'C1.1.3 Libraries', path: '/libraries' },
                            ]
                        },
                        {
                            level: 3, text: 'C1.2 Portability across systems', path: '/cq_overview_portability', children: [
                                { level: 4, text: 'C1.2.1 Intel', path: '/intel' },
                                { level: 4, text: 'C1.2.2 AMD', path: '/amd' },
                                { level: 4, text: 'C1.2.3 Arm', path: '/arm' },
                            ]
                        },
                        {
                            level: 3, text: 'C1.3 Multiprocessor', path: '/cq_overview_multiprocessor', children: [
                                { level: 4, text: 'C1.3.1Best system computer technology [Gf perf/core] per app', path: '/best_system_perf' },
                                { level: 4, text: 'C1.3.2 Best system efficient total MP Performance per App. & Domain [tot Gf/system]', path: '/best_total_system_perf' },
                                { level: 4, text: 'C1.3.3 Architectural performance ratios showing top performer by [Gf]', path: '/architectural_performance_ratios' },
                                { level: 4, text: 'C1.3.2 Performance by scalability type', path: '/perf_by_scalability_type' },
                                { level: 4, text: 'C1.3.3 Best App insights per domain. ', path: '/best_app_insights_per_domain' },
                            ]
                        },
                    ]
                },
                { level: 2, text: 'C2. Automatic application analysis', path: '/automatic_application_analysis' },
                { level: 2, text: 'C3. Manual Interactive Mode', path: '/manual_interactive_mode' },
                {
                    level: 2, text: 'C4. Quality 10-year trend realities', path: '/quality_10_year_trend_realities', children: [
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
                        position: 'static',
                        alignItems: 'center',

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
