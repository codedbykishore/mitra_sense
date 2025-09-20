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
        const res = await fetch("http://localhost:8000/me", {
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
          }
        }
      } catch (err) {
        console.error("Error fetching user:", err)
      } finally {
        setLoading(false)
      }
    }

    fetchUser()
  }, [])

  return { user, loading }
}
