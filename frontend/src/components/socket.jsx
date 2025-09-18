// socket.js
import { io } from "socket.io-client";

// Only one socket instance ever created
export const socket = io("http://localhost:5000");
