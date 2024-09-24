import React, { useState } from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';
import { Card, Button } from 'nhsuk-react-components';
import { Chart } from 'react-google-charts';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

type Props = {};

// Generate 3-hour intervals (00:00, 03:00, ..., 21:00)
const hours = ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00'];

function generateDaytimeBiasedData(
    minDay: number,
    maxDay: number,
    minNight: number,
    maxNight: number,
) {
    return hours.map((hour) => {
        const hourInt = parseInt(hour.split(':')[0]);
        if (hourInt >= 6 && hourInt <= 21) {
            return Math.floor(Math.random() * (maxDay - minDay) + minDay);
        } else {
            return Math.floor(Math.random() * (maxNight - minNight) + minNight);
        }
    });
}

function SpikeGraphPage({}: Props) {
    const [showTable, setShowTable] = useState(false); // Toggle between table and chart view

    // Bar chart data for ChartJS
    const barData = {
        labels: hours,
        datasets: [
            {
                label: 'Successes',
                data: generateDaytimeBiasedData(50, 150, 0, 20),
                backgroundColor: 'rgba(0, 114, 206, 0.5)',
                borderColor: 'rgba(0, 114, 206, 0.8)',
                borderWidth: 1,
            },
            {
                label: 'Failures',
                data: generateDaytimeBiasedData(10, 50, 0, 10),
                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                borderColor: 'rgba(255, 99, 132, 0.8)',
                borderWidth: 1,
            },
        ],
    };

    const barConfig = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top' as const,
            },
            title: {
                display: false,
            },
        },
        scales: {
            x: { stacked: true },
            y: { stacked: true, beginAtZero: true },
        },
    };

    // Google Charts data
    const googleData = [
        ['Hour', 'Successes', 'Failures'],
        ...hours.map((hour) => [
            hour,
            Math.floor(Math.random() * (150 - 50) + 50),
            Math.floor(Math.random() * (50 - 10) + 10),
        ]),
    ];

    const googleOptions = {
        chart: {
            title: 'GP2GP Attachment Rates',
            subtitle: 'Successes vs Failures',
        },
        height: 500,
        chartArea: { width: '90%', height: '80%' },
        bars: 'horizontal',
        colors: ['#0072CE', '#FF6384'],
        isStacked: true,
        legend: { position: 'top' },
    };

    // Toggle between the chart and table
    const handleToggleView = () => setShowTable(!showTable);

    // Render a table as fallback when JavaScript is not enabled or when the user switches to table view
    const renderTable = (data: (string | number)[][], heading: string) => (
        <>
            <h3>{heading}</h3>
            <table className="nhsuk-table">
                <thead>
                    <tr>
                        <th>Hour</th>
                        <th>Successes</th>
                        <th>Failures</th>
                    </tr>
                </thead>
                <tbody>
                    {data.slice(1).map(([hour, successes, failures], index) => (
                        <tr key={index}>
                            <td>{hour}</td>
                            <td>{successes}</td>
                            <td>{failures}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </>
    );

    return (
        <>
            {/* Graceful fallback when JavaScript is disabled */}
            <noscript>
                <Card feature>
                    <Card.Content>
                        <Card.Heading>GP2GP Attachment Rates (No JavaScript)</Card.Heading>
                        <Card.Description>
                            {renderTable(googleData, 'GP2GP Attachment Rates Table')}
                        </Card.Description>
                    </Card.Content>
                </Card>
            </noscript>

            {/* Toggle button to switch between chart and table */}
            <Button onClick={handleToggleView}>{showTable ? 'Show Graphs' : 'Show Tables'}</Button>

            {!showTable ? (
                <>
                    {/* ChartJS Bar Chart */}
                    <Card feature>
                        <Card.Content>
                            <Card.Heading>GP2GP Attachment Rates (Chart.js)</Card.Heading>
                            <Card.Description>
                                <Bar data={barData} options={barConfig} />
                            </Card.Description>
                        </Card.Content>
                    </Card>

                    {/* Google Charts */}
                    <Card feature>
                        <Card.Content>
                            <Card.Heading>GP2GP Attachment Rates (Google Charts)</Card.Heading>
                            <Card.Description
                                style={{
                                    display: 'flex',
                                    flexFlow: 'row nowrap',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}
                            >
                                <Chart
                                    chartType="ColumnChart"
                                    width="100%"
                                    height="100%"
                                    data={googleData}
                                    options={googleOptions}
                                />
                            </Card.Description>
                        </Card.Content>
                    </Card>
                </>
            ) : (
                <>
                    {/* Table for Chart.js Data */}
                    <Card feature>
                        <Card.Content>
                            <Card.Heading>GP2GP Attachment Rates (Chart.js Data)</Card.Heading>
                            <Card.Description>
                                {renderTable(
                                    [
                                        ['Hour', 'Successes', 'Failures'],
                                        ...hours.map((hour, i) => [
                                            hour,
                                            barData.datasets[0].data[i],
                                            barData.datasets[1].data[i],
                                        ]),
                                    ],
                                    'Chart.js Data Table',
                                )}
                            </Card.Description>
                        </Card.Content>
                    </Card>

                    {/* Table for Google Charts Data */}
                    <Card feature>
                        <Card.Content>
                            <Card.Heading>GP2GP Attachment Rates (Google Charts Data)</Card.Heading>
                            <Card.Description>
                                {renderTable(googleData, 'Google Charts Data Table')}
                            </Card.Description>
                        </Card.Content>
                    </Card>
                </>
            )}
        </>
    );
}

export default SpikeGraphPage;
