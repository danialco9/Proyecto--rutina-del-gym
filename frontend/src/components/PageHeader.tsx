import type { ReactNode } from 'react'

interface PageHeaderProps {
  eyebrow: string
  title: string
  description: string
  action?: ReactNode
}

/** Shared heading for the main screens: a small label, a large title and an optional action. */
export function PageHeader({ eyebrow, title, description, action }: PageHeaderProps) {
  return (
    <header className="flex items-start justify-between gap-4 border-b pb-5">
      <div className="min-w-0 space-y-1">
        <p className="eyebrow">{eyebrow}</p>
        <h1 className="font-heading text-2xl font-semibold tracking-tight lg:text-3xl">{title}</h1>
        <p className="text-muted-foreground text-sm">{description}</p>
      </div>
      {action}
    </header>
  )
}
