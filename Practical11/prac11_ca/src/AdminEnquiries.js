import { useEffect, useState } from 'react';

export default function AdminEnquiries() {
  const [enquiries, setEnquiries] = useState([]);

  useEffect(() => {
    if (localStorage.getItem('adminLoggedIn') !== 'true') {
      window.location.href = '/admin';
      return;
    }

    fetch('http://localhost:5000/api/enquiries')
      .then(res => res.json())
      .then(data => {
        console.log('ENQUIRIES RECEIVED:', data);
        setEnquiries(data);
      })
      .catch(err => {
        console.error('Fetch error:', err);
      });
  }, []);

  return (
    <div className="container">
      <h2>Client Enquiries</h2>

      {enquiries.length === 0 && <p>No enquiries found</p>}

      {enquiries.map(e => (
        <div key={e.id} className="card">
          <h3>{e.name}</h3>
          <p><b>Email:</b> {e.email}</p>
          <p>{e.message}</p>
        </div>
      ))}
    </div>
  );
}
