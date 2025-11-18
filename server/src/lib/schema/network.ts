import * as z from "zod";

export const networkSchema = z.object({
  ssid: z.string(),
  signal: z.string(),
  security: z.string(),
});

export const networkListSchema = networkSchema.array();

export const connectNetworkSchema = z.object({
  ssid: z.string(),
  password: z.string(),
});

export const ipAddressSchema = z.object({
  name: z.string(),
  ip: z.string(),
});
