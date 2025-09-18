//This component establishes a chart to display the number of scan items which returned as passed, requiring attention, or failed
//Last updated 14 September 2025
//Recomended next changes:
//  -add a switch case for more chart types besides just pie and doughnot. Some of the chart types have slightly different syntax to each other so a little more work is needed on this. 
// - the legend is functional but the text doesn't look amazing. Played around with font settings and layout but can't get it to look quite right. Worth reviewing!

//Note: no css for this component as this is purely javascript (no JSX) and the libary in use (charts.js) has its own parameters for styling  

//To render this component:
//import ComplianceChart from './components/ComplianceChart';
//<ComplianceChart chartType={selectedChartType} dataInput = {[array of three numbers]}></ComplianceChart>
//'doughnut' and 'pie' are current options for selectedChartType

import React, { useRef, useEffect } from 'react';
import '@fontsource/league-spartan';

// Imports only the minimum required components below
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  Title,
  DoughnutController,
} from 'chart.js';


ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  DoughnutController,
  Title
);

//Accepts chartType and dataInput as parameters. ChartType currently supports doughnut and pie chart, more to be added later.
//dataInput should be an array of 3 numbers, being, in order, number of High Priority Items, Medium Priority Items, and Passed Items.
//This should be made more robust in future. For now, since the graph is only used for one very consistent thing, this is functional. 
//Fallback to 1,1,1 as array if error in data.
const ComplianceChart = ({ chartType = 'doughnut', dataInput = [1, 1, 1] }) => {
  const chartRef = useRef(null);
  const chartInstanceRef = useRef(null);

  useEffect(() => {
    const ctx = chartRef.current.getContext('2d');
   
    if (chartInstanceRef.current) {
      chartInstanceRef.current.destroy();
    }

    // Dummy data, to be replaced with data ingest function. Style can remain. 
    const data = {
      labels: ['High Priority Issues', 'Medium Priority Issues', 'Pass'],
      datasets: [{
        data: dataInput,
        backgroundColor: [
          '#ef4444',
          '#f97316',
          '#10b981',
        ],
        borderColor: [
          '#ef4444',
          '#f97316',
          '#10b981',
        ],
        borderWidth: 2,
        hoverOffset: 20
      }]
    };

    //CONFIG AREA
    //Main chart area config
    const config = {
      type: 'doughnut',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false, //Note: the graph will break the card system and expand the card even beyond !important limits if this is set to true!
        
        //This is a very placeholder chart switch system.
        //If its a doughnut chart, cut out a 60% hole. If its a pie chart, don't cut a hole (so yes, technically the pie chart is a doughnut chart in disguise)
        //This should definitely be replaced with a switch case in future to allow more diverse chart types like bar charts!
        cutout: chartType === 'doughnut' ? '60%' : '0%', 

        //This padding below is required so that the hovered section (which expands on hover) doesn't clip out of frame
        //If you adjust the hover offset, increase this padding as well to give spare room
        layout: {
          padding: {
            top: 25,
            bottom: 25,
            left: 25,
            right: 25,
          }
        },

        plugins: {
          
          /* Code for a title. Re-enable title here if you want to use this independently. Currently the card system provides a title so we don't need it.
          title: {
            display: true,
            text: 'Compliance Scan Results',
            color: 'white',
            font: {
              size: 18,
              weight: 'bold',
            },
            padding: 20
          },
          */

          //Legend configuration 
          legend: {
            position: 'bottom',
            labels: {
              padding: 45,
              color: 'white',
              usePointStyle: true,
              font: {
                size: 16,
                /*family: '"League Spartan", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',*/
              },
            }
          },


          //Tooltip configuration
          //The tooltip will display when you hover over a section of the chart
          tooltip: {
            position: 'nearest',
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.parsed;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = ((value / total) * 100).toFixed(1);
                return ` ${label}: ${value} items (${percentage}%)`;
              }
            }
          }
        },
        animation: {
          animateScale: true,
          animateRotate: true
        }
      }
    };




    //Instantiate the chart
    chartInstanceRef.current = new ChartJS(ctx, config);

    //Destroy the existing chart (if any) 
    return () => {
      if (chartInstanceRef.current) {
        chartInstanceRef.current.destroy();
      }
    };
  }, [chartType, dataInput]); //Re-render if the chartType or data is changed 

  //Scale to fit the max size provided with the card
  return (
    <div style={{ width: '100%', height: '100%', padding: '0px' }}> 
      <canvas ref={chartRef}></canvas>
    </div>
  );
};

export default ComplianceChart;