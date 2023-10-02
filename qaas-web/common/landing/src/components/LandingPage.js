import React from 'react';
import LinkBox from './LinkBox';
const App = () => {
    return (
        <div>
            <h1>Choose a repository:</h1>
            <div>
                <LinkBox href="https://oneview-intel.liparad.uvsq.fr">
                    Oneview repository (requires login)
                </LinkBox>
                <LinkBox href="https://qaas-intel.liparad.uvsq.fr">
                    QaaS repository (requires login)
                </LinkBox>
            </div>
        </div>
    );
};

export default App;
