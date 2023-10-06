import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const findMatchingItemAndParents = (items, path, parentPaths = []) => {
    for (const item of items) {
        const newParentPaths = [...parentPaths, item.path];
        if (item.path === path) return { matchingItem: item, parentPaths: newParentPaths };
        if (item.children) {
            const result = findMatchingItemAndParents(item.children, path, newParentPaths);
            if (result) return result;
        }
    }
    return null;
};

export const useNavigationState = (drawerItems, initialHash) => {
    const location = useLocation();
    const navigate = useNavigate();
    const [expandedSections, setExpandedSections] = useState([]);
    const [selectedItem, setSelectedItem] = useState(initialHash || '/');
    const [navStack, setNavStack] = useState([drawerItems]);


    useEffect(() => {
        let initialPath = localStorage.getItem('selectedItem');
        if (!initialPath) {
            initialPath = location.pathname;
        }

        const result = findMatchingItemAndParents(drawerItems, initialPath);
        if (result) {
            setSelectedItem(initialPath);
            setExpandedSections(result.parentPaths);
        }
    }, []);

    useEffect(() => {
        const currentPath = location.pathname;

        if (currentPath !== selectedItem) {
            const result = findMatchingItemAndParents(drawerItems, currentPath);
            if (result) {
                setSelectedItem(currentPath);
                localStorage.setItem('selectedItem', currentPath);
                setExpandedSections(result.parentPaths);
            }
        }
    }, [location.pathname, selectedItem]);

    const navigateToSection = (path, children, drillDown) => {
        navigate(path);
        setSelectedItem(path);
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

    return { expandedSections, selectedItem, navigateToSection, goBack, navStack };

};
