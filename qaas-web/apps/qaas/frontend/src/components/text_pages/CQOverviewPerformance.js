import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import minitopImage from '../imgs/minitop.png';
export default function CQOverviewPerformance() {
    return (
        <div className="textPageContainer">
            <h1>C1.1 Performance vs. compilers</h1>
            <p>

                Most application developers have a favorite (or mandated) compiler and possibly a favored set of compilation flags.
                If available, QaaS uses a developer-chosen compiler/flag set; otherwise it uses an expert-chosen default compiler and settings
                for each system. In either case, the question is: How much can QaaS improve performance time by searching across many compiler
                flags and other compilers? We compare ICX, ICC and GCC for performance and portability.
            </p>

            <p>
                In the following sections, QaaS results are shown for a collection of miniapps,
                whole applications, and library functions. Generally, the miniapps are web-available simplifications of real apps,
                intended to allow performance tuning on short-running approximations of the full app. In some cases, the miniapps
                are rather well tuned to start, in other cases less so.
            </p>

        </div>
    );


}