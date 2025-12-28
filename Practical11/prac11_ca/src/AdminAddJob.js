import { useState } from 'react';

export default function AdminAddJob() {
  const [jobTitle, setJobTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = e => {
    e.preventDefault();
    fetch('http://localhost:5000/api/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        job_title: jobTitle,
        job_description: description,
        location
      })
    })
      .then(res => res.json())
      .then(() => {
        alert('Job Added Successfully');
        setJobTitle(''); setDescription(''); setLocation('');
      })
      .catch(err => console.error(err));
  };

  return (
    <div className="form-page">
      <div className="form-box">
        <h2>Add New Job</h2>
        <form onSubmit={handleSubmit}>
          <label>Job Title</label>
          <input type="text" value={jobTitle} onChange={e => setJobTitle(e.target.value)} required />

          <label>Job Description</label>
          <textarea value={description} onChange={e => setDescription(e.target.value)} required />

          <label>Location</label>
          <input type="text" value={location} onChange={e => setLocation(e.target.value)} required />

          <button type="submit">Add Job</button>
        </form>
      </div>
    </div>
  );
}
