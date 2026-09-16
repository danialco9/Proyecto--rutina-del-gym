import { useMemo, useState } from 'react'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Input } from '@/components/ui/input'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { EQUIPMENT_LABELS, MUSCLE_GROUP_LABELS } from '@/lib/labels'
import type { Exercise } from '@/lib/types'
import { filterExercises } from './exercise-search'
import { useExercises } from './queries'

interface ExercisePickerProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSelect: (exercise: Exercise) => void
}

export function ExercisePicker({ open, onOpenChange, onSelect }: ExercisePickerProps) {
  const [search, setSearch] = useState('')
  const exercises = useExercises()
  const results = useMemo(() => filterExercises(exercises.data ?? [], search), [exercises.data, search])

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="mx-auto max-h-[85dvh] max-w-2xl rounded-t-xl">
        <SheetHeader>
          <SheetTitle>Añadir ejercicio</SheetTitle>
          <SheetDescription>Busca por nombre, grupo muscular o material.</SheetDescription>
        </SheetHeader>
        <div className="px-4">
          <Input
            type="search"
            aria-label="Buscar ejercicio"
            placeholder="Ej.: prensa, pecho, polea…"
            className="h-11"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </div>
        <div className="min-h-0 overflow-y-auto px-2 pb-4">
          {exercises.isPending && <p className="text-muted-foreground px-2 text-sm">Cargando ejercicios…</p>}
          {exercises.isError && (
            <Alert variant="destructive" className="mx-2 w-auto">
              <AlertDescription>No se pudo cargar el catálogo de ejercicios.</AlertDescription>
            </Alert>
          )}
          {exercises.isSuccess && results.length === 0 && (
            <p className="text-muted-foreground px-2 text-sm">No hay ejercicios que coincidan.</p>
          )}
          <ul>
            {results.map((exercise) => (
              <li key={exercise.id}>
                <button
                  type="button"
                  className="hover:bg-muted flex w-full flex-col items-start rounded-lg px-2 py-2.5 text-left transition-colors"
                  onClick={() => onSelect(exercise)}
                >
                  <span className="font-medium">{exercise.name}</span>
                  <span className="text-muted-foreground text-xs">
                    {MUSCLE_GROUP_LABELS[exercise.muscle_group]}
                    {exercise.equipment && ` · ${EQUIPMENT_LABELS[exercise.equipment]}`}
                  </span>
                </button>
              </li>
            ))}
          </ul>
        </div>
      </SheetContent>
    </Sheet>
  )
}
