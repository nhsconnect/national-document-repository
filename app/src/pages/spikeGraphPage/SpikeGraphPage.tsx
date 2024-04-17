import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    PointElement,
    LineElement,
} from 'chart.js';
import { Bar, Line } from 'react-chartjs-2';
import moment from 'moment';
import { Card } from 'nhsuk-react-components';
import { faker } from '@faker-js/faker';
ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    PointElement,
    LineElement,
);
type Props = {};

function SpikeGraphPage({}: Props) {
    const labels = moment.monthsShort();
    const barData = {
        labels: labels,
        datasets: [
            {
                label: 'LG',
                data: labels.map(() => faker.number.int({ min: 20, max: 100 })),
                backgroundColor: 'rgba(0, 114, 206, 0.5)',
                borderColor: 'rgba(0, 114, 206, 0.8)',
                borderWidth: 1,
            },
            {
                label: 'ARF',
                data: labels.map(() => faker.number.int({ min: 20, max: 100 })),
                backgroundColor: 'rgba(118, 134, 146, 0.5)',
                borderColor: 'rgba(118, 134, 146, 0.8)',
                borderWidth: 1,
            },
        ],
    };
    const lineData = {
        labels,
        datasets: [
            {
                label: 'Searches',
                data: labels.map(() => faker.number.int({ min: 5000, max: 20000 })),
                backgroundColor: 'rgba(0, 114, 206, 0.5)',
                borderColor: 'rgba(0, 114, 206, 0.8)',
            },
        ],
    };
    const config = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: false,
            },
        },
    };
    return (
        <>
            <Card feature>
                <Card.Content>
                    <Card.Heading>Record volume</Card.Heading>
                    <Card.Description>
                        <Bar data={barData} options={config} />;
                    </Card.Description>
                </Card.Content>
            </Card>
            <Card feature>
                <Card.Content>
                    <Card.Heading>Patient search volume</Card.Heading>
                    <Card.Description>
                        <Line data={lineData} options={config} />;
                    </Card.Description>
                </Card.Content>
            </Card>
        </>
    );
}

export default SpikeGraphPage;
