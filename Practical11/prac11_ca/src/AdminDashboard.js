import { Link } from 'react-router-dom';
export default function AdminDashboard() {

  if (localStorage.getItem('adminLoggedIn') !== 'true') {
    window.location.href = '/admin';
    return null;
  }

  return (
    <div className="container">
      <h2>Admin Dashboard</h2>

      <div className="admin-actions">
        <button onClick={() => window.location.href = '/admin/client'}>
          Add Client
        </button>

        <button onClick={() => window.location.href = '/clients'}>
          View Clients
        </button>

        <button onClick={() => window.location.href = '/admin/enquiries'}>
          View Client Enquiries
        </button>
      
        <button onClick={() => window.location.href = '/admin/applications'}>
          Show Job Applications
        </button>
      </div>

      <div className="admin-actions">
        <Link to="/admin/jobs/add" className="btn btn-primary">
          ➕ Add Available Job
        </Link>

        <Link to="/admin/applications" className="btn btn-outline">
          View Applications
        </Link>
      </div>

      <button
        style={{ marginTop: '30px' }}
        onClick={() => {
          localStorage.removeItem('adminLoggedIn');
          window.location.href = '/admin';
        }}
      >
        Logout
      </button>
    </div>
  );
}
