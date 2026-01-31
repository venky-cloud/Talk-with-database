import type { VercelRequest, VercelResponse } from '@vercel/node';
import { MongoClient } from 'mongodb';

const MONGODB_URI = "mongodb+srv://admin:admin@tedbus.vqk1yid.mongodb.net/?retryWrites=true&w=majority&appName=tedbus";
const DB_NAME = 'test'; // Change to your DB name if needed

export default async function handler(req: VercelRequest, res: VercelResponse) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method Not Allowed' });
  }

  const client = new MongoClient(MONGODB_URI);

  try {
    await client.connect();
    const db = client.db(DB_NAME);
    const collection = db.collection('queries');
    const doc = req.body;
    const result = await collection.insertOne(doc);
    res.status(200).json({ insertedId: result.insertedId });
  } catch (error) {
    console.error(error);
    res.status(500).json({ message: 'Failed to save query', error });
  } finally {
    await client.close();
  }
}
