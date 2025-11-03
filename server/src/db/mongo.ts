import { MongoClient } from "mongodb";
import { MONGODB_URI } from "$env/static/private";

export const client = new MongoClient(MONGODB_URI);

// connect to the database
export async function connect(): Promise<void> {
	await client.connect();
}

// disconnect from the database
export async function disconnect(): Promise<void> {
	await client.close();
}

// get the database
export function getDB(): any {
	return client.db();
}
