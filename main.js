// main.js
// Job: wire the engine together. This file should stay small — it does
// not contain drawing logic, input logic, or math. It just connects
// the pieces from /src.

import { setupCanvas } from "./src/canvas/setupCanvas.js";
import { startLoop } from "./src/canvas/loop.js";
import { setupInput } from "./src/input/input.js";

const canvasEl = document.getElementById("stage");
const { ctx, getWidth, getHeight } = setupCanvas(canvasEl);
const input = setupInput();

startLoop({ ctx, getWidth, getHeight, input });
