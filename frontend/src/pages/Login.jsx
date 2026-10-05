
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function Login() {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = (e) => {
    e.preventDefault();

    if (!email || !password) {
      alert("Please enter email and password");
      return;
    }

    // Get registered user
    const savedUser = localStorage.getItem("newsai_user");

    if (!savedUser) {
      alert("No account found. Please register first.");
      return;
    }

    const user = JSON.parse(savedUser);

    // Check email and password
    if (
      user.email !== email ||
      user.password !== password
    ) {
      alert("Invalid email or password");
      return;
    }

    // Login successful
    login({
      name: user.name,
      email: user.email,
    });

    navigate("/news");
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-slate-900 p-8 rounded-2xl shadow-2xl">

        <div className="text-center mb-8">

          <div className="text-5xl mb-3">
            📰
          </div>

          <h1 className="text-3xl font-bold text-white">
            Welcome Back
          </h1>

          <p className="text-slate-400 mt-2">
            Login to NewsAI
          </p>

        </div>

        <form onSubmit={handleLogin}>

          <label className="block text-slate-300 mb-2">
            Email
          </label>

          <input
            type="email"
            className="w-full p-3 rounded-lg mb-5 bg-slate-800 text-white border border-slate-700"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label className="block text-slate-300 mb-2">
            Password
          </label>

          <input
            type="password"
            className="w-full p-3 rounded-lg mb-6 bg-slate-800 text-white border border-slate-700"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            type="submit"
            className="w-full bg-cyan-500 hover:bg-cyan-400 p-3 rounded-lg font-semibold"
          >
            Login
          </button>

        </form>

        <p className="text-center text-slate-400 mt-6">
          Don't have an account?{" "}

          <Link
            to="/register"
            className="text-cyan-400 hover:text-cyan-300 font-semibold"
          >
            Create Account
          </Link>
        </p>

      </div>

    </div>
  );
}

export default Login;

