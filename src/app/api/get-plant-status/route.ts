import { NextResponse } from 'next/server';
import { DynamoDBClient, ScanCommand, UpdateItemCommand } from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

const dynamoDB = new DynamoDBClient({
    region: "us-east-2",
    credentials: {
      accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
      secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
    },
  });
  
  export async function GET() {
    try {
      const [plantDataRaw, speciesDataRaw] = await Promise.all([
        dynamoDB.send(new ScanCommand({ TableName: "plantData" })),
        dynamoDB.send(new ScanCommand({ TableName: "speciesDatabase" })),
      ]);
  
      const plantData = plantDataRaw.Items?.map((item) => unmarshall(item)) || [];
      const speciesData = speciesDataRaw.Items?.map((item) => unmarshall(item)) || [];
      const speciesMap = new Map(speciesData.map((species) => [species.plantName, species]));
  
      const result = await Promise.all(
        plantData.map(async (plant) => {
          const species = speciesMap.get(plant.plantName);
          if (!species) {
            return {
              plantName: plant.plantName,
              status: [{ status: "no species data", message: "No matching species data found." }],
            };
          }
  
          const statuses: { status: string; message?: string }[] = [];
  
          const microMoisture = Number(plant.moisture);
          const microSun = Number(plant.sunlight);
          const microTemp = Number(plant.temperature);
          const microHumid = Number(plant.humidity);
          const microBattery = Number(plant.battery);
  
          const moistureRange = (species.moisture?.split("-") ?? []).map(Number);
          const sunlightRange = (species.sunlight?.split("-") ?? []).map(Number);
          const tempRange = (species.temperature?.split("-") ?? []).map(Number);
          const humidityMin = Number(species.humidity) * 0.85;
          const humidityMax = Number(species.humidity) * 1.15;
          const batteryMin = 20;
          
          if(moistureRange.length === 2) {
            if (microMoisture < moistureRange[0])
                statuses.push({ status: "too little moisture", message: species.shortageMoisture });
            else if (microMoisture > moistureRange[1])
                statuses.push({ status: "too much moisture", message: species.surplusMoisture });
          }
  
          if(sunlightRange.length === 2) {
            if (microSun < sunlightRange[0])
                statuses.push({ status: "too little sunlight", message: species.shortageSun });
            else if (microSun > sunlightRange[1])
                statuses.push({ status: "too much sunlight", message: species.surplusSun });
          }
  
          if (tempRange.length === 2) {
            if (microTemp < tempRange[0])
              statuses.push({ status: "too cold", message: species.shortageTemp });
            else if (microTemp > tempRange[1])
              statuses.push({ status: "too hot", message: species.surplusTemp });
          }
  
          if (microHumid < humidityMin)
            statuses.push({ status: "humidity too low", message: species.shortageHumid || "Increase ambient humidity" });
          else if (microHumid > humidityMax)
            statuses.push({ status: "humidity too high", message: species.surplusHumid || "Reduce ambient humidity" });
  
          if (microBattery < batteryMin)
            statuses.push({ status: "battery low", message: "Recharge or replace battery" });
  
          if (plant.microLED)
            statuses.push({ status: `LED status: ${plant.microLED}` });
  
          const finalStatuses = statuses.length
            ? statuses
            : [{ status: "looking good", message: "Everything is fine" }];
  
          const ledColor =
            finalStatuses.length === 1 && finalStatuses[0].status === "looking good"
              ? "#00FF00"
              : "#FF0000";
  
          if (plant.led !== ledColor) {
            await dynamoDB.send(
              new UpdateItemCommand({
                TableName: "plantData",
                Key: {
                  plantName: { S: plant.plantName },
                },
                UpdateExpression: "SET led = :ledColor",
                ExpressionAttributeValues: {
                  ":ledColor": { S: ledColor },
                },
              })
            );
          }
  
          return {
            plantName: plant.plantName,
            status: finalStatuses,
          };
        })
      );
  
      return NextResponse.json({ result });
    } catch (error) {
      console.error("Error in /api/get-plant-status:", error);
      return NextResponse.json({ error: "Failed to fetch plant status" }, { status: 500 });
    }
  }