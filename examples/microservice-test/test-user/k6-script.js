import http from 'k6/http';
import { check } from 'k6';

const BASE_URLS = [ // current & forecast -> on port 8001 & 8002
    { url: 'http://192.168.1.1:8080', endpoints: ['/api/v1/current', '/api/v1/current/airqual'] }, 
    { url: 'http://192.168.1.1:8080', endpoints: ['/api/v1/forecast/', '/api/v1/forecast/detailed', '/api/v1/forecast/three-day', '/api/v1/forecast/hourly'] }
];

export default function () {
    const LOCATIONS = ['London', 'France', 'New York', 'Tokyo', 'Ottawa']; // test location query

    BASE_URLS.forEach(({ url, endpoints }) => {
        endpoints.forEach(endpoint => {
            LOCATIONS.forEach(location => {
                const fullUrl = `${url}${endpoint}?location=${encodeURIComponent(location)}`;
                const response = http.get(fullUrl);

                check(response, {
                    'status is 200': (r) => r.status === 200,
                });
            });
        });
    });
}
