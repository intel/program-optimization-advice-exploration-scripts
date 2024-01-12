import React from 'react';
import { Link } from 'react-router-dom';

export const contentList = [
    {
        text: 'Overview of QaaS: Summaries of past runs', path: '/qaas/overview', children: [
            { text: 'How to improve performance', path: '/qaas/overview/perf_improve' },
            { text: 'Unicore performance comparisons', path: '/qaas/overview/unicore_perf_contents' },
            {
                text: 'Compiler Comparison', path: '/qaas/overview/multiprocessor_comp_contents', children: [
                    { text: 'AMG/HACC click target', path: '/qaas/overview/AMG_HACC_click_target' },
                    { text: 'Developer flag recommendations', path: '/qaas/overview/flag_rec_miniapps' },
                ]
            }


        ]
    },
    {
        text: 'CQ Overview[Broad QaaS Introduction]', path: '/qaas/cq_overview'
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
