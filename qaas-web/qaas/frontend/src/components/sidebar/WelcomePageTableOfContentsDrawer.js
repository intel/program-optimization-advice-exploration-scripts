import React, { useState, useEffect } from 'react';
import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import { useNavigate, useLocation } from 'react-router-dom';
import DrawerItemsList from './DrawerItemList';
import ListItemButton from '@mui/material/ListItemButton';
import { useNavigationState } from '../hooks/useNavigationState';
const drawerItems = [
    { text: 'Overview', path: '/qaas' },
    {
        text: 'A. Quality definitions', path: '/qaas/quality_definitions', children: [
            { text: 'A.1 Detailed Definitions', path: '/qaas/quality_detailed_definitions', status: 'empty' },
        ]
    },
    { text: 'B. Constraints and Scope', path: '/qaas/constraints_and_scope' },
    {
        text: 'C. Initial QaaS offerings', path: '/qaas/initial_qaas_offerings', children: [
            { text: 'C0 Overview', path: '/qaas/overview' },

            {

                text: 'C1. CQ Overview', path: '/qaas/cq_overview', children: [
                    {
                        text: 'C1.1 Performance vs. compilers', path: '/qaas/cq_overview_performance', children: [
                            {
                                text: 'C1.1.1 Miniapps', path: '/qaas/miniapps', children: [
                                    {
                                        text: 'C1.1.1.A Compiler Details', path: '/qaas/compiler_details', children: [
                                            { text: 'L2.1: Multi-Compiler Gains', path: '/qaas/multi_compiler_gains' },
                                            {
                                                text: 'L2.2: QaaS Searches L2', path: '/qaas/qaas_searches_l2', children: [
                                                    { text: 'L3.1: QaaS Searches', path: '/qaas/qaas_searches', },
                                                ]
                                            },
                                            // { text: 'C1.1.2 Applications', path: '/apps' },
                                            // { text: 'C1.1.3 Libraries', path: '/libraries' },
                                        ]

                                    },

                                ]
                            },
                            { text: 'C1.1.2 Applications', path: '/qaas/apps' },
                            { text: 'C1.1.3 Libraries', path: '/qaas/libraries' },
                        ]
                    },
                    {
                        text: 'C1.2 Portability across systems', path: '/qaas/cq_overview_portability', children: [
                            { text: 'C1.2.1 Intel', path: '/qaas/intel', status: 'empty' },
                            { text: 'C1.2.2 AMD', path: '/qaas/amd', status: 'empty' },
                            { text: 'C1.2.3 Arm', path: '/qaas/arm', status: 'empty' },
                        ]
                    },
                    {
                        text: 'C1.3 Multiprocessing', path: '/qaas/cq_overview_multiprocessor', children: [
                            { text: 'C1.3.1Best system computer technology [Gf perf/core] per app', path: '/qaas/gf_cor' },
                            { text: 'C1.3.2 Best system efficient total MP Performance per App. & Domain [tot Gf/system]', path: '/qaas/gf_system' },
                            { text: 'C1.3.3 Architectural performance ratios showing top performer by [Gf]', path: '/qaas/gf_arch' },

                        ]
                    },
                    {
                        text: 'C1.4 Performance by scalability type', path: '/qaas/perf_by_scalability_type', children: [
                            { text: 'C1.4.1.a Best arch perf/cost implicit w. various numbers of cores for optimal scalability', path: '/qaas/gf_cost' },
                            { text: 'C1.4.1.b  Type of scaling – replication factors', path: '/qaas/type_of_scaling_replication_factors' },
                        ]
                    },
                    { text: 'C1.5 Oneview ', path: '/qaas/oneview' },
                    { text: 'C1.6 Best App insights per domain ', path: '/qaas/best_app_insights_per_domain' },

                ]
            },
            { text: 'C2. Automatic application analysis', path: '/qaas/automatic_application_analysis' },
            { text: 'C3. Manual Interactive Mode', path: '/qaas/manual_interactive_mode' },
            {
                text: 'C4. Quality 10-year trend realities', path: '/qaas/quality_10_year_trend_realities', children: [
                    { text: 'C4.1 Conclusions', path: '/qaas/quality_10_year_trend_conclusions' },
                ]
            },
        ]
    },
];


const WelcomePageTableOfContentsDrawer = () => {

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
                    {navStack.length > 1 && <ListItemButton onClick={goBack}>Go Back</ListItemButton>}
                    <DrawerItemsList
                        items={navStack[navStack.length - 1]}
                        navigateToSection={navigateToSection}
                        selectedItem={selectedItem}
                        expandedSections={expandedSections}
                        parent={selectedItem}
                        level={navStack.length === 1 ? 0 : 1}

                    />
                </List>


            </Drawer>
        </div>
    );
};

export default WelcomePageTableOfContentsDrawer;
