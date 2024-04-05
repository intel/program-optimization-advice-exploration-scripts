import React from 'react';
import * as ReactDOM from 'react-dom';

import ReactDOMServer from 'react-dom/server';
import { Parser } from 'htmlparser2';
import QualityDefinitions from '../text_pages/QualityDefinitions';
import { StaticRouter } from 'react-router-dom/server';


export const extractContentFromComponentList = (componentList) => {
    return componentList.map(({ path, component: Component }) => {
        // Render the component to a string
        // console.log(path)
        let componentHtml = ReactDOMServer.renderToString(
            <StaticRouter location={path}>
                <Component />
            </StaticRouter>
        );
        let extractedContent = '';

        let isRelevantTag = false;

        const parser = new Parser({
            onopentag(name) {
                if (name === 'h1' || name === 'h2' || name === 'p' || name === 'ul') {
                    isRelevantTag = true;
                }
            },
            ontext(text) {
                if (isRelevantTag) {
                    extractedContent += text + ' ';
                }
            },
            onclosetag(name) {
                if (name === 'h1' || name === 'h2' || name === 'p' || name === 'ul') {
                    isRelevantTag = false;
                }
            }
        }, { decodeEntities: true });

        parser.write(componentHtml);
        parser.end();

        return { path, content: extractedContent.trim() };
    });
};




