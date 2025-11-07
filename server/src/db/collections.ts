import { getDB } from "$db/mongo";
import { sendVerificationEmailFn } from "better-auth/api";
const db = getDB();

export async function getCollection(
  collection_name: string,
  skip: number,
  limit: number,
): Promise<Record<string, any>[]> {
  const data = await db
    .collection(collection_name)
    .find({})
    .project({ _id: 0 })
    .skip(skip)
    .limit(limit)
    .toArray();

  return data;
}

export async function searchCollection(
  collection_name: string,
  search: string,
): Promise<Record<string, any>[]> {
  const data = await db
    .collection(collection_name)
    .find({ title: { $regex: search, $options: "i" } })
    .project({ _id: 0 })
    .toArray();

  return data;
}
