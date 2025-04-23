import { NextResponse } from 'next/server';
import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
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

    const speciesMap = new Map(speciesData.map(species => [species.plantName, species]));

    const result = plantData.map((plant) => {
      const species = speciesMap.get(plant.plantName);
      if (!species) {
        return {
          plantName: plant.plantName,
          status: [{ status: "no species data", message: "No matching species data found." }],
        };
      }

      const statuses: { status: string; message?: string }[] = [];

      const microMoisture = Number(plant.microMoisture);
      const microSun = Number(plant.microSun);
      const microTemp = Number(plant.microTemp);
      const microHumid = Number(plant.microHumid);
      const microBattery = Number(plant.microBattery);

      const moistureMin = Number(species.moisture) * 0.85;
      const moistureMax = Number(species.moisture) * 1.15;
      const sunlightMin = Number(species.sunlight) * 0.85;
      const sunlightMax = Number(species.sunlight) * 1.15;
      const humidityMin = Number(species.humidity) * 0.85;
      const humidityMax = Number(species.humidity) * 1.15;
      const batteryMin = 20;
      const tempRange = (species.temperature?.split("-") ?? []).map(Number);

      if (microMoisture < moistureMin)
        statuses.push({ status: "too little moisture", message: species.shortageMoisture });
      else if (microMoisture > moistureMax)
        statuses.push({ status: "too much moisture", message: species.surplusMoisture });

      if (microSun < sunlightMin)
        statuses.push({ status: "too little sunlight", message: species.shortageSun });
      else if (microSun > sunlightMax)
        statuses.push({ status: "too much sunlight", message: species.surplusSun });

      if (tempRange.length === 2) {
        if (microTemp < tempRange[0])
          statuses.push({ status: "too cold", message: species.shortageTemp });
        else if (microTemp > tempRange[1])
          statuses.push({ status: "too hot", message: species.surplusTemp });
      }

      if (microHumid < humidityMin)
        statuses.push({ status: "humidity too low", message: "Increase ambient humidity" });
      else if (microHumid > humidityMax)
        statuses.push({ status: "humidity too high", message: "Reduce ambient humidity" });

      if (microBattery < batteryMin)
        statuses.push({ status: "battery low", message: "Recharge or replace battery" });

      if (plant.microLED)
        statuses.push({ status: `LED status: ${plant.microLED}` });

      return {
        plantName: plant.plantName,
        status: statuses.length
          ? statuses
          : [{ status: "looking good", message: "Everything is fine" }],
      };
    });

    return NextResponse.json({ result });
  } catch (error) {
    console.error("Error in /api/get-plant-status:", error);
    return NextResponse.json({ error: 'Failed to fetch plant status' }, { status: 500 });
  }
}
