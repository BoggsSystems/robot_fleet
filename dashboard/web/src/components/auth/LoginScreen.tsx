import { useState } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { ShieldCheck, LockKeyhole, UserRound } from 'lucide-react'
import { demoCredentials, useAuth } from '../../auth/AuthProvider'
import '../../App.css'
import './LoginScreen.css'

type LocationState = {
  from?: string
}

export function LoginScreen() {
  const { isAuthenticated, login } = useAuth()
  const location = useLocation()
  const [username, setUsername] = useState(demoCredentials.username)
  const [password, setPassword] = useState(demoCredentials.password)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (isAuthenticated) {
    const next = (location.state as LocationState | null)?.from ?? '/'
    return <Navigate to={next} replace />
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    setError('')
    setLoading(true)
    const result = await login(username, password)
    setLoading(false)
    if (!result.ok) {
      setError(result.error ?? 'Unable to sign in.')
    }
  }

  return (
    <main className="login-shell">
      <div className="login-frame">
        <div className="login-banner">
          <span className="env-badge">LOCAL SIM</span>
          <span className="login-clock">Cottage Operations Terminal</span>
        </div>

        <section className="login-panel">
          <div className="login-panel__header">
            <p className="eyebrow">Access</p>
            <h1>Cottage</h1>
            <p className="login-subtitle">
              Sign in to the local workstation shell for the digital twin runtime.
            </p>

            <div className="login-feature-list">
              <div className="login-feature">
                <ShieldCheck size={16} />
                <span>Protected shell routing</span>
              </div>
              <div className="login-feature">
                <LockKeyhole size={16} />
                <span>Demo credentials for local simulation</span>
              </div>
            </div>
          </div>

          <form className="login-form" onSubmit={handleSubmit}>
            <label className="field">
              <span>Username</span>
              <div className="field-input">
                <UserRound size={16} />
                <input value={username} onChange={(e) => setUsername(e.target.value)} />
              </div>
            </label>

            <label className="field">
              <span>Password</span>
              <div className="field-input">
                <LockKeyhole size={16} />
                <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
            </label>

            {error ? <div className="login-error">{error}</div> : null}

            <button className="primary-button" type="submit" disabled={loading}>
              {loading ? 'Authorizing…' : 'Enter Terminal'}
            </button>

            <div className="login-hint">
              <strong>Demo credentials</strong>
              <span>{demoCredentials.username} / {demoCredentials.password}</span>
            </div>
          </form>
        </section>
      </div>
    </main>
  )
}
