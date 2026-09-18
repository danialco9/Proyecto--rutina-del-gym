import type { ComponentProps, ReactNode } from 'react'
import authImage from '@/assets/hero-rack.webp'
import { Card, CardContent, CardDescription, CardFooter, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface AuthShellProps {
  title: string
  description: string
  children: ReactNode
  footer: ReactNode
}

/** Split screen shared by the login and registration pages: photography on the left, form on the
    right. Below lg the photo becomes a band above the card, so phones still get the branding. */
export function AuthShell({ title, description, children, footer }: AuthShellProps) {
  return (
    <main className="min-h-dvh lg:grid lg:grid-cols-2">
      <section className="relative isolate h-40 overflow-hidden lg:h-auto">
        <img src={authImage} alt="" className="absolute inset-0 size-full object-cover" aria-hidden />
        <div className="photo-scrim" />
        <div className="relative flex h-full flex-col justify-end p-6 lg:p-10">
          <p className="eyebrow text-white/70">Gym Tracker</p>
          <p className="font-heading mt-2 max-w-sm text-2xl font-semibold tracking-tight text-balance text-white lg:text-4xl">
            Levanta. Registra. Progresa.
          </p>
          <p className="mt-3 hidden max-w-sm text-sm text-white/80 lg:block">
            Cada serie que registras alimenta el análisis que decide tu próxima sesión.
          </p>
        </div>
      </section>

      <section className="flex items-center justify-center px-4 py-10">
        <Card className="w-full max-w-sm">
          <CardHeader>
            <h1 className="font-heading text-xl font-semibold">{title}</h1>
            <CardDescription>{description}</CardDescription>
          </CardHeader>
          <CardContent>{children}</CardContent>
          <CardFooter className="text-muted-foreground justify-center gap-1 text-sm">{footer}</CardFooter>
        </Card>
      </section>
    </main>
  )
}

interface FormFieldProps extends ComponentProps<'input'> {
  id: string
  label: string
  error?: string
}

/** Labelled input that announces its validation error to assistive technology. */
export function FormField({ id, label, error, ...inputProps }: FormFieldProps) {
  const errorId = `${id}-error`
  return (
    <div className="space-y-2">
      <Label htmlFor={id}>{label}</Label>
      <Input
        id={id}
        className="h-11"
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        {...inputProps}
      />
      {error && (
        <p id={errorId} className="text-destructive text-sm">
          {error}
        </p>
      )}
    </div>
  )
}
