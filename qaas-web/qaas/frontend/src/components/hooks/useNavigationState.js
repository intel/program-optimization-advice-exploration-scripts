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
    //keep stack of selected item so when go back to multiple levels items will still be selected not overriden
    const [selectedItemsStack, setSelectedItemsStack] = useState([initialHash || '/']);
    const [navStack, setNavStack] = useState([drawerItems]);
    const [isGoingBack, setIsGoingBack] = useState(false);
    //get current level
    useEffect(() => {
        const savedNavStack = localStorage.getItem('navStack');
        if (savedNavStack) {
            setNavStack(JSON.parse(savedNavStack));
        }
    }, []);

    useEffect(() => {
        let initialPath = localStorage.getItem('selectedItem');
        if (!initialPath) {
            initialPath = location.pathname;
        }

        const result = findMatchingItemAndParents(drawerItems, initialPath);
        if (result) {
            setSelectedItemsStack([initialPath]);
            setExpandedSections(result.parentPaths);
        }
    }, []);

    useEffect(() => {
        const currentPath = location.pathname;
        const currentSelectedItem = selectedItemsStack[selectedItemsStack.length - 1];


        if (!isGoingBack && currentPath !== currentSelectedItem) {
            const result = findMatchingItemAndParents(drawerItems, currentPath);
            if (result) {
                setSelectedItemsStack(prevStack => [...prevStack, currentPath]);  // Push the current path to the stack
                localStorage.setItem('selectedItem', currentPath);
                setExpandedSections(result.parentPaths);
            }
        }
        setIsGoingBack(false);


    }, [location.pathname, selectedItemsStack, isGoingBack]);



    const navigateToSection = (path, text, parent, children, drillDown) => {
        navigate(path);
        // clear expandedSections if we are drilling down
        if (drillDown && children) {
            //also put parent into the new level
            const selfCopy = { text: text, path: path, children: [] }; // copy of the item itself to the chilren's stack
            const newStack = [selfCopy, ...children];
            setNavStack(prevStack => {
                const nextStack = [...prevStack, newStack];
                localStorage.setItem('navStack', JSON.stringify(nextStack));
                return nextStack;
            });
            setSelectedItemsStack(prevStack => [...prevStack, path]);


        } else {
            if (children) {
                setExpandedSections(prevSections => {
                    if (prevSections.includes(path)) {
                        // if already expanded, collapse it
                        return prevSections.filter(section => section !== path);
                    } else {
                        // if not expanded, add it to the expanded sections
                        return [...prevSections, path];
                    }
                });
            }
        }
    };


    const goBack = () => {
        let newNavStack, newSelectedItemsStack;

        setNavStack(prevStack => {
            newNavStack = [...prevStack];
            newNavStack.pop();
            localStorage.setItem('navStack', JSON.stringify(newNavStack));
            return newNavStack;
        });

        setExpandedSections(prevSections => {
            const newSections = [...prevSections];
            newSections.pop();
            return newSections;
        });

        console.log("Before going back, selectedItemsStack: ", selectedItemsStack);

        setSelectedItemsStack(prevStack => {
            const newStack = [...prevStack];
            newStack.pop();
            const newSelected = newStack[newStack.length - 1];
            navigate(newSelected);
            console.log("After going back, selectedItemsStack should be: ", newStack);
            return newStack;
        });
        setIsGoingBack(true);


    };





    const currentSelectedItem = selectedItemsStack[selectedItemsStack.length - 1];
    return { expandedSections, selectedItem: currentSelectedItem, navigateToSection, goBack, navStack };

};
