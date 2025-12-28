import { Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <div className="navbar">
      <Link to="/">Home</Link>
      <Link to="/enquire">Enquire</Link>
      <Link to="/clients">Clients</Link>
      <Link to="/careers">Careers</Link> {/* ✅ add this */}
      <Link to="/admin">Admin</Link>
    </div>
  );
}
