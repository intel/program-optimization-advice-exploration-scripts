import React from 'react';

import MPminiappPerfVarTable from '../graph/table/MPminiappPerfVarTable';
import { Link } from 'react-router-dom';

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
                As outlined in Section B., we expose quality problems with specific compilers, architectures,
                multiprocessor performance and across a broad set of system types. We illustrate the results using
                various kinds of application SW examples: numerical libraries, HPC-type benchmarks, mini-applications,
                and whole applications. Wherever practical, we use multiple data sets to expose quality variations.
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

            <h2>Ice Lake Multicore Performance Details</h2>
            <p>
                Ever-present questions in parallel computing concern scalability: how well-matched is a code to a multicore architecture
                and what performance levels proceed from this? Fig. parvar shows these latter relevant characteristics for the 7 miniapps
                running on ICL. The compilers used are documented in Fig. bestcomp (see compiler section). Considering the number of cores
                leads to a 4th type of QaaS graphs for scalability.
            </p>
            <MPminiappPerfVarTable />

            <p>
                The scalability of codes has two points of focus: the number of processors used effectively, and scaling type in terms of code & data replication factors.
                Fig. parvar shows that excellent scalability can result from diverse SW approaches: MiniQMC and its data are replicated 32 times, while HACC executes 48 OpenMP
                threads simultaneously on one data set, and yet both achieve high Gf rates (12.8 and 16.6 Gf/core, respectively).
                Note that the best affinities for these two codes also differ substantially.
                Lower Gf results are achieved for the other 5 miniapps, using various kinds of SW scaling and HW configurations.
            </p>

            <p>
                Throughout this discussion we show results that maintain parallel efficiency above .5. This is intuitively desirable,
                but individual machine users may have more or less aggressive attitudes. Some may prefer satisfying an efficiency-knee
                criterion that considers HW cost, below which efficiency falls sharply. Others with more concern about raw speed than
                about cost will prefer to focus on a speedup knee, above which performance gains drop sharply with core increase.
                In the following we will introduce two types of scalability graphs that represent these ideas.
            </p>
            <p>
                Finally, total operating cost includes energy, and we will discuss several tradeoffs between performance and energy.
                Again, slopes and knees dominate the discussion. No one wants to minimize energy (by turning off the machine),
                but everyone has some form of constrained optimization in mind - minimal energy subject to pretty good performance
                (which includes many personal views of “good”). We will see that clock frequency, instruction set used (vector length),
                and number of cores used interact to influence several metrics that include time, rate and energy.
            </p>
            <p>
                Note to reader: this ends the current demo. We will soon add compiler details and portability detials at this level.
            </p>



        </div>
    );


}