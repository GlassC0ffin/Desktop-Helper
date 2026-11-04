# Prompts

Copilot (or any AI assistant) only gets used inside the constraints
already written in `SYSTEM_CHARTER.md`. I'm not asking it for ideas —
I'm asking it for specific technical help.

## Context block

Paste this at the top of a chat/session before asking anything:

> I'm building a Canvas-based studio engine. Files: `main.js` wires
> things together; `/src/canvas/setupCanvas.js` handles HiDPI setup;
> `/src/canvas/loop.js` owns the animation loop and behavior;
> `/src/input/input.js` captures raw input signals;
> `/src/utils/math.js` holds small numeric helpers. No external
> libraries in the template sketch — pure Canvas only. Keep each file
> to one job.

## Reusable prompt templates

**1. Canvas draw loop**
> Given this signal->parameter mapping: [describe it], write the
> body of a `requestAnimationFrame` loop that draws [shape] whose
> [visual property] responds to [parameter]. Keep it framework-free.

**2. Input mapping**
> I have a raw browser event (e.g. mousemove, scroll, keydown). Help
> me capture it in `input.js` as a simple getter function, without
> putting any drawing or mapping logic in that file.

**3. Debugging**
> Here is my loop function: [paste code]. The behavior I expect is
> [describe]. What I'm actually seeing is [describe]. What's the
> likely cause, and what's the smallest fix?

## Rule

Every AI response gets followed by my own explanation, in plain
language, of what changed and why — written as a code comment or a
changelog line. No paste-dumps without annotation.
