import { useEffect, useState } from 'react';

export default function AdminApplications() {
  const [apps, setApps] = useState([]);

  useEffect(() => {
    if (localStorage.getItem('adminLoggedIn') !== 'true') {
      window.location.href = '/admin';
      return;
    }

    fetch('http://localhost:5000/api/applications')
      .then(res => res.json())
      .then(setApps);
  }, []);

  const updateStatus = (id, status, email) => {
    fetch('http://localhost:5000/api/applications/status', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, status, email })
    })
      .then(res => res.json())
      .then(() => {
        // ✅ Update UI instantly
        setApps(prev =>
          prev.map(app =>
            app.id === id ? { ...app, status } : app
          )
        );
      });
  };

  return (
    <div className="container">
      <h2>Job Applications</h2>

      {apps.map(app => (
        <div key={app.id} className="card">
          <h3>{app.name}</h3>
          <p><b>Email:</b> {app.email}</p>
          <p><b>Phone:</b> {app.phone}</p>
          <p><b>Job:</b> {app.job_title}</p>
          <p>
            <b>Status:</b>{' '}
            <span
              style={{
                color:
                  app.status === 'Accepted'
                    ? 'limegreen'
                    : app.status === 'Rejected'
                    ? 'tomato'
                    : '#aaa',
                fontWeight: 'bold'
              }}
            >
              {app.status}
            </span>
          </p>

          <div className="admin-actions">
            <a
              href={`http://localhost:5000${app.resume_path}`}
              target="_blank"
              rel="noreferrer"
            >
              View CV
            </a>

            <button
              onClick={() =>
                updateStatus(app.id, 'Accepted', app.email)
              }
            >
              Accept
            </button>

            <button
              style={{ background: '#e11d48' }}
              onClick={() =>
                updateStatus(app.id, 'Rejected', app.email)
              }
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
