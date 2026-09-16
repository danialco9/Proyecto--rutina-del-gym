# gym-tracker (frontend)

Mobile-first React app to log workouts at the gym. The UI is in Spanish and follows the system
light/dark theme.

## Features

- **Login** with the backend's cookie session; protected routes redirect to `/login`.
- **Live workout logging**: start from a routine (sets prefilled from its targets) or a free
  workout, add exercises from the catalog with accent-insensitive search, and log each set with
  large −/+ buttons (±2.5 kg, ±1 rep) and optional RPE.
- **Routines**: create, edit and delete routine templates; add exercises from the catalog, reorder
  them with up/down buttons and set optional targets (sets, reps, weight, RPE).
- **Body measurements**: quick daily weigh-in with optional body fat, circumferences and notes;
  picking a date that already has an entry opens it for editing. Includes a weight chart (Recharts,
  lazy-loaded) and a history with the change from the previous weigh-in.
- **Last performance** of each exercise shown while logging.
- **Rest timer** that starts when a set is completed (+15 s / skip, vibrates when done).
- **Draft persistence**: the workout in progress is saved on the device and survives reloads;
  it is sent to the API only when you finish.

## Stack

React 19, TypeScript, Vite, Tailwind CSS v4, shadcn/ui (Base UI), TanStack Query, React Router,
React Hook Form + Zod, Recharts, Vitest + Testing Library, oxlint, Prettier.

## Structure

```
src/
  components/      App layout and shadcn/ui components (ui/)
  features/
    auth/          Login page, route guard, session queries
    home/          Home page with recent workouts
    measurements/  Weigh-ins and body measurements: form, weight chart, history
    routines/      Routine list and editor (React Hook Form field arrays)
    workout/       Live logging: draft reducer, timer, exercise picker, set rows
  lib/             API client, types, formatting, labels
  test/            Test setup, fetch mock and render helper
```

## Scripts

Requires Node.js 24 and pnpm. Start the backend on port 8000 first: the dev server proxies `/api`
to it, so the auth cookie stays same-origin.

```bash
pnpm install
pnpm dev            # http://localhost:5173
pnpm build          # type-check and production build
pnpm test           # unit and component tests
pnpm lint           # oxlint
pnpm format         # Prettier
```
