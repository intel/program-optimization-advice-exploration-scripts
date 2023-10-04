import React, { useState, useEffect } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import { useNavigate } from 'react-router-dom';
import DrawerItemsList from './DrawerItemList';
import ListItemButton from '@mui/material/ListItemButton';

const drawerItems = [
    { level: 1, text: 'Overview', path: '/' },
    {
        level: 1, text: 'A. Quality definitions', path: '/quality_definitions', children: [
            { level: 2, text: 'A.1 Detailed Definitions', path: '/quality_detailed_definitions', status: 'empty' },
        ]
    },
    { level: 1, text: 'B. Constraints and Scope', path: '/constraints_and_scope' },
    {
        level: 1, text: 'C. Initial QaaS offerings', path: '/initial_qaas_offerings', drillDown: true, children: [
            {
                level: 2, text: 'C1. CQ Overview', path: '/cq_overview', children: [
                    {
                        level: 3, text: 'C1.1 Performance vs. compilers', path: '/cq_overview_performance', children: [
                            {
                                level: 4, text: 'C1.1.1 Miniapps', path: '/miniapps', children: [
                                    { level: 5, text: 'C1.1.1.A Compiler Details', path: '/compiler_details' },

                                ]
                            },
                            { level: 4, text: 'C1.1.2 Apps', path: '/apps' },
                            { level: 4, text: 'C1.1.3 Libraries', path: '/libraries' },
                        ]
                    },
                    {
                        level: 3, text: 'C1.2 Portability across systems', path: '/cq_overview_portability', children: [
                            { level: 4, text: 'C1.2.1 Intel', path: '/intel', status: 'empty' },
                            { level: 4, text: 'C1.2.2 AMD', path: '/amd', status: 'empty' },
                            { level: 4, text: 'C1.2.3 Arm', path: '/arm', status: 'empty' },
                        ]
                    },
                    {
                        level: 3, text: 'C1.3 Multiprocessor', path: '/cq_overview_multiprocessor', children: [
                            { level: 4, text: 'C1.3.1Best system computer technology [Gf perf/core] per app', path: '/gf_cor' },
                            { level: 4, text: 'C1.3.2 Best system efficient total MP Performance per App. & Domain [tot Gf/system]', path: '/gf_system' },
                            { level: 4, text: 'C1.3.3 Architectural performance ratios showing top performer by [Gf]', path: '/gf_arch' },

                        ]
                    },
                    {
                        level: 3, text: 'C1.4 Performance by scalability type', path: '/perf_by_scalability_type', children: [
                            { level: 4, text: 'C1.4.1.a Best arch perf/cost implicit w. various numbers of cores for optimal scalability', path: '/gf_cost' },
                            { level: 4, text: 'C1.4.1.b  Type of scaling – replication factors', path: '/type_of_scaling_replication_factors' },
                        ]
                    },
                    { level: 3, text: 'C1.5 Oneview ', path: '/oneview' },
                    { level: 3, text: 'C1.6 Best App insights per domain ', path: '/best_app_insights_per_domain' },

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
const WelcomePageTableOfContentsDrawer = () => {
    const navigate = useNavigate();
    const [selectedItem, setSelectedItem] = useState('/');
    const [expandedSections, setExpandedSections] = useState([]);
    const [navStack, setNavStack] = useState([drawerItems]);

    useEffect(() => {
        const storedSelectedItem = localStorage.getItem('selectedItem');
        if (storedSelectedItem) {
            setSelectedItem(storedSelectedItem);
        }
    }, []);


    const navigateToSection = (path, children, drillDown) => {
        navigate(path);
        setSelectedItem(path);
        localStorage.setItem('selectedItem', path);
        if (drillDown && children) {
            setNavStack(prevStack => [...prevStack, children]);
        } else {
            if (children) {
                if (!expandedSections.includes(path)) {
                    setExpandedSections(prevSections => [...prevSections, path]);
                } else {
                    setExpandedSections(prevSections => prevSections.filter(section => section !== path));
                }
            }
        }
    };

    const goBack = () => {
        setNavStack(prevStack => {
            const newStack = [...prevStack];
            newStack.pop();
            return newStack;
        });
    };




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
                    {navStack.length > 1 && <ListItemButton onClick={goBack}>Go Back</ListItemButton>}
                    <DrawerItemsList
                        items={navStack[navStack.length - 1]}
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
