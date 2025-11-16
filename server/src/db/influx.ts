import { InfluxDB } from "influx";
import { INFLUX_PORT, INFLUX_HOST } from "$env/static/private";

const influx = new InfluxDB({
  host: INFLUX_HOST,
  port: parseInt(INFLUX_PORT),
});

export const get_influx = async (): Promise<InfluxDB | null> => {
  try {
    const hosts = await influx.ping(5000);

    for (const host of hosts) {
      if (host.online) {
        console.log(
          `${host.url.host} responded in ${host.rtt}ms running ${host.version}`,
        );
        return influx;
      } else {
        console.log(`${host.url.host} is offline :()`);
      }
    }
    return null;
  } catch (error) {
    console.error("Error during InfluxDB ping:", error);
    return null;
  }
};
