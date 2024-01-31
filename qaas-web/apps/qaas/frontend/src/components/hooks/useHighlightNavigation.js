import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

export const useHighlightNavigation = () => {
    const location = useLocation();

    useEffect(() => {
        const hash = location.hash.replace('#', '');
        if (hash) {
            const element = document.getElementById(hash);
            if (element) {
                element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                element.classList.add('highlight');
                //  remove the highlight after 5 seconds
                const timeoutId = setTimeout(() => {
                    element.classList.remove('highlight');
                }, 5000); // 5000 milliseconds = 5 seconds
            }




        }
    }, [location.hash]); // re-run the effect when the hash changes
};
