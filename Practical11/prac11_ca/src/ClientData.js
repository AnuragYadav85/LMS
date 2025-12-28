import { useEffect, useState } from 'react';

export default function ClientData() {
  const [clients, setClients] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/clients')
      .then(res => res.json())
      .then(setClients)
      .catch(() => setClients([]));
  }, []);

  return (
    <div className="container">
      <h2>Our Clients</h2>

      {clients.length === 0 && <p>No clients available</p>}

      {clients.map(client => (
        <div key={client.id} className="client-card">
          <img
            src={client.logo}
            alt={client.company_name}
            className="client-logo"
          />

          <div>
            <h3>{client.company_name}</h3>
            <p>{client.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
