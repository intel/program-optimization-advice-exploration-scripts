import React from 'react';

export default function GfCost() {
    return (
        <div className="textPageContainer">
            <h1>C1.4.1.a Best arch perf/cost implicit w. various numbers of cores for optimal scalability</h1>
            <p>
                This is similar to the classical scalability graph/ code, showing which apps scale best and by changing eff. param we can do sensitivity studies.
                We can put best point per code (one point per code) and construct a curve using many codes.
            </p>
            <p>
                Total MP Gf vs. # procs For example, to study an ensemble of codes to be run together, how big a system would be the right choice to effectively
                cover the set of codes. In such cases, the x axis could be varying machine sizes (# procs) s.t. eff parameter with labels of apps. z
                The y axis would be Gf. The slope and knees would be of interest.
                For a large ensemble of apps, we need some graphical selection methods – start with 11 codes, think through possibilities for variations as above.
            </p>

        </div>
    );


}