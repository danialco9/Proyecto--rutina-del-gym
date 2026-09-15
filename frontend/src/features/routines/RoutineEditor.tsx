import { zodResolver } from '@hookform/resolvers/zod'
import { ChevronLeftIcon, PlusIcon, Trash2Icon } from 'lucide-react'
import { useState } from 'react'
import { useFieldArray, useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router'
import { toast } from 'sonner'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { FormField } from '@/features/auth/AuthForm'
import { ExercisePicker } from '@/features/workout/ExercisePicker'
import { ApiError } from '@/lib/api'
import type { Routine } from '@/lib/types'
import { useCreateRoutine, useDeleteRoutine, useUpdateRoutine } from './queries'
import {
  emptyRoutineForm,
  formToRoutinePayload,
  routineFormSchema,
  routineToForm,
  type RoutineFormValues,
} from './routine-form'
import { RoutineExerciseFields } from './RoutineExerciseFields'

function saveErrorMessage(error: Error): string {
  if (error instanceof ApiError && error.status === 409) {
    return 'Ya tienes una rutina con ese nombre'
  }
  if (error instanceof ApiError && error.status === 422) {
    return 'Algún ejercicio ya no está disponible. Revisa la lista e inténtalo de nuevo.'
  }
  return 'No se pudo guardar la rutina. Inténtalo de nuevo.'
}

interface RoutineEditorProps {
  routine?: Routine
}

export function RoutineEditor({ routine }: RoutineEditorProps) {
  const navigate = useNavigate()
  const createRoutine = useCreateRoutine()
  const updateRoutine = useUpdateRoutine(routine?.id)
  const deleteRoutine = useDeleteRoutine()
  const [pickerOpen, setPickerOpen] = useState(false)
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<RoutineFormValues>({
    resolver: zodResolver(routineFormSchema),
    defaultValues: routine ? routineToForm(routine) : emptyRoutineForm,
  })
  const { fields, append, remove, move } = useFieldArray({ control, name: 'exercises' })

  const saving = createRoutine.isPending || updateRoutine.isPending
  const saveError = createRoutine.error ?? updateRoutine.error
  const exercisesError = errors.exercises?.root?.message ?? errors.exercises?.message

  const onSubmit = handleSubmit(async (values) => {
    const payload = formToRoutinePayload(values)
    try {
      if (routine) {
        await updateRoutine.mutateAsync(payload)
      } else {
        await createRoutine.mutateAsync(payload)
      }
      toast.success(routine ? 'Rutina actualizada' : 'Rutina creada')
      navigate('/rutinas')
    } catch {
      // The error is rendered from the mutation state.
    }
  })

  const onDelete = async () => {
    const confirmed = window.confirm(
      `¿Eliminar la rutina "${routine?.name}"? Los entrenos que ya registraste se conservan.`,
    )
    if (!routine || !confirmed) {
      return
    }
    try {
      await deleteRoutine.mutateAsync(routine.id)
      toast.success('Rutina eliminada')
      navigate('/rutinas')
    } catch {
      toast.error('No se pudo eliminar la rutina.')
    }
  }

  return (
    <form className="space-y-5" onSubmit={onSubmit} noValidate>
      <header className="space-y-1">
        <Link
          to="/rutinas"
          className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-sm"
        >
          <ChevronLeftIcon className="size-4" aria-hidden />
          Volver a rutinas
        </Link>
        <h1 className="font-heading text-2xl font-semibold">{routine ? 'Editar rutina' : 'Nueva rutina'}</h1>
      </header>

      <FormField
        id="routine-name"
        label="Nombre"
        placeholder="Ej.: Pierna"
        error={errors.name?.message}
        {...register('name')}
      />

      <div className="space-y-2">
        <Label htmlFor="routine-description">Descripción (opcional)</Label>
        <Textarea
          id="routine-description"
          placeholder="Ej.: Miércoles, foco en cuádriceps"
          aria-invalid={errors.description ? true : undefined}
          {...register('description')}
        />
        {errors.description && <p className="text-destructive text-sm">{errors.description.message}</p>}
      </div>

      <section className="space-y-3">
        <div className="space-y-1">
          <h2 className="font-heading text-lg font-medium">Ejercicios</h2>
          <p className="text-muted-foreground text-sm">
            En el orden en que los haces. Los objetivos son opcionales y se precargan al empezar el entreno.
          </p>
        </div>
        {fields.length === 0 && (
          <p className="text-muted-foreground rounded-xl border border-dashed p-6 text-center text-sm">
            Todavía no hay ejercicios en esta rutina.
          </p>
        )}
        <ol className="space-y-3">
          {fields.map((field, index) => (
            <li key={field.id}>
              <RoutineExerciseFields
                index={index}
                name={field.name}
                isFirst={index === 0}
                isLast={index === fields.length - 1}
                register={register}
                errors={errors.exercises?.[index]}
                onMoveUp={() => move(index, index - 1)}
                onMoveDown={() => move(index, index + 1)}
                onRemove={() => remove(index)}
              />
            </li>
          ))}
        </ol>
        {exercisesError && <p className="text-destructive text-sm">{exercisesError}</p>}
        <Button
          type="button"
          variant="outline"
          size="lg"
          className="h-12 w-full text-base"
          onClick={() => setPickerOpen(true)}
        >
          <PlusIcon />
          Añadir ejercicio
        </Button>
      </section>

      {saveError && (
        <Alert variant="destructive">
          <AlertDescription>{saveErrorMessage(saveError)}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Button type="submit" size="lg" className="h-12 w-full text-base" disabled={saving}>
          {saving ? 'Guardando…' : 'Guardar rutina'}
        </Button>
        {routine && (
          <Button
            type="button"
            variant="destructive"
            className="h-10 w-full"
            disabled={deleteRoutine.isPending}
            onClick={onDelete}
          >
            <Trash2Icon />
            Eliminar rutina
          </Button>
        )}
      </div>

      <ExercisePicker
        open={pickerOpen}
        onOpenChange={setPickerOpen}
        onSelect={(exercise) => {
          append({
            exerciseId: exercise.id,
            name: exercise.name,
            targetSets: null,
            targetReps: null,
            targetWeightKg: null,
            targetRpe: null,
          })
          setPickerOpen(false)
        }}
      />
    </form>
  )
}
