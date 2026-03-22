import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

export type SessionUser = {
  username: string
  displayName: string
  role: string
}

type AuthContextValue = {
  user: SessionUser | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<{ ok: boolean; error?: string }>
  logout: () => void
}

const SESSION_KEY = 'cottage_terminal_session'
const DEMO_USERNAME = 'admin'
const DEMO_PASSWORD = 'demo123'

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem(SESSION_KEY)
    if (!stored) {
      setIsLoading(false)
      return
    }

    try {
      setUser(JSON.parse(stored) as SessionUser)
    } catch {
      localStorage.removeItem(SESSION_KEY)
    } finally {
      setIsLoading(false)
    }
  }, [])

  const value = useMemo<AuthContextValue>(() => ({
    user,
    isAuthenticated: user !== null,
    isLoading,
    async login(username: string, password: string) {
      await new Promise((resolve) => setTimeout(resolve, 450))

      if (username !== DEMO_USERNAME || password !== DEMO_PASSWORD) {
        return { ok: false, error: 'Use the demo credentials to enter the local simulation terminal.' }
      }

      const nextUser: SessionUser = {
        username,
        displayName: 'Operations Admin',
        role: 'admin',
      }

      localStorage.setItem(SESSION_KEY, JSON.stringify(nextUser))
      setUser(nextUser)
      return { ok: true }
    },
    logout() {
      localStorage.removeItem(SESSION_KEY)
      setUser(null)
    },
  }), [user, isLoading])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === null) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const demoCredentials = {
  username: DEMO_USERNAME,
  password: DEMO_PASSWORD,
}
