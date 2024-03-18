import React from 'react';
import { Link } from 'react-router-dom';

export const contentList = [
    {
        text: 'Overview of QaaS: Summaries of past runs', path: '/overview', children: [
            { text: 'How to improve performance', path: '/qaas/overview/how_to_improve_performance' },
            {
                text: 'Unicore performance comparisons', path: '/qaas/overview/unicore_performance_comparisons', children: [
                    { text: 'Fig.uni', path: '/qaas/overview/unicore_performance_comparisons#figuni' },
                    { text: 'Fig.utab', path: '/qaas/overview/unicore_performance_comparisons#figutab' },

                ]
            },

            {
                text: 'Compiler Comparison', path: '/qaas/overview/compiler_comparison', children: [
                    { text: 'Fig. appgain', path: '/qaas/overview/compiler_comparison#figappgain' },
                    { text: 'Fig.Bestcomp', path: '/qaas/overview/compiler_comparison#figbestcomp' },
                    { text: 'AMG/HACC click target', path: '/qaas/overview/AMG_HACC_click_target' },
                    { text: 'Developer flag recommendations', path: '/qaas/overview/developer_flag_recommendations' },
                ]
            },
            {
                text: 'Multicore performance comparisons', path: '/qaas/overview/multicore_performance_comparisons', children: [

                    { text: 'Fig.Arccomp', path: '/qaas/overview/multicore_performance_comparisons#figarccomp' },
                    { text: 'Fig.MPperf', path: '/qaas/overview/multicore_performance_comparisons#figmpperf' },
                    { text: 'Fig.MPratio', path: '/qaas/overview/multicore_performance_comparisons#figmpratio' },

                ]
            },
            { text: 'Application Portability', path: '/qaas/overview/application_portability' },




        ]
    },
    {
        text: 'CQ Overview[Broad QaaS Introduction]', path: '/qaas/cq_overview', children: [
            { text: 'Constraints and Scope', path: '/qaas/overview/constraints_and_scope' },

        ]
    },


]



const ToCItem = ({ item }) => (
    <li>
        <Link className='link' to={item.path}>{item.text}</Link>
        {/*  if the item has children */}
        {item.children && <ToCSubList items={item.children} />}
    </li>
);

const ToCSubList = ({ items }) => (
    <ul>
        {items.map((subItem, index) => (
            <ToCItem key={index} item={subItem} />
        ))}
    </ul>
);

const TableOfContents = () => {
    return (
        <div className='ToCContainer'>
            <h2>Table of Contents</h2>
            {contentList.map((item, index) => (
                <ToCItem key={index} item={item} />
            ))}


        </div>
    );
};

export default TableOfContents;
