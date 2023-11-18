import React from 'react';
import IntroLink from './IntroLink';
export default function PerfImprove() {
    return (
        <div className="textPageContainer">
            <h2>How to improve performance</h2>
            <p>
                In the broadest sense, discussions of good performance must consider all of the following:
                <ul>
                    <li>
                        Which metric should be used to define performance? Time is best to compare any code across machines,
                        but to compare multiple codes we must use a rate metric. To study HPC codes, we use Gflops,
                        but the effectiveness of machine floating-point instruction sets at matching source codes must be considered.
                    </li>
                    <li>
                        The architectural features available to support good performance vary widely across machines.
                        Beyond instruction sets, this includes unicore and multicore architectures, and various bandwidths, latencies,
                        and sizes. The interactions among these HW parameters are difficult to distinguish, and often confuse people.
                    </li>
                    <li>
                        How well the source code structure matches available architectural features is a major issue.
                        Because code structure can take many forms, this includes compiler transformational strengths
                        for the wide range of syntactic forms in various languages.
                    </li>
                </ul>

            </p>

            <p>
                To approach this complex set of issues, we proceed by illustrating the subject with a few example codes and machine
                types. Then we discuss performance issues in a top-down manner. As you navigate this website,
                it is important to acknowledge that all such discussionc come down to two related issues:
                <ul>
                    <li>
                        Understanding a computation’s performance and
                    </li>
                    <li>
                        Improving a computation’s performance
                    </li>

                </ul>


            </p>

            <p>
                Our primary goal is the latter, and hardware choices like frequency, vector instruction set, prefetch options, or number of cores used may affect performance for better or worse.
                Similarly, software choices like language, compiler, compiler flags, and runtime libraries used are also consequential. These options and their combinations can vary performance,
                but don’t really help a developer to understand why performance changes.
            </p>

            <p>
                They are (mostly) independent variables, but the dependent variables that actually explain why performance changes often remain hidden. Some SW tools purport to explain more performance,
                but usually only offer views that may or may not matter. For example, if a function has a high time profile, it is not bad if the function runs at high Gf.
                Neither are relatively high cache misses if they are hidden behind lots of ALU processing. Understanding why the machine stalls is the key to lost time, and is the bottom line we seek.

            </p>
            <p>
                Our tools are set up to analyze the code, make multiple runs using heuristics, find the best options, and then list the options and the gains they provide. Deeper explanations are offered as well,
                but are not central to the purpose of QaaS.
            </p>

        </div>
    );


}