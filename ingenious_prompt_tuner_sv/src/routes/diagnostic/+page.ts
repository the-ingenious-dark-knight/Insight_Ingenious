import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch, params }) => {
    const response = await fetch('http://localhost:80/api/v1/diagnostic', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': 'Basic ' + btoa('123:123')
        },
    });
    
    if (!response.ok) {
        throw new Error('Diagnostics Request failed');
    }

    const data = await response.json();
    return { props: { data } };
};