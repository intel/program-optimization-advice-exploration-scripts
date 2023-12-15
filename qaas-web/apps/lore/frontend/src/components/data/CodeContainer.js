import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

export default function CodeContainer({ code }) {
    return (
        <SyntaxHighlighter language="c" className="code-text">
            {code}
        </SyntaxHighlighter>
    );
}