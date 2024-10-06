// src/Simulation.js
import React, { useState, useEffect } from "react";
import axios from "axios";
import SimulationForm from "./SimulationForm"; // Import the new form component
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const Simulation = () => {
  const [simulationData, setSimulationData] = useState(null);
  const [salePrice, setSalePrice] = useState(50);
  const [purchasePrice, setPurchasePrice] = useState(100);


  // Fetch initial simulation data using POST
  useEffect(() => {
    const fetchData = async () => {
      try {
        const initialData = {
          // Include any necessary initial data here if needed
          u_price: 50,
          u_sale: 100,
          benefit_rate: 0.1,
          expences_F: 10000,
          delay_supply: 5,
          stock_rate: 0.2,
          order_n: 50,
          order_f: 4,
          due_date: 60,
          order_q: 100,
          order_fluc: 5,
        };

        const response = await axios.post(
          "http://127.0.0.1:5000/api/simulation",
          initialData
        );
        setSimulationData(response.data);
        console.log("Simulation data fetched successfully!", response.data);
      } catch (error) {
        console.error(
          "There was an error fetching the simulation data!",
          error
        );
      }
    };

    fetchData();
  }, []);

  // Handle form submission
  const handleFormSubmit = async (data) => {
    try {
      console.log("Submitting simulation data...", data);
      setPurchasePrice(data.u_price);
      setSalePrice(data.u_sale);
      const response = await axios.post(
        "http://127.0.0.1:5000/api/simulation",
        data
      );
      console.log("Simulation submitted successfully!", response.data);
      setSimulationData(response.data); // Update the state with the new simulation data
    } catch (error) {
      console.error("Error submitting simulation data!", error);
    }
  };

  if (!simulationData) {
    return <div>Loading...</div>;
  }

  const { dates, stock_price, quantity_ordered, cumulative_supply } =
    simulationData;

  // Create data structure for Recharts
  const chartData = dates.map((date, index) => ({
    date: date,
    stockPrice: stock_price[index],
    quantityOrdered: quantity_ordered[index],
    cumulativeSupply: cumulative_supply[index],
  }));

  return (
    <div className="d-flex flex-row  gap-3 w-100">
      <div className="container col-4">
        <SimulationForm onSubmit={handleFormSubmit} />{" "}
      </div>
      {/* Include the form here */}
      <div className="container col-9">
        <h1>Stock Simulation Charts</h1>
        {/* Chart 1: Forecast Sales */}
        <h2>Forecast Sales</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              label={{
                value: "Date",
                position: "insideBottomRight",
                offset: -5,
              }}
            />
            <YAxis
              label={{
                value: "Quantity Ordered",
                angle: -90,
                position: "insideLeft",
              }}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="quantityOrdered"
              stroke="#8884d8"
              name="Quantity Ordered"
            />
          </LineChart>
        </ResponsiveContainer>
        {/* Chart 2: Forecast Supply Planning */}
        <h2>Forecast Supply Planning</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              label={{
                value: "Date",
                position: "insideBottomRight",
                offset: -5,
              }}
            />
            <YAxis
              label={{
                value: "Cumulative Supply",
                angle: -90,
                position: "insideLeft",
              }}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="cumulativeSupply"
              stroke="#82ca9d"
              name="Cumulative Supply"
            />
          </LineChart>
        </ResponsiveContainer>
        {/* Chart 3: Stock Price Dynamics */}
        <h2>Stock Price Dynamics</h2>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              label={{
                value: "Date",
                position: "insideBottomRight",
                offset: -5,
              }}
            />
            <YAxis
              label={{
                value: "Stock Price",
                angle: -90,
                position: "insideLeft",
              }}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="stockPrice"
              stroke="#8884d8"
              name="Stock Price"
            />
            <Line
              type="monotone"
              dataKey={() => salePrice}
              stroke="blue"
              name="Unit Sale Price"
              strokeDasharray="5 5"
            />
            <Line
              type="monotone"
              dataKey={() => purchasePrice}
              stroke="green"
              name="Unit Purchase Price"
              strokeDasharray="5 5"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Simulation;
