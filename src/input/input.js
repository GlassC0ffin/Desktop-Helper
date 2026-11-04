// input.js
// Job: capture raw signals from the browser and expose them as simple
// getters. Nothing in here knows about radius, pulses, or drawing —
// it only knows about the mouse.

export function setupInput() {
  let x = window.innerWidth / 2;
  let y = window.innerHeight / 2;

  window.addEventListener("mousemove", (e) => {
    x = e.clientX;
    y = e.clientY;
  });

  return {
    getX: () => x,
    getY: () => y,
  };
}
