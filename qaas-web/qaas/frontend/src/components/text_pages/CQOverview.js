import React from 'react';


export default function CQOverview() {
    return (
        <div className="textPageContainer">
            <h1>C1. CQ Overview</h1>
            <p>
                This initial QaaS implementation illustrates the recent history (&lt; 10 years) of important but limited parts of the entire Computational Quality picture.
                We believe it covers enough to show the value of the approach. In this sense, it serves as a continuously updated encyclopedia of the factors contributing
                to CQ, their relative magnitudes and their variations. It will continue to expand in response to user interest.
            </p>
            <p>
                As outlined in Section B., we expose quality problems with specific compilers , architectures , multiprocessor performance
                and across a broad set of system types . We illustrate the results using various kinds of application SW examples: numerical libraries,
                HPC-type benchmarks, mini-applications, and whole applications . Wherever practical,
                we use multiple data sets to expose quality variations.
            </p>
        </div>
    );


}