import { useEffect, useState } from 'react';

export default function Careers() {
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/jobs')
      .then(res => res.json())
      .then(data => setJobs(data))
      .catch(err => console.error('Fetch jobs error:', err));
  }, []);

  const apply = async e => {
    e.preventDefault();
    const formData = new FormData(e.target);

    await fetch('http://localhost:5000/api/apply', {
      method: 'POST',
      body: formData
    });

    alert('Application submitted');
    e.target.reset();
  };

  return (
    <div className="container">
      <h2>Careers at CYBER IT</h2>

      <ul>
        {jobs.map(j => (
          <li key={j.id}>
            <b>{j.job_title}</b> – {j.job_description} ({j.location})
          </li>
        ))}
      </ul>

      <form onSubmit={apply} encType="multipart/form-data">
        <h3>Apply Now</h3>

        <input name="name" placeholder="Full Name" required />
        <input name="email" type="email" placeholder="Email" required />
        <input name="phone" placeholder="Phone" required />

        <label>Select Job</label>
        <select name="job_title" required>
          <option value="">Select Job</option>
          {jobs.map(j => (
            <option key={j.id} value={j.job_title}>
              {j.job_title} – {j.job_description} ({j.location})
            </option>
          ))}
        </select>

        <label>Passport Photo (jpg/png)</label>
        <input type="file" name="photo" accept="image/*" required />

        <label>Resume (PDF)</label>
        <input type="file" name="resume" accept="application/pdf" required />

        <button type="submit">Submit Application</button>
      </form>
    </div>
  );
}
