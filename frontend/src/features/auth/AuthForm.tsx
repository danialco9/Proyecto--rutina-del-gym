import type { ComponentProps, ReactNode } from 'react'
import { Card, CardContent, CardDescription, CardFooter, CardHeader } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

interface AuthShellProps {
  title: string
  description: string
  children: ReactNode
  footer: ReactNode
}

/** Centered card shared by the login and registration pages. */
export function AuthShell({ title, description, children, footer }: AuthShellProps) {
  return (
    <main className="flex min-h-dvh items-center justify-center px-4">
      <Card className="w-full max-w-sm">
        <CardHeader>
          <p className="text-primary text-sm font-semibold tracking-wide uppercase">Gym Tracker</p>
          <h1 className="font-heading text-xl font-semibold">{title}</h1>
          <CardDescription>{description}</CardDescription>
        </CardHeader>
        <CardContent>{children}</CardContent>
        <CardFooter className="text-muted-foreground justify-center gap-1 text-sm">{footer}</CardFooter>
      </Card>
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
