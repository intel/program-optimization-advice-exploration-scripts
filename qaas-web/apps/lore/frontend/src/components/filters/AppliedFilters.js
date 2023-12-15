import React from 'react';

// const AppliedFilters = ({ appliedFilters = [], onRemoveFilter }) => (
//     <div>
//         <h3>Applied Filters</h3>
//         <ul>
//             {[...appliedFilters].map((filter, index) => (
//                 <li key={index}>
//                     {filter.type}: {filter.value}
//                     <button onClick={() => onRemoveFilter(index)}>Remove</button>
//                 </li>
//             ))}
//         </ul>
//     </div>
// );

// export default AppliedFilters;

const AppliedFilters = ({ appliedFilters = [], onRemoveFilter }) => (
    <div>
        <h3>Applied Filters</h3>
        <ul>
            {[...appliedFilters].map((filter, index) => (
                <li key={index}>
                    {filter.type}: {filter.operator} {filter.value}
                    <button onClick={() => onRemoveFilter(index)}>Remove</button>
                </li>
            ))}
        </ul>
    </div>
);

export default AppliedFilters;
