// DrawerItemsList.js
import React from 'react';
import DrawerItem from './DrawerItem';
const DrawerItemsList = ({ items, navigateToSection, selectedItem, expandedSections }) => {
    return items.map((item) => {
        const hasChildren = item.children && item.children.length > 0;
        return (
            <React.Fragment key={item.path}>
                <DrawerItem
                    level={item.level}
                    text={item.text}
                    path={item.path}
                    children={item.children}
                    navigateToSection={navigateToSection}
                    selectedItem={selectedItem}
                    hasChildren={hasChildren}
                />
                {expandedSections.includes(item.path) && hasChildren && (
                    <DrawerItemsList
                        items={item.children}
                        navigateToSection={navigateToSection}
                        selectedItem={selectedItem}
                        expandedSections={expandedSections}
                    />
                )}
            </React.Fragment>
        );
    });
};

export default DrawerItemsList;
