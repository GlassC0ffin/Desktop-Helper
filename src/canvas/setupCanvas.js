// setupCanvas.js
// Job: turn a raw <canvas> element into a HiDPI-correct drawing surface.
// Nothing in here knows about "the sketch" — it only knows about pixels.

export function setupCanvas(canvasEl) {
  const ctx = canvasEl.getContext("2d");

  function resize() {
    const dpr = window.devicePixelRatio || 1;
    const cssWidth = window.innerWidth;
    const cssHeight = window.innerHeight;

    // Backing store is scaled up by devicePixelRatio...
    canvasEl.width = cssWidth * dpr;
    canvasEl.height = cssHeight * dpr;

    // ...but the CSS size stays the same, so it doesn't look huge.
    canvasEl.style.width = `${cssWidth}px`;
    canvasEl.style.height = `${cssHeight}px`;

    // Reset then scale the context so we can keep drawing in CSS pixel
    // coordinates instead of doing DPR math everywhere else.
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.scale(dpr, dpr);
  }

  resize();
  window.addEventListener("resize", resize);

  return {
    ctx,
    getWidth: () => window.innerWidth,
    getHeight: () => window.innerHeight,
  };
}
