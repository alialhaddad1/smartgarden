import { NextResponse } from "next/server";
import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
import { unmarshall } from "@aws-sdk/util-dynamodb";

const dynamoDB = new DynamoDBClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});

type PlantStatus = {
  plantName: string;
  status: {
    status: string;
    message?: string;
  }[];
};

const fetchPlantStatus = async (): Promise<PlantStatus[]> => {
  try {
    const command = new ScanCommand({ TableName: "plantData" });
    const data = await dynamoDB.send(command);

    return (
      data.Items?.map((rawPlant) => {
        const plant = unmarshall(rawPlant);

        const moistureMin = Number(plant.moisture) * 0.85;
        const moistureMax = Number(plant.moisture) * 1.15;
        const sunlightMin = Number(plant.sunlight) * 0.85;
        const sunlightMax = Number(plant.sunlight) * 1.15;
        const tempRange = plant.temperature?.split("-").map(Number) || [];
        const humidityMin = 30;
        const humidityMax = 70;
        const batteryMin = 20;

        const statuses: { status: string; message?: string }[] = [];

        if (plant.microMoisture < moistureMin)
          statuses.push({ status: "too little moisture", message: plant.shortageMoisture });
        if (plant.microMoisture > moistureMax)
          statuses.push({ status: "too much moisture", message: plant.surplusMoisture });

        if (plant.microSun < sunlightMin)
          statuses.push({ status: "too little sunlight", message: plant.shortageSun });
        if (plant.microSun > sunlightMax)
          statuses.push({ status: "too much sunlight", message: plant.surplusSun });

        if (tempRange.length === 2) {
          if (plant.microTemp < tempRange[0])
            statuses.push({ status: "too cold", message: plant.shortageTemp });
          if (plant.microTemp > tempRange[1])
            statuses.push({ status: "too hot", message: plant.surplusTemp });
        }

        if (plant.microHumid < humidityMin)
          statuses.push({ status: "humidity too low", message: "Increase ambient humidity" });
        if (plant.microHumid > humidityMax)
          statuses.push({ status: "humidity too high", message: "Reduce ambient humidity" });

        if (plant.microBattery < batteryMin)
          statuses.push({ status: "battery low", message: "Recharge or replace battery" });

        if (plant.microLED)
          statuses.push({ status: `LED status: ${plant.microLED}` });

        return {
          plantName: plant.plantName,
          status: statuses.length
            ? statuses
            : [{ status: "looking good", message: "Everything is fine" }],
        };
      }) || []
    );
  } catch (error) {
    console.error("Error fetching plant status:", error);
    return [];
  }
};

export const GET = async () => {
  try {
    const plantStatuses = await fetchPlantStatus();
    return NextResponse.json(plantStatuses, { status: 200 });
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";

    if (error instanceof Error) {
      errorMessage = error.message;
    }

    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
};