import React from 'react';


export default function QualityDefinitions() {
    return (
        <div className="textPageContainer">
            <h1>Quality Definitions</h1>
            <p>We define quality to include performance, portability, reliability, cost of operation, and related topics.
                Each of these has important aspects clarified and quantified by QaaS:</p>
            <ol>
                <li>Performance is shown in various units, including time, Gflops, domain- or app-specific figures of merit (FoMs), etc.
                    QaaS is also sensitive to measuring the confidence one can have in performance (and other) metrics, an aspect of Reliability.</li>
                <li>Portability refers to the ability to run an app across various systems. Missing technology dependencies can prevent porting a code,
                    and even worse prevent performance portability e.g. a compiler that doesn’t work on some machine. We regard this as another aspect of Reliability.</li>
                <li>Operating costs for HPC can be substantial, so choosing the right number of processors, and using low power cores can be important,
                    as is running in minimal time. So high performance at low power defines a challenging balance-optimization.</li>
            </ol>
        </div>
    );


}