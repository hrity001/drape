import Link from "next/link";
export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t flex justify-around py-3 text-xs">
      <Link href="/">🔍 Discover</Link>
      <Link href="/stylist">🤖 Stylist</Link>
      <Link href="/submit">📝 Submit</Link>
    </nav>
  );
}

