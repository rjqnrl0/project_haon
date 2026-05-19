import { Routes, Route, Navigate } from 'react-router-dom'
import { PublicLayout } from './layouts/PublicLayout'
import { AuthLayout } from './layouts/AuthLayout'
import { AuthGuard } from './components/guards/AuthGuard'
import { FaceIDGuard } from './components/guards/FaceIDGuard'
import { Toast } from './components/common/Toast'
import { LoginPage } from './pages/auth/LoginPage'
import { SignupPage } from './pages/auth/SignupPage'
import { FaceIDRegisterPage } from './pages/face/FaceIDRegisterPage'
import { FittingPage } from './pages/fitting/FittingPage'
import { FittingResultPage } from './pages/fitting/FittingResultPage'
import { BackgroundPage } from './pages/background/BackgroundPage'
import { RecommendPage } from './pages/recommend/RecommendPage'
import { ShareViewPage } from './pages/share/ShareViewPage'

function App() {
  return (
    <>
      <Toast />
      <Routes>
        {/* Public routes */}
        <Route element={<PublicLayout />}>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/share/:shareToken" element={<ShareViewPage />} />
        </Route>

        {/* Auth required routes */}
        <Route element={<AuthGuard />}>
          <Route path="/face-id/register" element={<PublicLayout />}>
            <Route index element={<FaceIDRegisterPage />} />
          </Route>

          <Route element={<FaceIDGuard />}>
            <Route element={<AuthLayout />}>
              <Route path="/fitting" element={<FittingPage />} />
              <Route path="/fitting/result/:resultId" element={<FittingResultPage />} />
              <Route path="/background/:resultId" element={<BackgroundPage />} />
              <Route path="/recommend" element={<RecommendPage />} />
            </Route>
          </Route>
        </Route>

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/fitting" replace />} />
        <Route path="*" element={<Navigate to="/fitting" replace />} />
      </Routes>
    </>
  )
}

export default App
