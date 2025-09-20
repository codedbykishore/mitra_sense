"use client"
import { useEffect, useState } from "react"

interface User {
  name: string;
  email: string;
  picture: string;
  plan: string;
  onboarding_completed: boolean;
  role: string | null;
  profile: Record<string, string>;
}

export function useUser() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const res = await fetch("/me", {
          credentials: "include", // include session cookies
        })

        if (res.ok) {
          const data = await res.json()
          if (data.authenticated) {
            // construct the user object directly from the response
            setUser({
              name: data.name,
              email: data.email,
              picture: data.picture,
              plan: data.plan,
              onboarding_completed: data.onboarding_completed,
              role: data.role,
              profile: data.profile,
            })
          } else {
            // User is not authenticated, clear user state
            setUser(null)
          }
        } else {
          // Failed to fetch user, clear user state
          setUser(null)
        }
      } catch (err) {
        console.error("Error fetching user:", err)
        setUser(null)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  return { user, loading }
}
