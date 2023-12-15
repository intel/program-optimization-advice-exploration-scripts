import React from 'react';
import LinkBox from './LinkBox';
const App = () => {
    const myhost = window.location.hostname
    const myprotocol = window.location.protocol

    const ov = `${myprotocol}//${myhost}/oneview_page`;
    const qaas = `${myprotocol}//${myhost}/qaas_page`;
    const lore = `${myprotocol}//${myhost}/lore_page`;

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
