import { Link } from "react-router-dom";
function Navbar() {
  return (
    <nav className="sticky top-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">

      <div className="max-w-7xl mx-auto flex justify-between items-center px-8 py-4">

        <div className="flex items-center gap-3">

          <span className="text-3xl">📰</span>


          <h1 className="text-2xl font-bold text-cyan-400">
            NewsAI
          </h1>

        </div>

        <ul className="hidden md:flex gap-8 text-slate-300">

          <li className="hover:text-cyan-400 cursor-pointer transition">
            Home
          </li>

          <li className="hover:text-cyan-400 cursor-pointer transition">
            Categories
          </li>

          <li className="hover:text-cyan-400 cursor-pointer transition">
            Trending
          </li>

          <li className="hover:text-cyan-400 cursor-pointer transition">
            Dashboard
          </li>

          <li className="hover:text-cyan-400 cursor-pointer transition">
            About
          </li>

        </ul>

        <Link to="/login">
  <button className="bg-cyan-500 hover:bg-cyan-400 px-5 py-2 rounded-xl font-semibold transition">
    Login
  </button>
</Link>

      </div>

    </nav>
  );
}

export default Navbar;