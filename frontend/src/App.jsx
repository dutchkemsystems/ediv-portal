import React, { Suspense, lazy } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { CircularProgress, Box } from '@mui/material'
import Layout from './components/common/Layout'
import ErrorBoundary from './components/common/ErrorBoundary'

const Login = lazy(() => import('./pages/Login'))
const Dashboard = lazy(() => import('./pages/Dashboard'))
const Schools = lazy(() => import('./pages/Schools'))
const Staff = lazy(() => import('./pages/Staff'))
const Students = lazy(() => import('./pages/Students'))
const Attendance = lazy(() => import('./pages/Attendance'))
const Academics = lazy(() => import('./pages/Academics'))
const Finance = lazy(() => import('./pages/Finance'))
const HR = lazy(() => import('./pages/HR'))
const Registry = lazy(() => import('./pages/Registry'))
const Files = lazy(() => import('./pages/Files'))
const Workflows = lazy(() => import('./pages/Workflows'))
const Communication = lazy(() => import('./pages/Communication'))
const Notifications = lazy(() => import('./pages/Notifications'))
const Timetable = lazy(() => import('./pages/Timetable'))
const Transport = lazy(() => import('./pages/Transport'))
const Assets = lazy(() => import('./pages/Assets'))
const Discipline = lazy(() => import('./pages/Discipline'))
const Library = lazy(() => import('./pages/Library'))
const ELearning = lazy(() => import('./pages/ELearning'))
const Wellness = lazy(() => import('./pages/Wellness'))
const Alumni = lazy(() => import('./pages/Alumni'))
const Infrastructure = lazy(() => import('./pages/Infrastructure'))
const Inspection = lazy(() => import('./pages/Inspection'))
const French = lazy(() => import('./pages/French'))
const CoCurricular = lazy(() => import('./pages/CoCurricular'))
const CPD = lazy(() => import('./pages/CPD'))
const Reports = lazy(() => import('./pages/Reports'))
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'))
const ResetPassword = lazy(() => import('./pages/ResetPassword'))

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useSelector((state) => state.auth)
  return isAuthenticated ? children : <Navigate to="/login" />
}

function Loading() {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
      <CircularProgress />
    </Box>
  )
}

function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Loading />}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          {[
            { path: '/', element: Dashboard },
            { path: '/schools', element: Schools },
            { path: '/staff', element: Staff },
            { path: '/students', element: Students },
            { path: '/attendance', element: Attendance },
            { path: '/academics', element: Academics },
            { path: '/finance', element: Finance },
            { path: '/hr', element: HR },
            { path: '/registry', element: Registry },
            { path: '/files', element: Files },
            { path: '/workflows', element: Workflows },
            { path: '/communication', element: Communication },
            { path: '/notifications', element: Notifications },
            { path: '/timetable', element: Timetable },
            { path: '/transport', element: Transport },
            { path: '/assets', element: Assets },
            { path: '/discipline', element: Discipline },
            { path: '/library', element: Library },
            { path: '/e-learning', element: ELearning },
            { path: '/wellness', element: Wellness },
            { path: '/alumni', element: Alumni },
            { path: '/infrastructure', element: Infrastructure },
            { path: '/inspection', element: Inspection },
            { path: '/french', element: French },
            { path: '/co-curricular', element: CoCurricular },
            { path: '/cpd', element: CPD },
            { path: '/reports', element: Reports },
          ].map(({ path, element: Page }) => (
            <Route
              key={path}
              path={path}
              element={
                <ProtectedRoute>
                  <Layout><Page /></Layout>
                </ProtectedRoute>
              }
            />
          ))}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  )
}

export default App
