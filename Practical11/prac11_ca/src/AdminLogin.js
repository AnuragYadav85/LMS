export default function AdminLogin() {
  const login = async (e) => {
    e.preventDefault();

    const res = await fetch('http://localhost:5000/api/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: e.target.u.value,
        password: e.target.p.value
      })
    });

    const ok = await res.json();

    if (ok) {
      localStorage.setItem('adminLoggedIn', 'true');

      window.location = '/admin/dashboard';
    } else {
      alert('Invalid Login');
    }
  };

  return (
    <form onSubmit={login} className="login-form">
      <h2>Admin Login</h2>

      <input name="u" placeholder="Username" required />
      <input name="p" type="password" placeholder="Password" required />

      <button type="submit">Login</button>
    </form>
  );
}
