import React from 'react';

import arcompImage from '../imgs/arcomp.png';

export default function GfArch() {
    return (
        <div className="textPageContainer">
            <h1>C1.3.3 Architectural performance ratios showing top performer by [Gf]</h1>
            <p>
                We can effectively display ratios of architectures as bins for any comparable set,
                i.e. whose performances win/lose in some cases. ICL (now), SKL (uvsq) , as well as SPR (HM).
                For that we use as a label, /ratio in this graph instead of /#cores Fig. totGf or /arch Fig Gf/cor
            </p>
            <p>
                These would be equivalent to the 3-way compiler comparison graphs (fig histw), with histogram bins of perf ratios among HW archs instead of compilers.
            </p>
            <p>
                Best MP perf ratios among architectures -&gt; implicit cost ratios user provides
            </p>
            <p>
                Entries show app name and focus is on MP perf ratio = T other mach / T best mach = example:
                AMG(SPR/ICL) in Bin: Time ratio r= 1.1. Then all SPR / ICL wins are colored the same. Similarly
                for other arch ratios and colors. (just like Jan graph).

            </p>
            <div className='imageContainer'>
                <img src={arcompImage} alt="arcomp Description" />
            </div>
            <p>
                User can interpret arch ratios as a cost ratio tradeoff. If perf ratio is 3x, don’t pay more than 3x$ for fastest machine.

            </p>
            <p>
                Non histogram plots [y axis Gf or FOM, x-axis MP params.].  We have ICL data and will build graphs next
            </p>


        </div>
    );


}