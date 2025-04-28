import { NextResponse } from "next/server";
import { DynamoDBClient, ScanCommand } from "@aws-sdk/client-dynamodb";
//import { unmarshall } from "@aws-sdk/util-dynamodb";

const dynamoDB = new DynamoDBClient({
  region: process.env.AWS_REGION,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});
/*
interface PlantStatus {
  plantName: string;
  status: { status: string; message?: string }[];
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
          const humidityMin = Number(plant.humidity) * 0.85;
          const humidityMax = Number(plant.humidity) * 1.15;
          const batteryMin = 20;
  
          const microMoisture = Number(plant.microMoisture);
          const microSun = Number(plant.microSun);
          const microTemp = Number(plant.microTemp);
          const microHumid = Number(plant.microHumid);
          const microBattery = Number(plant.microBattery);
  
          const statuses: { status: string; message?: string }[] = [];
  
          if (microMoisture < moistureMin)
            statuses.push({ status: "too little moisture", message: plant.shortageMoisture });
          if (microMoisture > moistureMax)
            statuses.push({ status: "too much moisture", message: plant.surplusMoisture });
  
          if (microSun < sunlightMin)
            statuses.push({ status: "too little sunlight", message: plant.shortageSun });
          if (microSun > sunlightMax)
            statuses.push({ status: "too much sunlight", message: plant.surplusSun });
  
          if (tempRange.length === 2) {
            if (microTemp < tempRange[0])
              statuses.push({ status: "too cold", message: plant.shortageTemp });
            if (microTemp > tempRange[1])
              statuses.push({ status: "too hot", message: plant.surplusTemp });
          }
  
          if (microHumid < humidityMin)
            statuses.push({ status: "humidity too low", message: "Increase ambient humidity" });
          if (microHumid > humidityMax)
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
        }) || []
      );
    } catch (error) {
      console.error("Error fetching plant status:", error);
      return [];
    }
};
*/

export async function GET() {
  const params = {
    TableName: "plantData",
  };
 
  try {
    //const plantStatuses = await fetchPlantStatus();
    const data = await dynamoDB.send(new ScanCommand(params));
    const plants = data.Items?.map((item) => ({
      plantName: item.plantName.S,
      moisture: item.moisture.S,
      sunlight: item.sunlight.S,
      temperature: item.temperature.S,
      humidity: item.humidity.S,
      led: item.led.S,
      battery: item.battery.S,
    })) || [];
 
    return NextResponse.json(plants);
  } catch (error: unknown) {
    let errorMessage = "An unknown error occurred";
  
    if (error instanceof Error) {
      errorMessage = error.message;
    }
  
    return NextResponse.json({ error: errorMessage }, { status: 500 });
  }
}

/* 
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
*/