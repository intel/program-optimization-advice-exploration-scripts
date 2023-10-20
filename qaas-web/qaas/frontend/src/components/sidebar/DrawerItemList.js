// DrawerItemsList.js
import React from 'react';
import DrawerItem from './DrawerItem';
//start from level 0
const DrawerItemsList = ({ items, navigateToSection, selectedItem, expandedSections, level = 0, parent }) => {
    return items && items.map((item) => {
        const hasChildren = item.children && item.children.length > 0;

        return (
            <React.Fragment key={item.path}>
                <DrawerItem
                    level={level}  // Pass the current level
                    text={item.text}
                    path={item.path}
                    children={item.children}
                    parent={parent}
                    status={item.status}
                    drillDown={item.drillDown}
                    navigateToSection={navigateToSection}
                    selectedItem={selectedItem}
                    hasChildren={hasChildren}
                    expandedSections={expandedSections}
                />

                {expandedSections.includes(item.path) && hasChildren && (
                    <DrawerItemsList
                        items={item.children}
                        navigateToSection={navigateToSection}
                        selectedItem={selectedItem}
                        expandedSections={expandedSections}
                        parent={item}
                        level={level + 1}  // Increment level by 1 for child items
                    />
                )}
            </React.Fragment>
        );
    });
};

export default DrawerItemsList;

