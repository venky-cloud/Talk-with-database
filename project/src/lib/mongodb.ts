import { MongoClient, Db } from 'mongodb';

let client: MongoClient | null = null;
let db: Db | null = null;

const MONGODB_URI = "mongodb+srv://admin:admin@tedbus.vqk1yid.mongodb.net/?retryWrites=true&w=majority&appName=tedbus";

export async function connectToMongoDB() {
  try {
    if (!client) {
      client = new MongoClient(MONGODB_URI);
      await client.connect();
      db = client.db();
      console.log('Connected to MongoDB');
    }
    return { client, db };
  } catch (error) {
    console.error('MongoDB connection error:', error);
    throw error;
  }
}

export async function getCollection(collectionName: string) {
  try {
    if (!db) {
      await connectToMongoDB();
    }
    return db!.collection(collectionName);
  } catch (error) {
    console.error('Error getting collection:', error);
    throw error;
  }
}

export async function closeConnection() {
  try {
    if (client) {
      await client.close();
      client = null;
      db = null;
      console.log('Disconnected from MongoDB');
    }
  } catch (error) {
    console.error('Error closing MongoDB connection:', error);
    throw error;
  }
}