import React from 'react';
import port1Image from '../imgs/port1.png';

import port2Image from '../imgs/port2.png';

export default function Portability() {
    return (
        <div className="textPageContainer">
            <h1>C1.2 Portability across systems</h1>
            <p>
                The performance results (sect x for ARM) show some NA cases, for which apps failed to run on particular systems.
                Here we view the data totally from the reliability point of view – which codes run and which do not. Mention Portability and availability
            </p>
            <div className='imageContainer'>
                <img src={port1Image} alt="port1 Description" />
            </div>
            <p>
                Table port1 shows that similarly to performance, from a portability/reliability point of view, ICC is a better choice than ICX. However,
                GCC also has no porting problems for these cases. We could count failures for important cases, etc. Here ICX is being punished for one case .

            </p>
            <p>This can end up ambiguously -  Uni vs MP cases</p>
            <div className='imageContainer'>
                <img src={port2Image} alt="port2 Description" />
            </div>
            <p>
                Table port2 shows that for ARM, both GCC and the LLVM compilers have problems, but GCC is a better choice.
            </p>
            <p>Click for system calculator static table lookup, dyn – anything we have available. -&gt; active developer.</p>

            <p>Static we have menu, but they may pck a combo that we haven’t run – tell user. </p>
        </div>
    );


}