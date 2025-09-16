"use client"
import { useEffect, useState } from "react"

export function useUser() {
  const [user, setUser] = useState(null)
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
