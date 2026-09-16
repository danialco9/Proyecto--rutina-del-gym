const sections = [
  { title: 'Entrenar', description: 'Registra series, repeticiones, peso y esfuerzo.' },
  { title: 'Rutinas', description: 'Plantillas de rutina y catálogo de ejercicios.' },
  { title: 'Medidas', description: 'Peso corporal, grasa y perímetros.' },
  { title: 'Progreso', description: 'Récords, volumen semanal y recomendaciones.' },
] as const

export default function App() {
  return (
    <main className="mx-auto flex min-h-dvh max-w-3xl flex-col gap-8 px-4 py-10">
      <header className="space-y-2">
        <p className="text-sm font-semibold tracking-wide text-emerald-400 uppercase">Gym Tracker</p>
        <h1 className="text-3xl font-bold text-balance sm:text-4xl">Tu entrenamiento, medido</h1>
        <p className="text-slate-400">
          Registra cada sesión, sigue tu evolución y decide con datos cuándo cambiar la rutina.
        </p>
      </header>

      <ul className="grid gap-3 sm:grid-cols-2">
        {sections.map((section) => (
          <li key={section.title} className="rounded-xl border border-slate-800 bg-slate-900 p-4">
            <h2 className="font-semibold">{section.title}</h2>
            <p className="mt-1 text-sm text-slate-400">{section.description}</p>
          </li>
        ))}
      </ul>
    </main>
  )
}
