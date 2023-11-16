import React from 'react';


export default function CQOverview() {
    return (
        <div className="textPageContainer">
            <h1>C1. CQ Overview[Broad QaaS Introduction]</h1>
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
            <p>

                QaaS has the ability to answer many subtle variations of simple quality questions by consulting its extensive set of measurements and analyses.
                On the topic of how to achieve “best performance,” QaaS can deal with various nuances. If one seeks the very best time for one application on one or more systems,
                a clear answer is easy. But there are indeed many nuanced options in this issue:
            </p>
            <p>
                <ul>
                    <li>Is time really the preferred or only performance metric, Gf or app FOM may give alternative answers.</li>
                    <li>If there are actually several apps in question, then is the question about which system = &lt; compiler, arch&gt;
                        combination is best for each app, or instead, which compiler/system gets the most wins (or big wins) of all compilers, across the whole app suite.
                    </li>
                    <li>If one plans to use the best compiler/system for a set of apps, is maximizing top perf the question, or really avoiding perf losses (or big losses).</li>
                    <li>In all such inquiries, wins or losses may be best stated with some fuzziness. The real question may be about “pretty good” systems i.e.
                        including near wins in the process of counting, because runners-up may be most robust systems.</li>
                </ul>

                Even for our current set of just a dozen codes, a great deal of variety arises, which makes these questions relevant. Fig. 1 otherdoc shows absolute performance,
                while Fig. 2 appgain shows winning compiler statistics. Table sept8 opens the door to considering second best but pretty good solutions; note that ICC looks weak when avoiding losses becomes a focus. Tablecompare shows an overall comparison of these questions.

                Table port? Here or port section.. also points out that beyond performance:
                <ul>
                    <li>
                        Overall-quality must consider portability and cost. For example, on ARM compilers, compilation or execution may fail on the apps we have studied
                        (a rare experience on Intel compilers),
                        which in some situations is disastrous. For Nvidia, the closed ecosystem also prevents portability to or from what are often winning performance
                        numbers on very expensive HW.
                    </li>

                </ul>
            </p>


        </div>
    );


}