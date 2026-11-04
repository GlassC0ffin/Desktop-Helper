# Roadmap

This is the literal sequence I follow every time a new assignment
drops and I copy this template.

1. **Define intent + constraints** — rewrite `SYSTEM_CHARTER.md` for
   the new assignment before touching code.
2. **Sketch the system in words** — write signal / parameter /
   behavior / readability test as plain sentences.
3. **Build the smallest working version** — get one signal moving one
   parameter, nothing else, using the existing `/src` structure.
4. **Iterate through visible tests** — run it, watch it, change one
   thing at a time. Log each real change in
   `/process/changelog.md`.
5. **Polish only after meaning is legible** — no visual polish, extra
   parameters, or libraries until the readability test passes.
6. **Deploy and capture process evidence** — push, deploy, screenshot
   (see `/process/screenshots/`), then finish the README.
