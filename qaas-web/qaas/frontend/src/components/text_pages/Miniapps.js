import React from 'react';
import minitopImage from '../imgs/minitop.png';

import bestcompImage from '../imgs/bestcomp.png';
import CompilerComparisonHistogram from '../graph/CompilerComparisonHistogram';

export default function Miniapps() {
    return (
        <div className="textPageContainer">
            <h1>C1.1.1 Miniapps</h1>
            <p>
                The overall results for 7 miniapps on Intel Ice Lake are discussed here. First the best compiler,
                then the benefits of QaaS are explained. The best compiler per miniapp is simply the compiler for which QaaS found
                a flag setting that beat all others; 48 cases were tested here – 3 compilers with 16 flag settings each: Fig. bestcomp.
            </p>
            <div className='imageContainer'>
                <img src={bestcompImage} alt="BestComp Description" />
            </div>
            <p>
                The benefit of QaaS over app developers is discussed next. Fig. minitop compares compilers from the viewpoint of winning
                most in improving on well-chosen default flags for each compiler, that ICX is best. But from the viewpoint of losing least,
                ICC is best. Because we only have 7 miniapps, the table can be regarded as preliminary with only small variations among all 3 compilers.
                Overall results for numerical libraries are shown in Table libtop. Many people only care about a particular app domain or a few apps,
                which can be done by clicking here (menu of miniapps). For more details about the miniapps click here [More miniapp perf details].
                This is all of the stuff weve seen in past month.
                Note that we regard gains &lt; 10% as insignificant as they may include measurement errors and
                are generally not too important from an app developers’ point of view.

            </p>
            <div className='imageContainer'>
                <img src={minitopImage} alt="Minitop Description" />
            </div>
            <h2> Best compiler Time, Gf</h2>

            <h2 >Compiler comparisons</h2>
            <h2 style={{ marginLeft: '25px' }}>Compiler choice</h2>
            <CompilerComparisonHistogram />

            <h2 style={{ marginLeft: '25px' }}>Flag choice/compiler</h2>




        </div>
    );


}