import { command, getRequestEvent, query } from "$app/server";
import {
  connectNetworkSchema,
  ipAddressSchema,
  networkListSchema,
  networkSchema,
} from "$lib/schema/network";
import { redirect } from "@sveltejs/kit";
import axios from "axios";
import z from "zod";
import { UTIL_SERVER_IP, UTIL_SERVER_PORT } from "$env/static/private";

function requireAdmin() {
  const { locals, request } = getRequestEvent();
  if (!locals.user) {
    redirect(307, "/");
  } else {
    if (locals.user?.role !== "admin") {
      redirect(307, "/dashboard");
    }
  }
  return {
    user: locals.user,
    session: locals.session,
    headers: request.headers,
  };
}

export const listNetworks = query(async () => {
  const _ = requireAdmin();
  type Network = z.infer<typeof networkSchema>;
  let networks: Array<{ ssid: string; security: string; signal: string }> = [];
  try {
    await axios
      .get<{
        output: Network[];
      }>(`http://${UTIL_SERVER_IP}:${UTIL_SERVER_PORT}/network`)
      .then((data) => {
        networks = networkListSchema.parse(data.data.output);
      });
  } catch (error) {
    console.log(error);
  }
  return networks;
});

export const connectNetwork = command(
  connectNetworkSchema,
  async ({ ssid, password }) => {
    let result = "";
    try {
      let response: string = await axios.post(
        `http://${UTIL_SERVER_IP}:${UTIL_SERVER_PORT}/network`,
        {
          ssid: ssid,
          password: password,
        },
      );
      result = response;
    } catch (error) {
      console.log(error);
    }

    await listIp().refresh();
    await getConnectedNetwork().refresh();
    return result;
  },
);

export const getConnectedNetwork = query(async () => {
  let network: string = "";
  try {
    await axios
      .get<string>(
        `http://${UTIL_SERVER_IP}:${UTIL_SERVER_PORT}/connected/network`,
      )
      .then((data) => {
        network = data.data;
      });
  } catch (error) {
    console.log(error);
  }
  return network;
});

export const listIp = query(async () => {
  type IpSchema = z.infer<typeof ipAddressSchema>;
  let ips: IpSchema[] = [];
  try {
    await axios
      .get<IpSchema[]>(`http://${UTIL_SERVER_IP}:${UTIL_SERVER_PORT}/ipaddress`)
      .then((data) => {
        ips = data.data;
      });
  } catch (error) {
    console.log(error);
  }
  return ips;
});
