import React from 'react';
import LinkBox from './LinkBox';
const App = () => {
    const myhost = window.location.hostname
    const ov = `https://${myhost}/oneview_page`;
    const qaas = `https://${myhost}/qaas_page`;
    const lore = `https://${myhost}/lore_page`;

    return (
        <div>
            <h1>Choose a repository:</h1>
            <div>
                <LinkBox href={ov}>
                    Oneview repository (requires login)
                </LinkBox>
                <LinkBox href={qaas}>
                    QaaS repository (requires login)
                </LinkBox>
                <LinkBox href={lore}>
                    Lore repository (requires login)
                </LinkBox>
            </div>
        </div>
    );
};

export default App;
