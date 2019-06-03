// import Chart from 'chart.js';
import moment from 'moment';

import {
    setupMainChart,
    setupOccurenceQueueChart,
    setupNotificationQueueChart,
    Chart
} from './tsdb';

// window.Chart = Chart;
window.moment = moment;
export {
    setupMainChart,
    setupNotificationQueueChart,
    setupOccurenceQueueChart
};
