import { Navigate, type RouteObject } from 'react-router'
import { AppLayout } from '@/components/AppLayout'
import { AccountPage } from '@/features/account/AccountPage'
import { LoginPage } from '@/features/auth/LoginPage'
import { RegisterPage } from '@/features/auth/RegisterPage'
import { RequireAuth } from '@/features/auth/RequireAuth'
import { HomePage } from '@/features/home/HomePage'
import { MeasurementsPage } from '@/features/measurements/MeasurementsPage'
import { ProgressPage } from '@/features/progress/ProgressPage'
import { RoutineEditorPage } from '@/features/routines/RoutineEditorPage'
import { RoutinesPage } from '@/features/routines/RoutinesPage'
import { WorkoutPage } from '@/features/workout/WorkoutPage'

export const routes: RouteObject[] = [
  { path: '/login', element: <LoginPage /> },
  { path: '/registro', element: <RegisterPage /> },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <AppLayout />,
        children: [
          { index: true, element: <HomePage /> },
          { path: 'entrenar', element: <WorkoutPage /> },
          { path: 'rutinas', element: <RoutinesPage /> },
          { path: 'rutinas/nueva', element: <RoutineEditorPage /> },
          { path: 'rutinas/:routineId', element: <RoutineEditorPage /> },
          { path: 'medidas', element: <MeasurementsPage /> },
          { path: 'progreso', element: <ProgressPage /> },
          { path: 'cuenta', element: <AccountPage /> },
        ],
      },
    ],
  },
  { path: '*', element: <Navigate to="/" replace /> },
]
