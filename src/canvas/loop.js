// loop.js
// Job: own the animation loop and the one visible behavior.
//
// Template contract (see /docs/SYSTEM_CHARTER.md):
//   Signal:    mouse X position
//   Parameter: radius
//   Behavior:  a ring pulses faster as radius grows
//   Readability test: moving left -> right should visibly speed up
//                      the pulse within ~5 seconds.

export function startLoop({ ctx, getWidth, getHeight, input }) {
  let time = 0;

  function frame() {
    const width = getWidth();
    const height = getHeight();

    // clear
    ctx.fillStyle = "#0a0a0a";
    ctx.fillRect(0, 0, width, height);

    // --- signal -> parameter ---
    // mouse X (0..width) maps to a radius range (40..260)
    const mouseX = input.getX();
    const radius = mapRange(mouseX, 0, width, 40, 260);

    // radius also drives pulse speed: bigger radius, faster pulse
    const pulseSpeed = mapRange(radius, 40, 260, 0.02, 0.12);
    time += pulseSpeed;

    // --- behavior ---
    // ring "breathes": radius oscillates around the mapped radius
    const breath = Math.sin(time) * 12;
    const drawnRadius = radius + breath;

    ctx.beginPath();
    ctx.arc(width / 2, height / 2, Math.max(drawnRadius, 1), 0, Math.PI * 2);
    ctx.strokeStyle = "#f2f2f2";
    ctx.lineWidth = 2;
    ctx.stroke();

    requestAnimationFrame(frame);
  }

  requestAnimationFrame(frame);
}

function mapRange(value, inMin, inMax, outMin, outMax) {
  const t = (value - inMin) / (inMax - inMin);
  const clamped = Math.min(1, Math.max(0, t));
  return outMin + clamped * (outMax - outMin);
}
