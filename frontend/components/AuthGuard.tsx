"use client";
import { useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

const PUBLIC_PATHS = ["/login", "/register"];

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const quizDone = localStorage.getItem("has_completed_quiz");

    if (!token && !PUBLIC_PATHS.includes(pathname)) {
      router.push("/login");
    } else if (token && quizDone === "false" && pathname !== "/quiz") {
      router.push("/quiz");
    }
  }, [pathname]);

  return <>{children}</>;
}
