
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Register() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const handleRegister = (e) => {
    e.preventDefault();

    if (!name || !email || !password || !confirmPassword) {
      alert("Please fill all fields");
      return;
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    const user = {
      name,
      email,
      password,
    };

    localStorage.setItem(
      "newsai_user",
      JSON.stringify(user)
    );

    alert("Registration successful!");

    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center px-4">

      <div className="w-full max-w-md bg-slate-900 p-8 rounded-2xl shadow-2xl border border-slate-800">

        <div className="text-center mb-8">

          <div className="text-5xl mb-3">
            📰
          </div>

          <h1 className="text-3xl font-bold text-white">
            Create Account
          </h1>

          <p className="text-slate-400 mt-2">
            Join NewsAI today
          </p>

        </div>

        <form onSubmit={handleRegister}>

          <label className="block text-slate-300 mb-2">
            Name
          </label>

          <input
            type="text"
            className="w-full p-3 rounded-lg mb-5 bg-slate-800 text-white border border-slate-700 focus:outline-none focus:border-cyan-400"
            placeholder="Enter your name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <label className="block text-slate-300 mb-2">
            Email
          </label>

          <input
            type="email"
            className="w-full p-3 rounded-lg mb-5 bg-slate-800 text-white border border-slate-700 focus:outline-none focus:border-cyan-400"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <label className="block text-slate-300 mb-2">
            Password
          </label>

          <input
            type="password"
            className="w-full p-3 rounded-lg mb-5 bg-slate-800 text-white border border-slate-700 focus:outline-none focus:border-cyan-400"
            placeholder="Create a password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label className="block text-slate-300 mb-2">
            Confirm Password
          </label>

          <input
            type="password"
            className="w-full p-3 rounded-lg mb-6 bg-slate-800 text-white border border-slate-700 focus:outline-none focus:border-cyan-400"
            placeholder="Confirm your password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
          />

          <button
            type="submit"
            className="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 p-3 rounded-lg font-semibold transition"
          >
            Create Account
          </button>

        </form>

        <p className="text-center text-slate-400 mt-6">
          Already have an account?{" "}

          <Link
            to="/login"
            className="text-cyan-400 hover:text-cyan-300 font-semibold"
          >
            Login
          </Link>

        </p>

      </div>

    </div>
  );
}

export default Register;

